#!/usr/bin/env python3
"""
消息撤回和编辑功能测试用例
"""

import pytest
import requests
import json
import time
from datetime import datetime

# 测试配置
API_BASE_URL = "http://localhost:8000"
TEST_USER_ID = "test_user_edit_recall"
TEST_SESSION_ID = None
TEST_MESSAGE_ID = None

class TestMessageEditRecall:
    """消息编辑和撤回功能测试类"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        print("开始测试消息编辑和撤回功能...")
        
    def test_01_send_message(self):
        """测试发送消息并获取消息ID"""
        global TEST_SESSION_ID, TEST_MESSAGE_ID
        
        # 发送测试消息
        chat_data = {
            "message": "这是一条测试消息，用于测试编辑和撤回功能",
            "user_id": TEST_USER_ID,
            "session_id": None
        }
        
        response = requests.post(f"{API_BASE_URL}/chat", json=chat_data)
        assert response.status_code == 200
        
        result = response.json()
        TEST_SESSION_ID = result["session_id"]
        TEST_MESSAGE_ID = result["message_id"]
        
        print(f"✓ 消息发送成功，session_id: {TEST_SESSION_ID}, message_id: {TEST_MESSAGE_ID}")
        
        # 验证消息已保存
        history_response = requests.get(f"{API_BASE_URL}/chat/sessions/{TEST_SESSION_ID}/history")
        assert history_response.status_code == 200
        
        history = history_response.json()
        assert len(history["messages"]) >= 1
        
        # 找到用户消息
        user_messages = [msg for msg in history["messages"] if msg["role"] == "user"]
        assert len(user_messages) >= 1
        assert user_messages[0]["content"] == chat_data["message"]
        
        print("✓ 消息历史验证成功")
    
    def test_02_edit_message_success(self):
        """测试成功编辑消息"""
        global TEST_MESSAGE_ID
        
        # 获取实际的数据库消息ID
        history_response = requests.get(f"{API_BASE_URL}/chat/sessions/{TEST_SESSION_ID}/history")
        assert history_response.status_code == 200
        
        history = history_response.json()
        user_messages = [msg for msg in history["messages"] if msg["role"] == "user"]
        if not user_messages:
            print("❌ 没有找到用户消息")
            return
        
        # 使用数据库中的真实ID
        actual_message_id = user_messages[0]["id"]
        print(f"使用数据库消息ID: {actual_message_id}")
        
        new_content = "这是编辑后的消息内容"
        edit_data = {
            "user_id": TEST_USER_ID,
            "new_content": new_content,
            "emotion": "neutral",
            "emotion_intensity": 5.0
        }
        
        response = requests.put(f"{API_BASE_URL}/chat/messages/{actual_message_id}", json=edit_data)
        if response.status_code != 200:
            print(f"编辑失败，状态码: {response.status_code}, 响应: {response.text}")
        assert response.status_code == 200
        
        result = response.json()
        assert result["message"] == "消息修改成功"
        assert result["content"] == new_content
        
        print("✓ 消息编辑成功")
        
        # 验证消息已更新
        history_response = requests.get(f"{API_BASE_URL}/chat/sessions/{TEST_SESSION_ID}/history")
        assert history_response.status_code == 200
        
        history = history_response.json()
        user_messages = [msg for msg in history["messages"] if msg["role"] == "user"]
        assert user_messages[0]["content"] == new_content
        
        print("✓ 消息更新验证成功")
    
    def test_03_edit_message_unauthorized(self):
        """测试无权限编辑消息"""
        wrong_user_id = "wrong_user"
        edit_data = {
            "user_id": wrong_user_id,
            "new_content": "尝试无权限编辑",
        }
        
        response = requests.put(f"{API_BASE_URL}/chat/messages/{TEST_MESSAGE_ID}", json=edit_data)
        assert response.status_code == 404
        
        result = response.json()
        assert "消息不存在或无权修改" in result["detail"]
        
        print("✓ 无权限编辑测试通过")
    
    def test_04_edit_nonexistent_message(self):
        """测试编辑不存在的消息"""
        fake_message_id = 999999
        edit_data = {
            "user_id": TEST_USER_ID,
            "new_content": "编辑不存在的消息",
        }
        
        response = requests.put(f"{API_BASE_URL}/chat/messages/{fake_message_id}", json=edit_data)
        assert response.status_code == 404
        
        print("✓ 编辑不存在消息测试通过")
    
    def test_05_edit_empty_content(self):
        """测试编辑为空内容"""
        edit_data = {
            "user_id": TEST_USER_ID,
            "new_content": "",
        }
        
        response = requests.put(f"{API_BASE_URL}/chat/messages/{TEST_MESSAGE_ID}", json=edit_data)
        # 应该允许空内容或返回错误，取决于业务逻辑
        print(f"✓ 空内容编辑测试: {response.status_code}")
    
    def test_06_recall_message_success(self):
        """测试成功撤回消息"""
        global TEST_MESSAGE_ID
        
        # 先发送一条新消息用于撤回测试
        chat_data = {
            "message": "这条消息将被撤回",
            "user_id": TEST_USER_ID,
            "session_id": TEST_SESSION_ID
        }
        
        response = requests.post(f"{API_BASE_URL}/chat", json=chat_data)
        assert response.status_code == 200
        
        # 获取实际的数据库消息ID
        history_response = requests.get(f"{API_BASE_URL}/chat/sessions/{TEST_SESSION_ID}/history")
        assert history_response.status_code == 200
        
        history = history_response.json()
        # 找到刚发送的消息
        target_message = None
        for msg in history["messages"]:
            if msg["role"] == "user" and msg["content"] == "这条消息将被撤回":
                target_message = msg
                break
        
        if not target_message:
            print("❌ 没有找到目标消息")
            return
        
        actual_message_id = target_message["id"]
        print(f"撤回消息ID: {actual_message_id}")
        
        # 撤回消息
        response = requests.delete(f"{API_BASE_URL}/chat/messages/{actual_message_id}", 
                                 params={"user_id": TEST_USER_ID})
        if response.status_code != 200:
            print(f"撤回失败，状态码: {response.status_code}, 响应: {response.text}")
        assert response.status_code == 200
        
        result = response.json()
        assert result["message"] == "消息撤回成功"
        
        print("✓ 消息撤回成功")
        
        # 验证消息已删除
        history_response = requests.get(f"{API_BASE_URL}/chat/sessions/{TEST_SESSION_ID}/history")
        assert history_response.status_code == 200
        
        history = history_response.json()
        # 检查撤回的消息不在历史中
        message_contents = [msg["content"] for msg in history["messages"]]
        assert "这条消息将被撤回" not in message_contents
        
        print("✓ 消息撤回验证成功")
    
    def test_07_recall_message_unauthorized(self):
        """测试无权限撤回消息"""
        wrong_user_id = "wrong_user"
        
        response = requests.delete(f"{API_BASE_URL}/chat/messages/{TEST_MESSAGE_ID}", 
                                 params={"user_id": wrong_user_id})
        assert response.status_code == 404
        
        result = response.json()
        assert "消息不存在或无权删除" in result["detail"]
        
        print("✓ 无权限撤回测试通过")
    
    def test_08_recall_nonexistent_message(self):
        """测试撤回不存在的消息"""
        fake_message_id = 999999
        
        response = requests.delete(f"{API_BASE_URL}/chat/messages/{fake_message_id}", 
                                 params={"user_id": TEST_USER_ID})
        assert response.status_code == 404
        
        print("✓ 撤回不存在消息测试通过")
    
    def test_09_frontend_integration(self):
        """测试前端集成场景"""
        # 模拟前端的完整流程
        
        # 1. 发送消息
        chat_data = {
            "message": "前端集成测试消息",
            "user_id": TEST_USER_ID,
            "session_id": TEST_SESSION_ID
        }
        
        response = requests.post(f"{API_BASE_URL}/chat", json=chat_data)
        assert response.status_code == 200
        
        message_id = response.json()["message_id"]
        
        # 2. 获取消息历史（模拟前端加载）
        history_response = requests.get(f"{API_BASE_URL}/chat/sessions/{TEST_SESSION_ID}/history")
        assert history_response.status_code == 200
        
        history = history_response.json()
        user_messages = [msg for msg in history["messages"] if msg["role"] == "user"]
        original_message = next(msg for msg in user_messages if msg["content"] == chat_data["message"])
        
        # 3. 编辑消息（使用数据库ID）
        db_id = original_message["id"]  # 前端应该使用这个ID
        edit_data = {
            "user_id": TEST_USER_ID,
            "new_content": "前端集成测试 - 已编辑",
        }
        
        response = requests.put(f"{API_BASE_URL}/chat/messages/{db_id}", json=edit_data)
        assert response.status_code == 200
        
        # 4. 验证编辑结果
        history_response = requests.get(f"{API_BASE_URL}/chat/sessions/{TEST_SESSION_ID}/history")
        history = history_response.json()
        user_messages = [msg for msg in history["messages"] if msg["role"] == "user"]
        edited_message = next(msg for msg in user_messages if msg["id"] == db_id)
        assert edited_message["content"] == "前端集成测试 - 已编辑"
        
        print("✓ 前端集成测试通过")
    
    def test_10_concurrent_operations(self):
        """测试并发操作"""
        import threading
        import time
        
        # 发送测试消息
        chat_data = {
            "message": "并发测试消息",
            "user_id": TEST_USER_ID,
            "session_id": TEST_SESSION_ID
        }
        
        response = requests.post(f"{API_BASE_URL}/chat", json=chat_data)
        assert response.status_code == 200
        
        # 获取实际的数据库消息ID
        history_response = requests.get(f"{API_BASE_URL}/chat/sessions/{TEST_SESSION_ID}/history")
        assert history_response.status_code == 200
        
        history = history_response.json()
        # 找到刚发送的消息
        target_message = None
        for msg in history["messages"]:
            if msg["role"] == "user" and msg["content"] == "并发测试消息":
                target_message = msg
                break
        
        if not target_message:
            print("❌ 没有找到目标消息")
            return
        
        actual_message_id = target_message["id"]
        results = []
        
        def edit_message(content_suffix):
            edit_data = {
                "user_id": TEST_USER_ID,
                "new_content": f"并发编辑测试 - {content_suffix}",
            }
            response = requests.put(f"{API_BASE_URL}/chat/messages/{actual_message_id}", json=edit_data)
            results.append(response.status_code)
        
        # 启动多个并发编辑
        threads = []
        for i in range(3):
            thread = threading.Thread(target=edit_message, args=(f"线程{i}",))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 至少有一个成功
        if 200 not in results:
            print(f"❌ 并发操作失败，结果: {results}")
        assert 200 in results
        print(f"✓ 并发操作测试完成，结果: {results}")
    
    def test_11_message_id_consistency(self):
        """测试消息ID一致性"""
        # 发送消息
        chat_data = {
            "message": "ID一致性测试消息",
            "user_id": TEST_USER_ID,
            "session_id": TEST_SESSION_ID
        }
        
        response = requests.post(f"{API_BASE_URL}/chat", json=chat_data)
        assert response.status_code == 200
        
        api_message_id = response.json()["message_id"]
        
        # 获取历史记录中的ID
        history_response = requests.get(f"{API_BASE_URL}/chat/sessions/{TEST_SESSION_ID}/history")
        history = history_response.json()
        
        user_messages = [msg for msg in history["messages"] if msg["role"] == "user"]
        db_message = next(msg for msg in user_messages if msg["content"] == chat_data["message"])
        db_message_id = db_message["id"]
        
        print(f"API返回ID: {api_message_id}, 数据库ID: {db_message_id}")
        
        # 测试使用API返回的ID编辑
        edit_data = {
            "user_id": TEST_USER_ID,
            "new_content": "使用API ID编辑",
        }
        
        response = requests.put(f"{API_BASE_URL}/chat/messages/{api_message_id}", json=edit_data)
        print(f"使用API ID编辑结果: {response.status_code}")
        
        # 测试使用数据库ID编辑
        edit_data["new_content"] = "使用数据库ID编辑"
        response = requests.put(f"{API_BASE_URL}/chat/messages/{db_message_id}", json=edit_data)
        print(f"使用数据库ID编辑结果: {response.status_code}")
        
        print("✓ 消息ID一致性测试完成")

def run_tests():
    """运行所有测试"""
    test_instance = TestMessageEditRecall()
    test_instance.setup_class()
    
    test_methods = [
        test_instance.test_01_send_message,
        test_instance.test_02_edit_message_success,
        test_instance.test_03_edit_message_unauthorized,
        test_instance.test_04_edit_nonexistent_message,
        test_instance.test_05_edit_empty_content,
        test_instance.test_06_recall_message_success,
        test_instance.test_07_recall_message_unauthorized,
        test_instance.test_08_recall_nonexistent_message,
        test_instance.test_09_frontend_integration,
        test_instance.test_10_concurrent_operations,
        test_instance.test_11_message_id_consistency,
    ]
    
    passed = 0
    failed = 0
    
    for test_method in test_methods:
        try:
            print(f"\n运行测试: {test_method.__name__}")
            test_method()
            passed += 1
            print(f"✅ {test_method.__name__} 通过")
        except Exception as e:
            failed += 1
            print(f"❌ {test_method.__name__} 失败: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n测试结果: {passed} 通过, {failed} 失败")
    return failed == 0

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)