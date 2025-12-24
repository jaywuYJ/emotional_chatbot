#!/usr/bin/env python3
"""
测试增强的删除功能
1. 只能删除最近的用户消息
2. 删除用户消息时同时删除对应的AI回复
"""
import requests
import json
import sys
import os
import time

def test_enhanced_delete():
    """测试增强的删除功能"""
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("测试增强的删除功能")
    print("=" * 60)
    
    # 创建测试会话
    session_id = f"enhanced_delete_test_{int(time.time())}"
    user_id = "enhanced_delete_test_user"
    
    print(f"会话ID: {session_id}")
    print(f"用户ID: {user_id}")
    
    # 1. 发送第一条消息
    print("\n1️⃣ 发送第一条消息...")
    try:
        response = requests.post(f"{base_url}/chat", json={
            "message": "第一条消息：今天天气怎么样？",
            "user_id": user_id,
            "session_id": session_id
        })
        
        if response.status_code != 200:
            print(f"❌ 发送第一条消息失败: {response.status_code}")
            print(f"错误: {response.text}")
            return
        
        result = response.json()
        first_message_id = result.get('message_id')
        print(f"✅ 第一条消息发送成功，ID: {first_message_id}")
        print(f"🤖 AI回复: {result.get('response', '')[:50]}...")
        
    except Exception as e:
        print(f"❌ 发送第一条消息异常: {e}")
        return
    
    # 2. 发送第二条消息
    print("\n2️⃣ 发送第二条消息...")
    try:
        response = requests.post(f"{base_url}/chat", json={
            "message": "第二条消息：那明天呢？",
            "user_id": user_id,
            "session_id": session_id
        })
        
        if response.status_code == 200:
            result = response.json()
            second_message_id = result.get('message_id')
            print(f"✅ 第二条消息发送成功，ID: {second_message_id}")
            print(f"🤖 AI回复: {result.get('response', '')[:50]}...")
        else:
            print(f"❌ 第二条消息发送失败: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 第二条消息发送异常: {e}")
        return
    
    # 3. 查看删除前的会话历史
    print("\n3️⃣ 删除前的会话历史...")
    try:
        response = requests.get(f"{base_url}/chat/sessions/{session_id}/history")
        if response.status_code == 200:
            history = response.json()
            messages_before = history.get('messages', [])
            print(f"✅ 会话历史获取成功，共 {len(messages_before)} 条消息")
            for i, msg in enumerate(messages_before):
                role_icon = "👤" if msg['role'] == 'user' else "🤖"
                print(f"  {i+1}. {role_icon} [{msg['role']}] {msg['content'][:30]}... (ID: {msg['id']})")
        else:
            print(f"❌ 会话历史获取失败: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 会话历史获取异常: {e}")
        return
    
    # 4. 尝试删除第一条消息（应该失败，因为不是最近的）
    print(f"\n4️⃣ 尝试删除第一条消息 (ID: {first_message_id})...")
    print("期望：失败，因为不是最近的用户消息")
    
    try:
        response = requests.delete(
            f"{base_url}/chat/messages/{first_message_id}",
            params={"user_id": user_id}
        )
        
        print(f"删除请求状态码: {response.status_code}")
        
        if response.status_code == 403:
            print("✅ 正确阻止了删除非最近消息")
            print(f"📝 错误信息: {response.json().get('detail', '')}")
        elif response.status_code == 200:
            print("❌ 意外成功删除了非最近消息")
        else:
            print(f"⚠️ 意外的状态码: {response.status_code}")
            print(f"响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 删除第一条消息异常: {e}")
    
    # 5. 删除最近的消息（第二条，应该成功）
    print(f"\n5️⃣ 删除最近的消息 (ID: {second_message_id})...")
    print("期望：成功删除用户消息和对应的AI回复")
    
    try:
        response = requests.delete(
            f"{base_url}/chat/messages/{second_message_id}",
            params={"user_id": user_id}
        )
        
        print(f"删除请求状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 删除成功")
            print(f"📝 结果: {result.get('message')}")
            print(f"🗑️ 删除的消息数量: {result.get('deleted_count', 1)}")
            print(f"🆔 删除的消息ID: {result.get('deleted_messages', [])}")
        else:
            print(f"❌ 删除失败: {response.status_code}")
            print(f"错误: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ 删除最近消息异常: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 6. 查看删除后的会话历史
    print("\n6️⃣ 删除后的会话历史...")
    try:
        response = requests.get(f"{base_url}/chat/sessions/{session_id}/history")
        if response.status_code == 200:
            history = response.json()
            messages_after = history.get('messages', [])
            print(f"✅ 删除后会话历史，共 {len(messages_after)} 条消息")
            for i, msg in enumerate(messages_after):
                role_icon = "👤" if msg['role'] == 'user' else "🤖"
                print(f"  {i+1}. {role_icon} [{msg['role']}] {msg['content'][:30]}... (ID: {msg['id']})")
        else:
            print(f"❌ 删除后会话历史获取失败: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 删除后会话历史获取异常: {e}")
        return
    
    # 7. 验证结果
    print(f"\n7️⃣ 验证结果...")
    
    deleted_count = len(messages_before) - len(messages_after)
    print(f"删除前消息数量: {len(messages_before)}")
    print(f"删除后消息数量: {len(messages_after)}")
    print(f"实际删除数量: {deleted_count}")
    
    # 检查是否删除了用户消息和AI回复（应该删除2条）
    if deleted_count == 2:
        print("✅ 成功删除了用户消息和对应的AI回复")
        
        # 检查剩余的消息是否正确
        remaining_user_messages = [msg for msg in messages_after if msg['role'] == 'user']
        remaining_ai_messages = [msg for msg in messages_after if msg['role'] == 'assistant']
        
        print(f"剩余用户消息: {len(remaining_user_messages)} 条")
        print(f"剩余AI消息: {len(remaining_ai_messages)} 条")
        
        if len(remaining_user_messages) == len(remaining_ai_messages):
            print("✅ 用户消息和AI消息数量匹配")
            print("🎉 测试通过！增强的删除功能正常工作")
        else:
            print("⚠️ 用户消息和AI消息数量不匹配")
            
    elif deleted_count == 1:
        print("❌ 只删除了1条消息，AI回复未被删除")
        print("💡 需要检查AI回复删除逻辑")
    else:
        print(f"⚠️ 删除了 {deleted_count} 条消息，与期望不符")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_enhanced_delete()