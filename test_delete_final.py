#!/usr/bin/env python3
"""
最终的删除功能测试
"""
import requests
import json
import time

def test_delete_final():
    """最终的删除功能测试"""
    base_url = "http://localhost:8000"
    
    print("🎯 最终删除功能测试")
    print("=" * 40)
    
    # 测试参数
    session_id = f"final_test_{int(time.time())}"
    user_id = "final_test_user"
    
    try:
        # 1. 发送消息
        print("1. 发送消息...")
        response = requests.post(f"{base_url}/chat", json={
            "message": "测试删除功能，这是一条用户消息",
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
        
        # 2. 查看历史（删除前）
        print("\n2. 删除前的历史...")
        response = requests.get(f"{base_url}/chat/sessions/{session_id}/history")
        if response.status_code == 200:
            history = response.json()
            messages_before = history.get('messages', [])
            print(f"删除前: {len(messages_before)} 条消息")
            for i, msg in enumerate(messages_before):
                role_icon = "👤" if msg['role'] == 'user' else "🤖"
                print(f"  {i+1}. {role_icon} [{msg['role']}] ID:{msg['id']} - {msg['content'][:30]}...")
        else:
            print(f"❌ 获取历史失败: {response.status_code}")
            return
        
        # 3. 删除用户消息
        print(f"\n3. 删除用户消息 {user_message_id}...")
        response = requests.delete(
            f"{base_url}/chat/messages/{user_message_id}",
            params={"user_id": user_id}
        )
        
        print(f"删除请求状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 删除成功")
            print(f"   消息: {result.get('message')}")
            print(f"   删除数量: {result.get('deleted_count')}")
            print(f"   删除的消息ID: {result.get('deleted_messages')}")
            
            # 验证删除的消息ID
            deleted_ids = result.get('deleted_messages', [])
            if user_message_id in deleted_ids:
                print(f"   ✅ 用户消息 {user_message_id} 已删除")
            if ai_message_id and ai_message_id in deleted_ids:
                print(f"   ✅ AI消息 {ai_message_id} 已删除")
            elif ai_message_id:
                print(f"   ❌ AI消息 {ai_message_id} 未删除")
                
        else:
            print(f"❌ 删除失败")
            try:
                error_detail = response.json().get('detail', response.text)
                print(f"   错误: {error_detail}")
            except:
                print(f"   错误: {response.text}")
            return
        
        # 4. 查看历史（删除后）
        print("\n4. 删除后的历史...")
        response = requests.get(f"{base_url}/chat/sessions/{session_id}/history")
        if response.status_code == 200:
            history = response.json()
            messages_after = history.get('messages', [])
            print(f"删除后: {len(messages_after)} 条消息")
            for i, msg in enumerate(messages_after):
                role_icon = "👤" if msg['role'] == 'user' else "🤖"
                print(f"  {i+1}. {role_icon} [{msg['role']}] ID:{msg['id']} - {msg['content'][:30]}...")
            
            # 5. 分析结果
            print(f"\n5. 结果分析:")
            deleted_count = len(messages_before) - len(messages_after)
            print(f"   删除前: {len(messages_before)} 条消息")
            print(f"   删除后: {len(messages_after)} 条消息")
            print(f"   实际删除: {deleted_count} 条消息")
            
            if deleted_count == 2:
                print("   ✅ 成功删除用户消息和AI回复")
                print("   🎉 删除功能测试通过！")
            elif deleted_count == 1:
                print("   ⚠️ 只删除了1条消息，AI回复可能未删除")
                print("   💡 需要检查AI消息的dbId设置")
            elif deleted_count == 0:
                print("   ❌ 没有删除任何消息")
                print("   💡 需要检查删除逻辑")
            else:
                print(f"   ❓ 删除了 {deleted_count} 条消息（意外结果）")
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_delete_final()