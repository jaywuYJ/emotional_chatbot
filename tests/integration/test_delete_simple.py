#!/usr/bin/env python3
"""
简化的删除功能测试
"""
import requests
import json
import time

def test_delete_simple():
    """简化的删除功能测试"""
    base_url = "http://localhost:8000"
    
    print("🧪 测试删除功能")
    print("-" * 40)
    
    # 测试参数
    session_id = f"test_{int(time.time())}"
    user_id = "test_user"
    
    try:
        # 1. 发送消息
        print("1. 发送消息...")
        response = requests.post(f"{base_url}/chat", json={
            "message": "测试消息",
            "user_id": user_id,
            "session_id": session_id
        })
        
        if response.status_code == 200:
            result = response.json()
            message_id = result.get('message_id')
            print(f"✅ 消息发送成功，ID: {message_id}")
        else:
            print(f"❌ 消息发送失败: {response.status_code}")
            return
        
        # 2. 查看历史
        print("\n2. 查看历史...")
        response = requests.get(f"{base_url}/chat/sessions/{session_id}/history")
        if response.status_code == 200:
            history = response.json()
            messages = history.get('messages', [])
            print(f"✅ 历史消息: {len(messages)} 条")
            for msg in messages:
                print(f"   - {msg['role']}: {msg['content'][:30]}... (ID: {msg['id']})")
        
        # 3. 删除消息
        print(f"\n3. 删除消息 {message_id}...")
        response = requests.delete(
            f"{base_url}/chat/messages/{message_id}",
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
        
        # 4. 再次查看历史
        print("\n4. 删除后历史...")
        response = requests.get(f"{base_url}/chat/sessions/{session_id}/history")
        if response.status_code == 200:
            history = response.json()
            messages = history.get('messages', [])
            print(f"✅ 剩余消息: {len(messages)} 条")
            for msg in messages:
                print(f"   - {msg['role']}: {msg['content'][:30]}... (ID: {msg['id']})")
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")

if __name__ == "__main__":
    test_delete_simple()