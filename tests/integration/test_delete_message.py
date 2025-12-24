#!/usr/bin/env python3
"""
测试消息撤回功能
"""
import requests
import json
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_delete_message():
    """测试消息撤回功能"""
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("测试消息撤回功能")
    print("=" * 60)
    
    # 创建测试会话
    session_id = f"delete_test_{int(__import__('time').time())}"
    user_id = "delete_test_user"
    
    print(f"会话ID: {session_id}")
    print(f"用户ID: {user_id}")
    
    # 1. 发送第一条消息
    print("\n1. 发送第一条消息...")
    try:
        response = requests.post(f"{base_url}/chat", json={
            "message": "这是一条测试消息",
            "user_id": user_id,
            "session_id": session_id
        })
        
        if response.status_code != 200:
            print(f"❌ 发送消息失败: {response.status_code} - {response.text}")
            return
        
        result = response.json()
        message_id = result.get('message_id')
        print(f"✅ 消息发送成功，ID: {message_id}")
        print(f"AI回复: {result.get('response', '')[:50]}...")
        
    except Exception as e:
        print(f"❌ 发送消息异常: {e}")
        return
    
    # 2. 发送第二条消息
    print("\n2. 发送第二条消息...")
    try:
        response = requests.post(f"{base_url}/chat", json={
            "message": "这是第二条测试消息",
            "user_id": user_id,
            "session_id": session_id
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 第二条消息发送成功")
        else:
            print(f"❌ 第二条消息发送失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 第二条消息发送异常: {e}")
    
    # 3. 查看删除前的会话历史
    print("\n3. 删除前的会话历史...")
    try:
        response = requests.get(f"{base_url}/chat/sessions/{session_id}/history")
        if response.status_code == 200:
            history = response.json()
            print(f"✅ 会话历史获取成功，共 {len(history.get('messages', []))} 条消息")
            for i, msg in enumerate(history.get('messages', [])):
                print(f"  {i+1}. [{msg['role']}] {msg['content'][:30]}... (ID: {msg['id']})")
        else:
            print(f"❌ 会话历史获取失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 会话历史获取异常: {e}")
    
    # 4. 测试撤回第一条消息
    print(f"\n4. 撤回第一条消息 (ID: {message_id})...")
    try:
        # 测试不同的请求格式
        print(f"尝试删除消息，URL: {base_url}/chat/messages/{message_id}")
        print(f"参数: user_id={user_id}")
        
        response = requests.delete(
            f"{base_url}/chat/messages/{message_id}",
            params={"user_id": user_id}
        )
        
        print(f"删除请求状态码: {response.status_code}")
        print(f"删除请求响应: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 消息撤回成功")
            print(f"结果: {result.get('message')}")
        else:
            print(f"❌ 消息撤回失败: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"错误详情: {error_detail}")
            except:
                print(f"错误文本: {response.text}")
                
    except Exception as e:
        print(f"❌ 消息撤回异常: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. 查看删除后的会话历史
    print("\n5. 删除后的会话历史...")
    try:
        response = requests.get(f"{base_url}/chat/sessions/{session_id}/history")
        if response.status_code == 200:
            history = response.json()
            print(f"✅ 删除后会话历史，共 {len(history.get('messages', []))} 条消息")
            for i, msg in enumerate(history.get('messages', [])):
                print(f"  {i+1}. [{msg['role']}] {msg['content'][:30]}... (ID: {msg['id']})")
        else:
            print(f"❌ 删除后会话历史获取失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 删除后会话历史获取异常: {e}")
    
    # 6. 测试删除不存在的消息
    print(f"\n6. 测试删除不存在的消息...")
    try:
        fake_message_id = 99999
        response = requests.delete(
            f"{base_url}/chat/messages/{fake_message_id}",
            params={"user_id": user_id}
        )
        
        print(f"删除不存在消息状态码: {response.status_code}")
        if response.status_code == 404:
            print("✅ 正确返回404错误")
        else:
            print(f"❌ 期望404，实际返回: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试删除不存在消息异常: {e}")
    
    # 7. 测试删除其他用户的消息
    print(f"\n7. 测试删除其他用户的消息...")
    try:
        # 先发送一条消息
        response = requests.post(f"{base_url}/chat", json={
            "message": "其他用户的消息",
            "user_id": "other_user",
            "session_id": session_id
        })
        
        if response.status_code == 200:
            other_message_id = response.json().get('message_id')
            
            # 尝试用原用户删除其他用户的消息
            response = requests.delete(
                f"{base_url}/chat/messages/{other_message_id}",
                params={"user_id": user_id}  # 使用不同的用户ID
            )
            
            print(f"删除其他用户消息状态码: {response.status_code}")
            if response.status_code == 404:
                print("✅ 正确阻止删除其他用户的消息")
            else:
                print(f"❌ 应该阻止删除，但返回: {response.status_code}")
                
    except Exception as e:
        print(f"❌ 测试删除其他用户消息异常: {e}")
    
    print("\n" + "=" * 60)
    print("撤回功能测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_delete_message()