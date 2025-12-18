# 增强的删除功能

## 修复内容

### 1. 删除限制
- **只能删除最近的一条用户消息**
- 防止用户删除历史消息，保持对话的连贯性
- 前端只在最近的用户消息上显示"撤回"按钮
- 后端验证消息是否为该会话中最近的用户消息

### 2. 级联删除
- **删除用户消息时同时删除对应的AI回复**
- 避免出现孤立的AI回复
- 保持对话的逻辑完整性
- 删除相关的数据库记录（情感分析、反馈、评估等）

### 3. 权限验证
- **只能删除自己发送的消息**
- 不能删除AI消息
- 验证用户身份和消息所有权

## 技术实现

### 后端修改

#### 1. 路由层 (`backend/routers/chat.py`)
```python
# 添加了以下验证：
# 1. 检查是否为用户消息
if message.role != 'user':
    raise HTTPException(status_code=403, detail="只能删除自己发送的消息")

# 2. 检查是否为最近的用户消息
latest_user_message = db.db.query(ChatMessage).filter(
    ChatMessage.session_id == message.session_id,
    ChatMessage.user_id == user_id,
    ChatMessage.role == 'user'
).order_by(ChatMessage.created_at.desc()).first()

if not latest_user_message or latest_user_message.id != message.id:
    raise HTTPException(status_code=403, detail="只能撤回最近发送的一条消息")
```

#### 2. 数据库层 (`backend/database.py`)
```python
# 改进了AI回复查找逻辑：
if message.role == 'user':
    # 查找该用户消息之后的所有AI回复
    ai_responses = self.db.query(ChatMessage).filter(
        ChatMessage.session_id == message.session_id,
        ChatMessage.role == 'assistant',
        ChatMessage.created_at > message.created_at
    ).order_by(ChatMessage.created_at.asc()).all()
    
    if ai_responses:
        # 只删除紧接着的第一条AI回复
        first_ai_response = ai_responses[0]
        messages_to_delete.append(first_ai_response)
```

### 前端修改

#### 1. 按钮显示逻辑 (`frontend/src/components/ChatContainer.js`)
```javascript
// 只在最近的用户消息上显示撤回按钮
{message.role === 'user' && (() => {
  const userMessages = messages.filter(m => m.role === 'user');
  const latestUserMessage = userMessages[userMessages.length - 1];
  const isLatestUserMessage = latestUserMessage && latestUserMessage.id === message.id;
  
  return (
    <div>
      <button>编辑</button>
      {isLatestUserMessage && (
        <button onClick={() => handleDeleteMessage(message.id)}>
          撤回
        </button>
      )}
    </div>
  );
})()}
```

#### 2. 删除结果处理 (`frontend/src/App.js`)
```javascript
// 处理多条消息删除
const handleMessageDelete = useCallback((deleteInfo) => {
  const { deletedMessages } = deleteInfo;
  
  if (deletedMessages && deletedMessages.length > 0) {
    const newMessages = prevMessages.filter(msg => {
      const dbId = msg.dbId || msg.id;
      const shouldDelete = deletedMessages.includes(parseInt(dbId)) || 
                          deletedMessages.includes(dbId);
      return !shouldDelete;
    });
    return newMessages;
  }
}, []);
```

## 测试方法

### 1. 运行测试脚本
```bash
python test_enhanced_delete.py
```

### 2. 手动测试步骤
1. 发送多条消息
2. 尝试删除非最近的消息（应该失败）
3. 删除最近的用户消息（应该成功，同时删除AI回复）
4. 验证消息数量和对话完整性

### 3. 预期结果
- ✅ 只能删除最近的用户消息
- ✅ 删除用户消息时同时删除对应的AI回复
- ✅ 前端只在最近的用户消息上显示撤回按钮
- ✅ 保持对话的逻辑完整性

## 错误处理

### 1. 权限错误
- 状态码：403
- 消息："只能删除自己发送的消息"
- 消息："只能撤回最近发送的一条消息"

### 2. 消息不存在
- 状态码：404
- 消息："消息不存在或无权删除"

### 3. 服务器错误
- 状态码：500
- 详细错误信息和堆栈跟踪

## 用户体验改进

1. **视觉反馈**：只在可删除的消息上显示撤回按钮
2. **加载状态**：删除过程中显示加载动画
3. **错误提示**：友好的错误消息提示
4. **确认对话**：删除前需要用户确认
5. **即时更新**：删除后立即更新UI

## 数据一致性

1. **级联删除**：删除消息时同时删除相关数据
2. **事务处理**：确保删除操作的原子性
3. **错误回滚**：删除失败时回滚所有更改
4. **日志记录**：详细的删除操作日志

这个增强的删除功能提供了更好的用户体验和数据一致性，符合现代聊天应用的最佳实践。