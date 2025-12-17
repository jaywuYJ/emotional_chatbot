#!/usr/bin/env python3
"""
消息撤回和编辑功能修复脚本
修复发现的问题并优化实现
"""

import os
import sys

def fix_database_manager():
    """修复数据库管理器中的问题"""
    print("修复数据库管理器...")
    
    # 读取当前文件
    with open('backend/database.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复update_message方法中的问题
    old_update_method = '''    def update_message(self, message_id, user_id, new_content, emotion=None, emotion_intensity=None):
        """更新消息内容"""
        message = self.get_message(message_id, user_id)
        if not message:
            return None
        
        message.content = new_content
        if emotion is not None:
            message.emotion = emotion
        if emotion_intensity is not None:
            message.emotion_intensity = emotion_intensity
        
        self.db.commit()
        self.db.refresh(message)
        return message'''
    
    new_update_method = '''    def update_message(self, message_id, user_id, new_content, emotion=None, emotion_intensity=None):
        """更新消息内容"""
        message = self.get_message(message_id, user_id)
        if not message:
            return None
        
        # 验证内容不为空（可选，根据业务需求）
        if not new_content or not new_content.strip():
            raise ValueError("消息内容不能为空")
        
        message.content = new_content.strip()
        if emotion is not None:
            message.emotion = emotion
        if emotion_intensity is not None:
            message.emotion_intensity = emotion_intensity
        
        # 更新修改时间（如果有该字段）
        from datetime import datetime
        if hasattr(message, 'updated_at'):
            message.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(message)
        return message'''
    
    if old_update_method in content:
        content = content.replace(old_update_method, new_update_method)
        print("✓ 修复update_message方法")
    
    # 修复delete_message方法，添加级联删除
    old_delete_method = '''    def delete_message(self, message_id, user_id):
        """删除（撤回）消息"""
        message = self.get_message(message_id, user_id)
        if not message:
            return False
        
        self.db.delete(message)
        self.db.commit()
        return True'''
    
    new_delete_method = '''    def delete_message(self, message_id, user_id):
        """删除（撤回）消息"""
        message = self.get_message(message_id, user_id)
        if not message:
            return False
        
        try:
            # 删除相关的情感分析记录
            self.db.query(EmotionAnalysis).filter(EmotionAnalysis.message_id == message_id).delete()
            
            # 删除相关的反馈记录
            self.db.query(UserFeedback).filter(UserFeedback.message_id == message_id).delete()
            
            # 删除相关的评估记录
            self.db.query(ResponseEvaluation).filter(ResponseEvaluation.message_id == message_id).delete()
            
            # 删除消息本身
            self.db.delete(message)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"删除消息失败: {e}")
            return False'''
    
    if old_delete_method in content:
        content = content.replace(old_delete_method, new_delete_method)
        print("✓ 修复delete_message方法，添加级联删除")
    
    # 写回文件
    with open('backend/database.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ 数据库管理器修复完成")

def fix_chat_router():
    """修复聊天路由中的问题"""
    print("修复聊天路由...")
    
    # 读取当前文件
    with open('backend/routers/chat.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复update_message路由，添加输入验证
    old_update_route = '''@router.put("/messages/{message_id}")
async def update_message(message_id: str, request: MessageUpdateRequest):
    """
    修改消息内容（消息编辑功能）
    """
    try:
        from backend.database import DatabaseManager
        
        with DatabaseManager() as db:
            # 尝试将message_id转换为整数，如果失败则保持字符串
                try:
                    message_id_int = int(message_id)
                except ValueError:
                    message_id_int = message_id
                    
                updated_message = db.update_message(
                    message_id=message_id_int,
                    user_id=request.user_id,
                    new_content=request.new_content,
                    emotion=request.emotion,
                    emotion_intensity=request.emotion_intensity
                )
            
            if not updated_message:
                raise HTTPException(status_code=404, detail="消息不存在或无权修改")
            
            return {
                "message": "消息修改成功",
                "message_id": updated_message.id,
                "content": updated_message.content,
                "updated_at": updated_message.created_at
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"修改消息错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))'''
    
    new_update_route = '''@router.put("/messages/{message_id}")
async def update_message(message_id: str, request: MessageUpdateRequest):
    """
    修改消息内容（消息编辑功能）
    """
    try:
        # 输入验证
        if not request.new_content or not request.new_content.strip():
            raise HTTPException(status_code=400, detail="消息内容不能为空")
        
        if len(request.new_content.strip()) > 2000:
            raise HTTPException(status_code=400, detail="消息内容过长，最多2000字符")
        
        from backend.database import DatabaseManager
        
        with DatabaseManager() as db:
            # 尝试将message_id转换为整数，如果失败则保持字符串
            try:
                message_id_int = int(message_id)
            except ValueError:
                message_id_int = message_id
                
            updated_message = db.update_message(
                message_id=message_id_int,
                user_id=request.user_id,
                new_content=request.new_content.strip(),
                emotion=request.emotion,
                emotion_intensity=request.emotion_intensity
            )
            
            if not updated_message:
                raise HTTPException(status_code=404, detail="消息不存在或无权修改")
            
            return {
                "message": "消息修改成功",
                "message_id": updated_message.id,
                "content": updated_message.content,
                "updated_at": updated_message.created_at.isoformat() if updated_message.created_at else None
            }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"修改消息错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))'''
    
    if old_update_route in content:
        content = content.replace(old_update_route, new_update_route)
        print("✓ 修复update_message路由，添加输入验证")
    
    # 写回文件
    with open('backend/routers/chat.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ 聊天路由修复完成")

def fix_frontend_chat_container():
    """修复前端ChatContainer组件"""
    print("修复前端ChatContainer组件...")
    
    # 读取当前文件
    with open('frontend/src/components/ChatContainer.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复编辑功能，添加更好的错误处理和用户体验
    old_edit_save = '''  // 保存编辑
  const handleEditSave = async (messageId) => {
    if (!editContent.trim()) return;
    
    try {
      const message = messages.find(m => m.id === messageId);
      if (!message) return;
      
      // 使用数据库ID而不是前端生成的ID
      const dbId = message.dbId || message.id;
      
      const result = await ChatAPI.updateMessage(dbId, {
        user_id: message.user_id,
        new_content: editContent
      });
      
      if (onMessageUpdate) {
        onMessageUpdate({
          id: messageId,
          content: editContent
        });
      }
      
      setEditingMessageId(null);
      setEditContent('');
    } catch (error) {
      console.error('编辑消息失败:', error);
      alert('编辑消息失败，请重试');
    }
  };'''
    
    new_edit_save = '''  // 保存编辑
  const handleEditSave = async (messageId) => {
    const trimmedContent = editContent.trim();
    
    // 输入验证
    if (!trimmedContent) {
      alert('消息内容不能为空');
      return;
    }
    
    if (trimmedContent.length > 2000) {
      alert('消息内容过长，最多2000字符');
      return;
    }
    
    try {
      const message = messages.find(m => m.id === messageId);
      if (!message) {
        alert('消息不存在');
        return;
      }
      
      // 使用数据库ID而不是前端生成的ID
      const dbId = message.dbId || message.id;
      
      const result = await ChatAPI.updateMessage(dbId, {
        user_id: message.user_id || 'anonymous',
        new_content: trimmedContent
      });
      
      if (onMessageUpdate) {
        onMessageUpdate({
          id: messageId,
          content: trimmedContent
        });
      }
      
      setEditingMessageId(null);
      setEditContent('');
    } catch (error) {
      console.error('编辑消息失败:', error);
      
      // 更友好的错误提示
      let errorMessage = '编辑消息失败，请重试';
      if (error.response?.status === 400) {
        errorMessage = error.response.data.detail || '输入内容无效';
      } else if (error.response?.status === 404) {
        errorMessage = '消息不存在或无权修改';
      } else if (error.response?.status === 500) {
        errorMessage = '服务器错误，请稍后重试';
      }
      
      alert(errorMessage);
    }
  };'''
    
    if old_edit_save in content:
        content = content.replace(old_edit_save, new_edit_save)
        print("✓ 修复编辑保存功能")
    
    # 修复撤回功能
    old_delete_message = '''  // 撤回消息
  const handleDeleteMessage = async (messageId) => {
    if (!window.confirm('确定要撤回这条消息吗？')) return;
    
    try {
      const message = messages.find(m => m.id === messageId);
      if (!message) return;
      
      // 使用数据库ID而不是前端生成的ID
      const dbId = message.dbId || message.id;
      
      const result = await ChatAPI.deleteMessage(dbId, message.user_id);
      
      if (onMessageDelete) {
        onMessageDelete(messageId);
      }
    } catch (error) {
      console.error('撤回消息失败:', error);
      alert('撤回消息失败，请重试');
    }
  };'''
    
    new_delete_message = '''  // 撤回消息
  const handleDeleteMessage = async (messageId) => {
    if (!window.confirm('确定要撤回这条消息吗？撤回后无法恢复。')) return;
    
    try {
      const message = messages.find(m => m.id === messageId);
      if (!message) {
        alert('消息不存在');
        return;
      }
      
      // 使用数据库ID而不是前端生成的ID
      const dbId = message.dbId || message.id;
      
      const result = await ChatAPI.deleteMessage(dbId, message.user_id || 'anonymous');
      
      if (onMessageDelete) {
        onMessageDelete(messageId);
      }
    } catch (error) {
      console.error('撤回消息失败:', error);
      
      // 更友好的错误提示
      let errorMessage = '撤回消息失败，请重试';
      if (error.response?.status === 404) {
        errorMessage = '消息不存在或无权撤回';
      } else if (error.response?.status === 500) {
        errorMessage = '服务器错误，请稍后重试';
      }
      
      alert(errorMessage);
    }
  };'''
    
    if old_delete_message in content:
        content = content.replace(old_delete_message, new_delete_message)
        print("✓ 修复撤回消息功能")
    
    # 写回文件
    with open('frontend/src/components/ChatContainer.js', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ 前端ChatContainer组件修复完成")

def add_message_id_mapping():
    """添加消息ID映射功能"""
    print("添加消息ID映射功能...")
    
    # 修复useChat hook中的消息ID处理
    with open('frontend/src/hooks/useChat.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 在sendMessage函数中添加ID映射
    old_send_message = '''      // 更新用户消息的ID为后端返回的真实ID
      setMessages(prev => prev.map(msg => 
        msg.id === newUserMessage.id 
          ? { ...msg, id: response.message_id } 
          : msg
      ));'''
    
    new_send_message = '''      // 更新用户消息的ID为后端返回的真实ID，同时保存数据库ID
      setMessages(prev => prev.map(msg => 
        msg.id === newUserMessage.id 
          ? { 
              ...msg, 
              id: response.message_id,
              dbId: response.message_id,  // 保存数据库ID用于编辑和撤回
              user_id: currentUserId      // 确保user_id存在
            } 
          : msg
      ));'''
    
    if old_send_message in content:
        content = content.replace(old_send_message, new_send_message)
        print("✓ 修复useChat中的消息ID映射")
    
    # 写回文件
    with open('frontend/src/hooks/useChat.js', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ 消息ID映射功能添加完成")

def add_database_indexes():
    """添加数据库索引优化性能"""
    print("添加数据库索引...")
    
    # 创建数据库索引脚本
    index_script = '''-- 消息编辑和撤回功能相关索引
-- 为提高查询性能而添加

-- 消息表索引
CREATE INDEX IF NOT EXISTS idx_chat_messages_user_id_created_at ON chat_messages(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_role ON chat_messages(session_id, role);

-- 情感分析表索引
CREATE INDEX IF NOT EXISTS idx_emotion_analysis_message_id ON emotion_analysis(message_id);

-- 用户反馈表索引
CREATE INDEX IF NOT EXISTS idx_user_feedback_message_id ON user_feedback(message_id);

-- 评估表索引
CREATE INDEX IF NOT EXISTS idx_response_evaluations_message_id ON response_evaluations(message_id);
'''
    
    with open('add_indexes.sql', 'w', encoding='utf-8') as f:
        f.write(index_script)
    
    print("✓ 数据库索引脚本已生成: add_indexes.sql")

def create_migration_script():
    """创建数据库迁移脚本"""
    print("创建数据库迁移脚本...")
    
    migration_script = '''#!/usr/bin/env python3
"""
消息编辑和撤回功能数据库迁移脚本
"""

from backend.database import DatabaseManager, ChatMessage
from sqlalchemy import text

def add_updated_at_column():
    """为消息表添加updated_at字段"""
    try:
        with DatabaseManager() as db:
            # 检查字段是否已存在
            result = db.db.execute(text("""
                SELECT COUNT(*) as count 
                FROM information_schema.columns 
                WHERE table_name = 'chat_messages' 
                AND column_name = 'updated_at'
            """)).fetchone()
            
            if result.count == 0:
                # 添加updated_at字段
                db.db.execute(text("""
                    ALTER TABLE chat_messages 
                    ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                """))
                db.db.commit()
                print("✓ 已添加updated_at字段到chat_messages表")
            else:
                print("✓ updated_at字段已存在")
                
    except Exception as e:
        print(f"添加updated_at字段失败: {e}")

def add_message_version_tracking():
    """添加消息版本跟踪表"""
    try:
        with DatabaseManager() as db:
            # 创建消息版本历史表
            db.db.execute(text("""
                CREATE TABLE IF NOT EXISTS message_edit_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    message_id INT NOT NULL,
                    user_id VARCHAR(100) NOT NULL,
                    old_content TEXT,
                    new_content TEXT,
                    edit_reason VARCHAR(200),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_message_edit_history_message_id (message_id),
                    INDEX idx_message_edit_history_user_id (user_id)
                )
            """))
            db.db.commit()
            print("✓ 已创建消息编辑历史表")
            
    except Exception as e:
        print(f"创建消息编辑历史表失败: {e}")

def run_migration():
    """运行迁移"""
    print("开始数据库迁移...")
    add_updated_at_column()
    add_message_version_tracking()
    print("数据库迁移完成")

if __name__ == "__main__":
    run_migration()
'''
    
    with open('migrate_message_features.py', 'w', encoding='utf-8') as f:
        f.write(migration_script)
    
    print("✓ 数据库迁移脚本已生成: migrate_message_features.py")

def main():
    """主修复函数"""
    print("开始修复消息撤回和编辑功能...")
    
    try:
        fix_database_manager()
        fix_chat_router()
        fix_frontend_chat_container()
        add_message_id_mapping()
        add_database_indexes()
        create_migration_script()
        
        print("\n✅ 所有修复完成！")
        print("\n后续步骤:")
        print("1. 运行数据库迁移: python migrate_message_features.py")
        print("2. 执行数据库索引: mysql < add_indexes.sql")
        print("3. 运行测试: python test_message_edit_recall.py")
        print("4. 重启前后端服务")
        
    except Exception as e:
        print(f"❌ 修复过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)