#!/usr/bin/env python3
"""
简单的撤回功能测试
"""
import requests
import json

def test_simple_delete():
    base_url = "http://localhost:8000"
    
    print("🧪 简单撤回功能测试")
    print("=" * 50)
    
    # 1. 创建一个新的测试会话
    session_id = f"delete_simple_{int(__import__('time').time())}"
    user_id = "delete_simple_user"
    
    print(f"📝 会话ID: {session_id}")
    print(f"👤 用户ID: {user_id}")
    
    # 2. 发送一条消息
    print("\n1️⃣ 发送消息...")
    response = requests.post(f"{base_url}/chat", json={
        "message": "这是一条要被删除的测试消息",
        "user_id": user_id,
        "session_id": session_id
    })
    
    if response.status_code != 200:
        print(f"❌ 发送消息失败: {response.status_code}")
        print(f"错误: {response.text}")
        return
    
    result = response.json()
    message_id = result.get('message_id')
    print(f"✅ 消息发送成功，ID: {message_id}")
    print(f"🤖 AI回复: {result.get('response', '')[:50]}...")
    
    # 3. 立即删除这条消息
    print(f"\n2️⃣ 删除消息 {message_id}...")
    
    # 测试正确的参数格式
    delete_url = f"{base_url}/chat/messages/{message_id}"
    params = {"user_id": user_id}
    
    print(f"删除URL: {delete_url}")
    print(f"参数: {params}")
    
    delete_response = requests.delete(delete_url, params=params)
    
    print(f"删除响应状态码: {delete_response.status_code}")
    print(f"删除响应内容: {delete_response.text}")
    
    if delete_response.status_code == 200:
        delete_result = delete_response.json()
        print(f"✅ 删除成功")
        print(f"📝 结果: {delete_result.get('message')}")
    else:
        print(f"❌ 删除失败: {delete_response.status_code}")
        try:
            error_detail = delete_response.json()
            print(f"错误详情: {error_detail}")
        except:
            print(f"错误文本: {delete_response.text}")
        return
    
    # 4. 检查会话历史
    print(f"\n3️⃣ 检查删除后的会话历史...")
    history_response = requests.get(f"{base_url}/chat/sessions/{session_id}/history")
    
    if history_response.status_code != 200:
        print(f"❌ 获取历史失败: {history_response.status_code}")
        return
    
    history = history_response.json()
    messages = history.get('messages', [])
    print(f"📚 会话历史 (共 {len(messages)} 条消息):")
    
    for i, msg in enumerate(messages):
        role_icon = "👤" if msg['role'] == 'user' else "🤖"
        print(f"  {i+1}. {role_icon} {msg['content'][:30]}... (ID: {msg['id']})")
    
    # 5. 验证结果
    print(f"\n4️⃣ 验证结果...")
    
    # 检查被删除的消息是否还在历史中
    deleted_message_found = any(msg['id'] == message_id for msg in messages)
    
    if not deleted_message_found:
        print("✅ 消息已成功从历史中删除")
        print("🎉 撤回功能测试通过！")
    else:
        print("❌ 消息仍然存在于历史中")
        print("💡 可能是数据库删除失败或历史查询有问题")
    
    print("\n" + "=" * 50)
    print("测试完成")

if __name__ == "__main__":
    test_simple_delete()