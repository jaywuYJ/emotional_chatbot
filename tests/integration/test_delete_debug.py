#!/usr/bin/env python3
"""
调试删除功能的简单测试
"""
import requests
import json
import time

def test_delete_debug():
    """调试删除功能"""
    base_url = "http://localhost:8000"
    
    print("🔍 调试删除功能")
    print("-" * 30)
    
    # 测试参数
    session_id = f"debug_{int(time.time())}"
    user_id = "debug_user"
    
    try:
        # 1. 发送消息
        print("1. 发送消息...")
        response = requests.post(f"{base_url}/chat", json={
            "message": "测试删除功能",
            "user_id": user_id,
            "session_id": session_id
        })
        
        if response.status_code == 200:
            result = response.json()
            message_id = result.get('message_id')
            print(f"✅ 消息发送成功，ID: {message_id}")
            print(f"🤖 AI回复: {result.get('response', '')[:50]}...")
        else:
            print(f"❌ 消息发送失败: {response.status_code}")
            print(f"错误: {response.text}")
            return
        
        # 2. 查看历史（删除前）
        print("\n2. 删除前的历史...")
        response = requests.get(f"{base_url}/chat/sessions/{session_id}/history")
        if response.status_code == 200:
            history = response.json()
            messages_before = history.get('messages', [])
            print(f"删除前: {len(messages_before)} 条消息")
            for msg in messages_before:
                print(f"  - {msg['role']}: {msg['content'][:30]}... (ID: {msg['id']})")
        
        # 3. 删除消息
        print(f"\n3. 删除消息 {message_id}...")
        response = requests.delete(
            f"{base_url}/chat/messages/{message_id}",
            params={"user_id": user_id}
        )
        
        print(f"删除请求状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 删除成功")
            print(f"   消息: {result.get('message')}")
            print(f"   删除数量: {result.get('deleted_count')}")
            print(f"   删除ID: {result.get('deleted_messages')}")
        else:
            print(f"❌ 删除失败")
            try:
                error_detail = response.json().get('detail', response.text)
                print(f"   错误: {error_detail}")
            except:
                print(f"   错误: {response.text}")
        
        # 4. 查看历史（删除后）
        print("\n4. 删除后的历史...")
        response = requests.get(f"{base_url}/chat/sessions/{session_id}/history")
        if response.status_code == 200:
            history = response.json()
            messages_after = history.get('messages', [])
            print(f"删除后: {len(messages_after)} 条消息")
            for msg in messages_after:
                print(f"  - {msg['role']}: {msg['content'][:30]}... (ID: {msg['id']})")
            
            # 分析结果
            deleted_count = len(messages_before) - len(messages_after)
            print(f"\n📊 结果分析:")
            print(f"   删除前: {len(messages_before)} 条")
            print(f"   删除后: {len(messages_after)} 条")
            print(f"   实际删除: {deleted_count} 条")
            
            if deleted_count == 2:
                print("✅ 成功删除用户消息和AI回复")
            elif deleted_count == 1:
                print("⚠️ 只删除了用户消息，AI回复未删除")
            else:
                print(f"❓ 删除了 {deleted_count} 条消息")
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_delete_debug()