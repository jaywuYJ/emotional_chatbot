#!/usr/bin/env python3
"""
测试消息编辑功能
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from backend.services.chat_service import ChatService
from backend.models import ChatRequest, MessageUpdateRequest
from backend.database import DatabaseManager
import uuid

async def test_edit_functionality():
    """测试消息编辑和重新生成功能"""
    print("=" * 60)
    print("测试消息编辑功能")
    print("=" * 60)
    
    # 初始化服务
    chat_service = ChatService()
    
    # 创建测试会话
    session_id = str(uuid.uuid4())
    user_id = "test_user"
    
    print(f"会话ID: {session_id}")
    print(f"用户ID: {user_id}")
    
    # 1. 发送第一条消息
    print("\n1. 发送第一条消息...")
    request1 = ChatRequest(
        message="今天天气怎么样？",
        user_id=user_id,
        session_id=session_id
    )
    
    response1 = await chat_service.chat(request1)
    print(f"AI回复: {response1.response[:100]}...")
    print(f"消息ID: {response1.message_id}")
    
    # 2. 发送第二条消息
    print("\n2. 发送第二条消息...")
    request2 = ChatRequest(
        message="那明天呢？",
        user_id=user_id,
        session_id=session_id
    )
    
    response2 = await chat_service.chat(request2)
    print(f"AI回复: {response2.response[:100]}...")
    print(f"消息ID: {response2.message_id}")
    
    # 3. 查看当前会话历史
    print("\n3. 编辑前的会话历史:")
    history = await chat_service.get_session_history(session_id)
    for i, msg in enumerate(history['messages']):
        print(f"  {i+1}. [{msg['role']}] {msg['content'][:50]}...")
    
    # 4. 编辑第一条消息
    print("\n4. 编辑第一条消息...")
    
    # 获取第一条用户消息的ID
    user_messages = [msg for msg in history['messages'] if msg['role'] == 'user']
    if user_messages:
        first_message_id = user_messages[0]['id']
        print(f"编辑消息ID: {first_message_id}")
        
        # 模拟编辑请求
        edit_request = MessageUpdateRequest(
            new_content="今天北京的天气如何？",
            user_id=user_id,
            emotion="neutral",
            emotion_intensity=5.0
        )
        
        # 这里我们需要直接调用路由器的逻辑，因为我们在测试环境中
        # 实际应用中这会通过HTTP API调用
        from backend.routers.chat import update_message
        
        try:
            edit_result = await update_message(str(first_message_id), edit_request)
            print(f"编辑结果: {edit_result['message']}")
            if 'new_response' in edit_result:
                print(f"新的AI回复: {edit_result['new_response']['content'][:100]}...")
            print(f"删除的消息数量: {edit_result.get('deleted_messages_count', 0)}")
        except Exception as e:
            print(f"编辑失败: {e}")
            import traceback
            traceback.print_exc()
    
    # 5. 查看编辑后的会话历史
    print("\n5. 编辑后的会话历史:")
    history_after = await chat_service.get_session_history(session_id)
    for i, msg in enumerate(history_after['messages']):
        print(f"  {i+1}. [{msg['role']}] {msg['content'][:50]}...")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_edit_functionality())