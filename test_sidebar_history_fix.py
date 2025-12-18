#!/usr/bin/env python3
"""
测试侧边栏历史记录修复
"""
import requests
import json
import time

def test_sidebar_history_fix():
    """测试侧边栏历史记录修复"""
    base_url = "http://localhost:8000"
    
    print("🔧 测试侧边栏历史记录修复")
    print("=" * 50)
    
    # 测试参数
    session_id = f"sidebar_test_{int(time.time())}"
    user_id = "sidebar_test_user"
    
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
            first_user_id = result.get('message_id')
            first_ai_id = result.get('ai_message_id')
            print(f"✅ 第一条消息发送成功")
            print(f"   用户消息ID: {first_user_id}")
            print(f"   AI消息ID: {first_ai_id}")
        else:
            print(f"❌ 第一条消息发送失败: {response.status_code}")
            return
        
        # 2. 检查历史会话列表
        print("\n2. 检查发送消息后的历史会话...")
        response = requests.get(f"{base_url}/users/{user_id}/sessions")
        if response.status_code == 200:
            sessions = response.json().get('sessions', [])
            print(f"历史会话数量: {len(sessions)}")
            for i, session in enumerate(sessions):
                if session['session_id'] == session_id:
                    print(f"  找到当前会话: {session['title']}")
                    print(f"  消息数量: {session['message_count']}")
                    break
        
        # 3. 发送第二条消息
        print("\n3. 发送第二条消息...")
        response = requests.post(f"{base_url}/chat", json={
            "message": "第二条测试消息",
            "user_id": user_id,
            "session_id": session_id
        })
        
        if response.status_code == 200:
            result = response.json()
            second_user_id = result.get('message_id')
            second_ai_id = result.get('ai_message_id')
            print(f"✅ 第二条消息发送成功")
            print(f"   用户消息ID: {second_user_id}")
            print(f"   AI消息ID: {second_ai_id}")
        else:
            print(f"❌ 第二条消息发送失败: {response.status_code}")
            return
        
        # 4. 再次检查历史会话列表
        print("\n4. 检查发送第二条消息后的历史会话...")
        response = requests.get(f"{base_url}/users/{user_id}/sessions")
        if response.status_code == 200:
            sessions = response.json().get('sessions', [])
            print(f"历史会话数量: {len(sessions)}")
            current_session_count = 0
            for session in sessions:
                if session['session_id'] == session_id:
                    current_session_count += 1
                    print(f"  会话: {session['title']}")
                    print(f"  消息数量: {session['message_count']}")
            
            if current_session_count == 1:
                print("✅ 正确：同一会话只有一条历史记录")
            else:
                print(f"❌ 错误：同一会话有 {current_session_count} 条历史记录")
        
        # 5. 删除最近的用户消息
        print(f"\n5. 删除最近的用户消息 {second_user_id}...")
        response = requests.delete(
            f"{base_url}/chat/messages/{second_user_id}",
            params={"user_id": user_id}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 删除成功")
            print(f"   删除数量: {result.get('deleted_count')}")
            print(f"   删除的消息ID: {result.get('deleted_messages')}")
        else:
            print(f"❌ 删除失败: {response.status_code}")
            return
        
        # 6. 检查删除后的历史会话
        print("\n6. 检查删除消息后的历史会话...")
        response = requests.get(f"{base_url}/users/{user_id}/sessions")
        if response.status_code == 200:
            sessions = response.json().get('sessions', [])
            print(f"历史会话数量: {len(sessions)}")
            
            current_session_found = False
            for session in sessions:
                if session['session_id'] == session_id:
                    current_session_found = True
                    print(f"  会话: {session['title']}")
                    print(f"  消息数量: {session['message_count']}")
                    print(f"  预览: {session['preview']}")
            
            if current_session_found:
                print("✅ 会话仍然存在（因为还有第一条消息）")
            else:
                print("❌ 会话消失了（可能是bug）")
        
        # 7. 检查当前会话的消息
        print("\n7. 检查当前会话的消息...")
        response = requests.get(f"{base_url}/chat/sessions/{session_id}/history")
        if response.status_code == 200:
            history = response.json()
            messages = history.get('messages', [])
            print(f"当前会话消息数量: {len(messages)}")
            for msg in messages:
                print(f"  - {msg['role']} (ID: {msg['id']}): {msg['content'][:30]}...")
        
        # 8. 删除剩余的消息（清空会话）
        print(f"\n8. 删除剩余的用户消息 {first_user_id}...")
        response = requests.delete(
            f"{base_url}/chat/messages/{first_user_id}",
            params={"user_id": user_id}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 删除成功")
            print(f"   删除数量: {result.get('deleted_count')}")
        
        # 9. 检查清空后的历史会话
        print("\n9. 检查清空会话后的历史会话...")
        response = requests.get(f"{base_url}/users/{user_id}/sessions")
        if response.status_code == 200:
            sessions = response.json().get('sessions', [])
            print(f"历史会话数量: {len(sessions)}")
            
            current_session_found = False
            for session in sessions:
                if session['session_id'] == session_id:
                    current_session_found = True
                    print(f"  ❌ 空会话仍然存在: {session['title']}")
            
            if not current_session_found:
                print("✅ 空会话已从历史记录中移除")
        
        print("\n" + "=" * 50)
        print("测试完成")
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sidebar_history_fix()