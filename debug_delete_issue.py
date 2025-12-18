#!/usr/bin/env python3
"""
调试删除功能问题
"""
import requests
import json
import time
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from backend.database import DatabaseManager, ChatMessage

def debug_delete_issue():
    """调试删除功能问题"""
    base_url = "http://localhost:8000"
    
    print("🔍 调试删除功能问题")
    print("-" * 50)
    
    # 测试参数
    session_id = f"debug_delete_{int(time.time())}"
    user_id = "debug_user"
    
    try:
        # 1. 发送第一条消息
        print("1. 发送第一条消息...")
        response = requests.post(f"{base_url}/chat", json={
            "message": "第一条测试消息",
            "user_id": user_id,
            "session_id": session_id
        })
        
        if response.status_code == 200:
            result = response.json()
            first_message_id = result.get('message_id')
            print(f"✅ 第一条消息发送成功，ID: {first_message_id}")
        else:
            print(f"❌ 第一条消息发送失败: {response.status_code}")
            return
        
        # 2. 发送第二条消息
        print("\n2. 发送第二条消息...")
        response = requests.post(f"{base_url}/chat", json={
            "message": "第二条测试消息",
            "user_id": user_id,
            "session_id": session_id
        })
        
        if response.status_code == 200:
            result = response.json()
            second_message_id = result.get('message_id')
            print(f"✅ 第二条消息发送成功，ID: {second_message_id}")
        else:
            print(f"❌ 第二条消息发送失败: {response.status_code}")
            return
        
        # 3. 直接查询数据库检查消息结构
        print(f"\n3. 检查数据库中的消息结构...")
        with DatabaseManager() as db:
            messages = db.db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).order_by(ChatMessage.created_at.asc()).all()
            
            print(f"数据库中共有 {len(messages)} 条消息:")
            for i, msg in enumerate(messages):
                print(f"  {i+1}. ID: {msg.id}, 角色: {msg.role}, 时间: {msg.created_at}")
                print(f"     内容: {msg.content[:50]}...")
                print(f"     用户ID: {msg.user_id}")
                print()
        
        # 4. 模拟删除逻辑，查看AI回复查找过程
        print(f"4. 模拟删除第二条用户消息的逻辑...")
        with DatabaseManager() as db:
            # 获取第二条用户消息
            user_message = db.get_message(second_message_id, user_id)
            if user_message:
                print(f"找到用户消息: ID={user_message.id}, 时间={user_message.created_at}")
                
                # 查找AI回复
                ai_responses = db.db.query(ChatMessage).filter(
                    ChatMessage.session_id == user_message.session_id,
                    ChatMessage.role == 'assistant',
                    ChatMessage.created_at > user_message.created_at
                ).order_by(ChatMessage.created_at.asc()).all()
                
                print(f"找到 {len(ai_responses)} 条AI回复:")
                for ai_msg in ai_responses:
                    print(f"  - AI消息 ID: {ai_msg.id}, 时间: {ai_msg.created_at}")
                    print(f"    内容: {ai_msg.content[:50]}...")
                    print(f"    用户ID: {ai_msg.user_id}")
                
                if ai_responses:
                    first_ai = ai_responses[0]
                    print(f"\n将删除的AI回复: ID={first_ai.id}")
                else:
                    print("\n❌ 没有找到AI回复！")
                    
                    # 检查是否有任何AI消息
                    all_ai_messages = db.db.query(ChatMessage).filter(
                        ChatMessage.session_id == user_message.session_id,
                        ChatMessage.role == 'assistant'
                    ).all()
                    
                    print(f"会话中总共有 {len(all_ai_messages)} 条AI消息:")
                    for ai_msg in all_ai_messages:
                        print(f"  - AI消息 ID: {ai_msg.id}, 时间: {ai_msg.created_at}")
                        print(f"    与用户消息时间比较: {ai_msg.created_at} > {user_message.created_at} = {ai_msg.created_at > user_message.created_at}")
        
        # 5. 实际执行删除
        print(f"\n5. 实际执行删除...")
        response = requests.delete(
            f"{base_url}/chat/messages/{second_message_id}",
            params={"user_id": user_id}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 删除成功")
            print(f"   删除数量: {result.get('deleted_count')}")
            print(f"   删除ID: {result.get('deleted_messages')}")
        else:
            print(f"❌ 删除失败: {response.status_code}")
            print(f"   错误: {response.json().get('detail', response.text)}")
        
        # 6. 检查删除后的数据库状态
        print(f"\n6. 检查删除后的数据库状态...")
        with DatabaseManager() as db:
            remaining_messages = db.db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).order_by(ChatMessage.created_at.asc()).all()
            
            print(f"删除后剩余 {len(remaining_messages)} 条消息:")
            for i, msg in enumerate(remaining_messages):
                print(f"  {i+1}. ID: {msg.id}, 角色: {msg.role}, 时间: {msg.created_at}")
                print(f"     内容: {msg.content[:50]}...")
        
    except Exception as e:
        print(f"❌ 调试过程异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_delete_issue()