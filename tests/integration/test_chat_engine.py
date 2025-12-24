#!/usr/bin/env python3
"""
测试聊天引擎是否正常工作
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 加载环境变量
from dotenv import load_dotenv
env_path = Path(__file__).parent / 'config.env'
load_dotenv(env_path)

def test_chat_engine():
    print("🔍 测试聊天引擎...")
    
    # 检查环境变量
    print("\n1. 检查环境变量...")
    api_key = os.getenv("LLM_API_KEY") or os.getenv("DASHSCOPE_API_KEY") or os.getenv("OPENAI_API_KEY")
    api_base_url = os.getenv("LLM_BASE_URL") or os.getenv("API_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("DEFAULT_MODEL", "qwen-plus")
    
    print(f"API Key: {'已设置' if api_key else '未设置'}")
    print(f"API Base URL: {api_base_url}")
    print(f"Model: {model}")
    
    if not api_key:
        print("❌ API Key未设置，无法测试")
        return False
    
    # 测试导入
    print("\n2. 测试模块导入...")
    try:
        from backend.modules.llm.core.llm_with_plugins import EmotionalChatEngineWithPlugins
        print("✓ EmotionalChatEngineWithPlugins 导入成功")
    except Exception as e:
        print(f"❌ EmotionalChatEngineWithPlugins 导入失败: {e}")
        return False
    
    # 测试引擎初始化
    print("\n3. 测试引擎初始化...")
    try:
        engine = EmotionalChatEngineWithPlugins()
        print("✓ 聊天引擎初始化成功")
    except Exception as e:
        print(f"❌ 聊天引擎初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 测试简单聊天
    print("\n4. 测试简单聊天...")
    try:
        from backend.models import ChatRequest
        
        request = ChatRequest(
            message="你好",
            user_id="test_user",
            session_id=None
        )
        
        print("发送测试消息: '你好'")
        response = engine.chat(request)
        
        print(f"✓ 聊天测试成功")
        print(f"  回复: {response.response[:100]}...")
        print(f"  情绪: {response.emotion}")
        print(f"  会话ID: {response.session_id}")
        print(f"  消息ID: {response.message_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ 聊天测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_engine():
    print("\n🔍 测试简单聊天引擎...")
    
    try:
        from backend.modules.llm.core.llm_core import SimpleEmotionalChatEngine
        from backend.models import ChatRequest
        
        engine = SimpleEmotionalChatEngine()
        print("✓ 简单聊天引擎初始化成功")
        
        request = ChatRequest(
            message="你好",
            user_id="test_user",
            session_id=None
        )
        
        print("发送测试消息: '你好'")
        response = engine.chat(request)
        
        print(f"✓ 简单聊天测试成功")
        print(f"  回复: {response.response[:100]}...")
        print(f"  情绪: {response.emotion}")
        
        return True
        
    except Exception as e:
        print(f"❌ 简单聊天测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_connection():
    print("\n🔍 测试API连接...")
    
    try:
        import requests
        
        api_key = os.getenv("LLM_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
        api_base_url = os.getenv("LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        model = os.getenv("DEFAULT_MODEL", "qwen-plus")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [
                {"role": "user", "content": "你好"}
            ],
            "max_tokens": 100
        }
        
        print(f"测试API连接: {api_base_url}/chat/completions")
        response = requests.post(
            f"{api_base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        print(f"API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                print(f"✓ API连接成功，回复: {content[:100]}...")
                return True
            else:
                print(f"❌ API响应格式异常: {result}")
                return False
        else:
            print(f"❌ API连接失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API连接测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("聊天引擎诊断工具")
    print("=" * 50)
    
    # 测试API连接
    api_ok = test_api_connection()
    
    # 测试简单引擎
    simple_ok = test_simple_engine()
    
    # 测试插件引擎
    plugin_ok = test_chat_engine()
    
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print(f"API连接: {'✅' if api_ok else '❌'}")
    print(f"简单引擎: {'✅' if simple_ok else '❌'}")
    print(f"插件引擎: {'✅' if plugin_ok else '❌'}")
    print("=" * 50)
    
    if not any([api_ok, simple_ok, plugin_ok]):
        print("\n❌ 所有测试都失败了，请检查配置")
        sys.exit(1)
    elif plugin_ok:
        print("\n✅ 聊天引擎工作正常")
        sys.exit(0)
    else:
        print("\n⚠️ 插件引擎有问题，但基础功能可用")
        sys.exit(0)