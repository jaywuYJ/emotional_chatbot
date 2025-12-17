#!/usr/bin/env python3
"""
简单的编辑功能测试 - 验证前后端是否正常工作
"""
import requests
import json

def test_simple_edit():
    base_url = "http://localhost:8000"
    
    print("🧪 简单编辑功能测试")
    print("=" * 50)
    
    # 1. 创建一个新的测试会话
    session_id = f"simple_test_{int(__import__('time').time())}"
    user_id = "simple_test_user"
    
    print(f"📝 会话ID: {session_id}")
    print(f"👤 用户ID: {user_id}")
    
    # 2. 发送第一条消息
    print("\n1️⃣ 发送消息...")
    response = requests.post(f"{base_url}/chat", json={
        "message": "你好",
        "user_id": user_id,
        "session_id": session_id
    })
    
    if response.status_code != 200:
        print(f"❌ 发送消息失败: {response.status_code}")
        return
    
    result = response.json()
    message_id = result.get('message_id')
    print(f"✅ 消息发送成功，ID: {message_id}")
    print(f"🤖 AI回复: {result.get('response', '')[:50]}...")
    
    # 3. 立即编辑这条消息
    print(f"\n2️⃣ 编辑消息 {message_id}...")
    edit_response = requests.put(f"{base_url}/chat/messages/{message_id}", json={
        "user_id": user_id,
        "new_content": "你好，今天天气怎么样？"
    })
    
    if edit_response.status_code != 200:
        print(f"❌ 编辑失败: {edit_response.status_code}")
        print(f"错误: {edit_response.text}")
        return
    
    edit_result = edit_response.json()
    print(f"✅ 编辑成功")
    print(f"📝 新内容: {edit_result.get('content')}")
    
    if edit_result.get('new_response'):
        print(f"🤖 新AI回复: {edit_result['new_response'].get('content', '')[:50]}...")
        print(f"🗑️ 删除了 {edit_result.get('deleted_messages_count', 0)} 条消息")
    else:
        print("ℹ️ 没有生成新的AI回复")
    
    # 4. 检查会话历史
    print(f"\n3️⃣ 检查会话历史...")
    history_response = requests.get(f"{base_url}/chat/sessions/{session_id}/history")
    
    if history_response.status_code != 200:
        print(f"❌ 获取历史失败: {history_response.status_code}")
        return
    
    history = history_response.json()
    messages = history.get('messages', [])
    print(f"📚 会话历史 (共 {len(messages)} 条消息):")
    
    for i, msg in enumerate(messages):
        role_icon = "👤" if msg['role'] == 'user' else "🤖"
        print(f"  {i+1}. {role_icon} {msg['content'][:30]}...")
    
    # 5. 验证结果
    print(f"\n4️⃣ 验证结果...")
    
    # 应该有2条消息：编辑后的用户消息 + 新的AI回复
    if len(messages) == 2:
        user_msg = next((m for m in messages if m['role'] == 'user'), None)
        ai_msg = next((m for m in messages if m['role'] == 'assistant'), None)
        
        if user_msg and user_msg['content'] == "你好，今天天气怎么样？":
            print("✅ 用户消息编辑成功")
        else:
            print("❌ 用户消息编辑失败")
            
        if ai_msg:
            print("✅ AI回复生成成功")
        else:
            print("❌ AI回复生成失败")
            
        print("🎉 编辑功能测试通过！")
    else:
        print(f"❌ 消息数量不正确，期望2条，实际{len(messages)}条")
    
    print("\n" + "=" * 50)
    print("测试完成")

if __name__ == "__main__":
    test_simple_edit()