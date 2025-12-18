#!/usr/bin/env python3
"""
简单的API删除测试
"""
import requests
import json
import time

def test_delete_simple_api():
    """简单的API删除测试"""
    base_url = "http://localhost:8000"
    
    print("🧪 简单的API删除测试")
    print("-" * 30)
    
    # 测试参数
    session_id = f"simple_api_test_{int(time.time())}"
    user_id = "simple_api_user"
    
    try:
        # 1. 发送消息
        print("1. 发送消息...")
        response = requests.post(f"{base_url}/chat", json={
            "message": "测试删除API",
            "user_id": user_id,
            "session_id": session_id
        })
        
        if response.status_code == 200:
            result = response.json()
            user_message_id = result.get('message_id')
            ai_message_id = result.get('ai_message_id')
            print(f"✅ 消息发送成功")
            print(f"   用户消息ID: {user_message_id}")
            print(f"   AI消息ID: {ai_message_id}")
            print(f"   AI回复: {result.get('response', '')[:50]}...")
        else:
            print(f"❌ 消息发送失败: {response.status_code}")
            print(f"错误: {response.text}")
            return
        
        # 2. 查看历史
        print("\n2. 查看历史...")
        response = requests.get(f"{base_url}/chat/sessions/{session_id}/history")
        if response.status_code == 200:
            history = response.json()
            messages_before = history.get('messages', [])
            print(f"删除前: {len(messages_before)} 条消息")
            for msg in messages_before:
                print(f"  - {msg['role']} (ID: {msg['id']}): {msg['content'][:30]}...")
        else:
            print(f"❌ 获取历史失败: {response.status_code}")
        
        # 3. 删除消息
        print(f"\n3. 删除用户消息 {user_message_id}...")
        response = requests.delete(
            f"{base_url}/chat/messages/{user_message_id}",
            params={"user_id": user_id}
        )
        
        print(f"删除请求状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 删除响应成功")
            print(f"   消息: {result.get('message')}")
            print(f"   删除数量: {result.get('deleted_count')}")
            print(f"   删除的消息ID: {result.get('deleted_messages')}")
        else:
            print(f"❌ 删除失败")
            try:
                error_detail = response.json().get('detail', response.text)
                print(f"   错误: {error_detail}")
            except:
                print(f"   错误: {response.text}")
        
        # 4. 再次查看历史
        print("\n4. 删除后的历史...")
        response = requests.get(f"{base_url}/chat/sessions/{session_id}/history")
        if response.status_code == 200:
            history = response.json()
            messages_after = history.get('messages', [])
            print(f"删除后: {len(messages_after)} 条消息")
            for msg in messages_after:
                print(f"  - {msg['role']} (ID: {msg['id']}): {msg['content'][:30]}...")
            
            # 分析结果
            deleted_count = len(messages_before) - len(messages_after)
            print(f"\n📊 结果:")
            print(f"   删除前: {len(messages_before)} 条")
            print(f"   删除后: {len(messages_after)} 条")
            print(f"   实际删除: {deleted_count} 条")
            
            if deleted_count == 2:
                print("   ✅ 成功删除用户消息和AI回复")
            elif deleted_count == 1:
                print("   ⚠️ 只删除了1条消息")
            else:
                print(f"   ❓ 删除了 {deleted_count} 条消息")
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_delete_simple_api()