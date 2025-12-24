#!/usr/bin/env python3
"""
测试删除/撤回消息功能
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
USER_ID = "test_user_delete"

def test_delete_feature():
    print("=" * 60)
    print("测试删除/撤回消息功能")
    print("=" * 60)
    
    # 1. 创建新会话并发送消息
    print("\n1. 发送第一条消息...")
    response1 = requests.post(f"{BASE_URL}/chat", json={
        "message": "你好，这是第一条测试消息",
        "user_id": USER_ID
    })
    
    if response1.status_code != 200:
        print(f"❌ 发送消息失败: {response1.status_code}")
        print(response1.text)
        return
    
    data1 = response1.json()
    session_id = data1.get("session_id")
    message_id_1 = data1.get("message_id")
    ai_message_id_1 = data1.get("ai_message_id")
    
    print(f"✅ 消息发送成功")
    print(f"   Session ID: {session_id}")
    print(f"   User Message ID: {message_id_1}")
    print(f"   AI Message ID: {ai_message_id_1}")
    
    # 2. 发送第二条消息
    print("\n2. 发送第二条消息...")
    response2 = requests.post(f"{BASE_URL}/chat", json={
        "message": "这是第二条测试消息",
        "user_id": USER_ID,
        "session_id": session_id
    })
    
    if response2.status_code != 200:
        print(f"❌ 发送消息失败: {response2.status_code}")
        return
    
    data2 = response2.json()
    message_id_2 = data2.get("message_id")
    ai_message_id_2 = data2.get("ai_message_id")
    
    print(f"✅ 消息发送成功")
    print(f"   User Message ID: {message_id_2}")
    print(f"   AI Message ID: {ai_message_id_2}")
    
    # 3. 获取会话历史
    print("\n3. 获取会话历史...")
    response_history = requests.get(f"{BASE_URL}/chat/sessions/{session_id}/history")
    
    if response_history.status_code != 200:
        print(f"❌ 获取历史失败: {response_history.status_code}")
        return
    
    history = response_history.json()
    messages = history.get("messages", [])
    print(f"✅ 当前会话有 {len(messages)} 条消息")
    
    for i, msg in enumerate(messages, 1):
        print(f"   {i}. [{msg['role']}] ID:{msg['id']} - {msg['content'][:30]}...")
    
    # 4. 尝试删除第一条消息（应该失败，因为不是最近的）
    print(f"\n4. 尝试删除第一条用户消息 (ID: {message_id_1})...")
    print("   预期：失败（只能删除最近的一条用户消息）")
    
    response_delete_1 = requests.delete(
        f"{BASE_URL}/chat/messages/{message_id_1}",
        params={"user_id": USER_ID}
    )
    
    if response_delete_1.status_code == 403:
        print(f"✅ 符合预期：{response_delete_1.json().get('detail')}")
    else:
        print(f"⚠️  意外结果: {response_delete_1.status_code}")
        print(response_delete_1.text)
    
    # 5. 删除最近的一条用户消息（第二条，应该成功）
    print(f"\n5. 删除最近的用户消息 (ID: {message_id_2})...")
    print("   预期：成功，并删除其后的AI回复")
    
    response_delete_2 = requests.delete(
        f"{BASE_URL}/chat/messages/{message_id_2}",
        params={"user_id": USER_ID}
    )
    
    if response_delete_2.status_code == 200:
        delete_result = response_delete_2.json()
        print(f"✅ 删除成功")
        print(f"   删除的消息数: {delete_result.get('deleted_count')}")
        print(f"   删除的消息ID列表: {delete_result.get('deleted_messages')}")
    else:
        print(f"❌ 删除失败: {response_delete_2.status_code}")
        print(response_delete_2.text)
        return
    
    # 6. 再次获取会话历史，验证删除结果
    print("\n6. 验证删除结果...")
    response_history_after = requests.get(f"{BASE_URL}/chat/sessions/{session_id}/history")
    
    if response_history_after.status_code != 200:
        print(f"❌ 获取历史失败: {response_history_after.status_code}")
        return
    
    history_after = response_history_after.json()
    messages_after = history_after.get("messages", [])
    print(f"✅ 删除后会话有 {len(messages_after)} 条消息")
    
    for i, msg in enumerate(messages_after, 1):
        print(f"   {i}. [{msg['role']}] ID:{msg['id']} - {msg['content'][:30]}...")
    
    # 7. 尝试再次删除（现在第一条消息应该是最近的了）
    print(f"\n7. 再次尝试删除第一条用户消息 (ID: {message_id_1})...")
    print("   预期：成功（现在它是最近的用户消息了）")
    
    response_delete_3 = requests.delete(
        f"{BASE_URL}/chat/messages/{message_id_1}",
        params={"user_id": USER_ID}
    )
    
    if response_delete_3.status_code == 200:
        delete_result_3 = response_delete_3.json()
        print(f"✅ 删除成功")
        print(f"   删除的消息数: {delete_result_3.get('deleted_count')}")
        print(f"   删除的消息ID列表: {delete_result_3.get('deleted_messages')}")
    else:
        print(f"❌ 删除失败: {response_delete_3.status_code}")
        print(response_delete_3.text)
    
    # 8. 最终验证
    print("\n8. 最终验证...")
    response_history_final = requests.get(f"{BASE_URL}/chat/sessions/{session_id}/history")
    
    if response_history_final.status_code != 200:
        print(f"❌ 获取历史失败: {response_history_final.status_code}")
        return
    
    history_final = response_history_final.json()
    messages_final = history_final.get("messages", [])
    print(f"✅ 最终会话有 {len(messages_final)} 条消息")
    
    if len(messages_final) == 0:
        print("✅ 所有消息已成功删除")
    else:
        print("剩余消息:")
        for i, msg in enumerate(messages_final, 1):
            print(f"   {i}. [{msg['role']}] ID:{msg['id']} - {msg['content'][:30]}...")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_delete_feature()
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
