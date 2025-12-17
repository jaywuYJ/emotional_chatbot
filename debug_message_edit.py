#!/usr/bin/env python3
"""
调试消息编辑功能
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"
TEST_USER_ID = "debug_user"

def debug_message_edit():
    print("🔍 开始调试消息编辑功能...")
    
    # 1. 发送一条测试消息
    print("\n1. 发送测试消息...")
    chat_data = {
        "message": "这是一条用于调试的测试消息",
        "user_id": TEST_USER_ID,
        "session_id": None
    }
    
    response = requests.post(f"{API_BASE_URL}/chat", json=chat_data)
    print(f"发送消息状态码: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ 发送消息失败: {response.text}")
        return
    
    result = response.json()
    session_id = result["session_id"]
    api_message_id = result["message_id"]
    
    print(f"✓ 消息发送成功")
    print(f"  Session ID: {session_id}")
    print(f"  API返回的Message ID: {api_message_id}")
    
    # 2. 获取会话历史，查看实际的数据库ID
    print("\n2. 获取会话历史...")
    history_response = requests.get(f"{API_BASE_URL}/chat/sessions/{session_id}/history")
    print(f"获取历史状态码: {history_response.status_code}")
    
    if history_response.status_code != 200:
        print(f"❌ 获取历史失败: {history_response.text}")
        return
    
    history = history_response.json()
    print(f"✓ 历史获取成功，消息数量: {len(history['messages'])}")
    
    # 找到用户消息
    user_messages = [msg for msg in history["messages"] if msg["role"] == "user"]
    if not user_messages:
        print("❌ 没有找到用户消息")
        return
    
    user_message = user_messages[0]
    db_message_id = user_message["id"]
    message_user_id = user_message.get("user_id", "未知")
    
    print(f"✓ 找到用户消息:")
    print(f"  数据库Message ID: {db_message_id}")
    print(f"  消息User ID: {message_user_id}")
    print(f"  消息内容: {user_message['content']}")
    print(f"  完整消息对象: {json.dumps(user_message, indent=2, ensure_ascii=False)}")
    
    # 3. 尝试使用API返回的ID编辑消息
    print(f"\n3. 使用API返回的ID ({api_message_id}) 编辑消息...")
    edit_data = {
        "user_id": TEST_USER_ID,
        "new_content": "使用API ID编辑的内容"
    }
    
    response = requests.put(f"{API_BASE_URL}/chat/messages/{api_message_id}", json=edit_data)
    print(f"编辑状态码: {response.status_code}")
    print(f"编辑响应: {response.text}")
    
    # 4. 尝试使用数据库ID编辑消息
    print(f"\n4. 使用数据库ID ({db_message_id}) 编辑消息...")
    edit_data = {
        "user_id": TEST_USER_ID,
        "new_content": "使用数据库ID编辑的内容"
    }
    
    response = requests.put(f"{API_BASE_URL}/chat/messages/{db_message_id}", json=edit_data)
    print(f"编辑状态码: {response.status_code}")
    print(f"编辑响应: {response.text}")
    
    if response.status_code == 200:
        print("✅ 使用数据库ID编辑成功！")
        
        # 5. 验证编辑结果
        print("\n5. 验证编辑结果...")
        history_response = requests.get(f"{API_BASE_URL}/chat/sessions/{session_id}/history")
        if history_response.status_code == 200:
            history = history_response.json()
            user_messages = [msg for msg in history["messages"] if msg["role"] == "user"]
            if user_messages:
                updated_content = user_messages[0]["content"]
                print(f"✓ 消息已更新为: {updated_content}")
            else:
                print("❌ 找不到更新后的消息")
        else:
            print("❌ 无法获取更新后的历史")
    else:
        print("❌ 使用数据库ID编辑也失败了")
    
    # 6. 测试权限验证
    print(f"\n6. 测试权限验证（使用错误的user_id）...")
    edit_data = {
        "user_id": "wrong_user",
        "new_content": "恶意编辑尝试"
    }
    
    response = requests.put(f"{API_BASE_URL}/chat/messages/{db_message_id}", json=edit_data)
    print(f"权限测试状态码: {response.status_code}")
    print(f"权限测试响应: {response.text}")
    
    if response.status_code == 404:
        print("✅ 权限验证正常工作")
    else:
        print("❌ 权限验证可能有问题")

if __name__ == "__main__":
    debug_message_edit()