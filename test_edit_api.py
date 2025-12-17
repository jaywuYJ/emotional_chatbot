#!/usr/bin/env python3
"""
测试编辑API是否正常工作
"""
import requests
import json
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_edit_api():
    """测试编辑API"""
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("测试编辑API")
    print("=" * 60)
    
    # 1. 发送一条消息
    print("\n1. 发送第一条消息...")
    chat_data = {
        "message": "今天天气怎么样？",
        "user_id": "test_user",
        "session_id": "test_session_123"
    }
    
    try:
        response = requests.post(f"{base_url}/chat", json=chat_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 消息发送成功")
            print(f"  消息ID: {result.get('message_id')}")
            print(f"  AI回复: {result.get('response', '')[:100]}...")
            message_id = result.get('message_id')
        else:
            print(f"✗ 消息发送失败: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"✗ 消息发送异常: {e}")
        return
    
    # 2. 发送第二条消息
    print("\n2. 发送第二条消息...")
    chat_data2 = {
        "message": "那明天呢？",
        "user_id": "test_user",
        "session_id": "test_session_123"
    }
    
    try:
        response = requests.post(f"{base_url}/chat", json=chat_data2)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 第二条消息发送成功")
            print(f"  AI回复: {result.get('response', '')[:100]}...")
        else:
            print(f"✗ 第二条消息发送失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ 第二条消息发送异常: {e}")
    
    # 3. 获取会话历史
    print("\n3. 获取会话历史...")
    try:
        response = requests.get(f"{base_url}/chat/sessions/test_session_123/history")
        if response.status_code == 200:
            history = response.json()
            print(f"✓ 会话历史获取成功，共 {len(history.get('messages', []))} 条消息")
            for i, msg in enumerate(history.get('messages', [])):
                print(f"  {i+1}. [{msg['role']}] {msg['content'][:50]}... (ID: {msg['id']})")
        else:
            print(f"✗ 会话历史获取失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ 会话历史获取异常: {e}")
    
    # 4. 编辑第一条消息
    print(f"\n4. 编辑第一条消息 (ID: {message_id})...")
    edit_data = {
        "user_id": "test_user",
        "new_content": "今天北京的天气如何？"
    }
    
    try:
        response = requests.put(f"{base_url}/chat/messages/{message_id}", json=edit_data)
        print(f"编辑请求状态码: {response.status_code}")
        print(f"编辑请求响应: {response.text[:500]}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 消息编辑成功")
            print(f"  编辑结果: {result.get('message')}")
            print(f"  删除的消息数量: {result.get('deleted_messages_count', 0)}")
            
            if result.get('new_response'):
                print(f"  新的AI回复: {result['new_response'].get('content', '')[:100]}...")
                print(f"  回复情感: {result['new_response'].get('emotion', 'unknown')}")
            else:
                print(f"  没有生成新的AI回复")
        else:
            print(f"✗ 消息编辑失败: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"  错误详情: {error_detail}")
            except:
                print(f"  错误文本: {response.text}")
    except Exception as e:
        print(f"✗ 消息编辑异常: {e}")
    
    # 5. 再次获取会话历史查看变化
    print("\n5. 编辑后的会话历史...")
    try:
        response = requests.get(f"{base_url}/chat/sessions/test_session_123/history")
        if response.status_code == 200:
            history = response.json()
            print(f"✓ 编辑后会话历史，共 {len(history.get('messages', []))} 条消息")
            for i, msg in enumerate(history.get('messages', [])):
                print(f"  {i+1}. [{msg['role']}] {msg['content'][:50]}... (ID: {msg['id']})")
        else:
            print(f"✗ 编辑后会话历史获取失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ 编辑后会话历史获取异常: {e}")
    
    print("\n" + "=" * 60)
    print("API测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_edit_api()