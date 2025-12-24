#!/usr/bin/env python3
"""
测试LLM路由器功能
验证多种LLM提供商的支持
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from backend.modules.llm.llm_router import LLMRouter
from backend.modules.llm.providers.base_provider import LLMMessage
from backend.models import ChatRequest
from backend.services.chat_service import ChatService

async def test_llm_router():
    """测试LLM路由器基本功能"""
    print("=" * 80)
    print("测试LLM路由器")
    print("=" * 80)
    
    try:
        # 初始化路由器
        router = LLMRouter()
        
        # 显示当前提供商信息
        current_info = router.get_current_provider_info()
        print(f"🤖 当前提供商: {current_info['name']}")
        print(f"📋 模型: {current_info.get('model', 'unknown')}")
        print(f"✅ 可用: {current_info['available']}")
        
        # 列出所有提供商
        print(f"\n📊 所有提供商状态:")
        providers = router.list_available_providers()
        for provider in providers:
            status = "✅" if provider['available'] else "❌"
            error = f" ({provider.get('error', '')})" if not provider['available'] and provider.get('error') else ""
            print(f"   {status} {provider['name']}: {provider['model']}{error}")
        
        # 测试聊天功能
        if current_info['available']:
            print(f"\n💬 测试聊天功能...")
            messages = [
                LLMMessage(role="system", content="你是一个友善的AI助手。"),
                LLMMessage(role="user", content="你好，请简单介绍一下自己。")
            ]
            
            response = await router.chat_completion(messages, max_tokens=100)
            print(f"👤 用户: 你好，请简单介绍一下自己。")
            print(f"🤖 AI: {response.content}")
            print(f"📊 使用模型: {response.model}")
            
            if response.usage:
                print(f"📈 Token使用: {response.usage}")
        else:
            print(f"\n⚠️  没有可用的LLM提供商，跳过聊天测试")
        
    except Exception as e:
        print(f"❌ LLM路由器测试失败: {e}")
        import traceback
        traceback.print_exc()

async def test_chat_service_with_router():
    """测试聊天服务使用新路由器"""
    print("\n" + "=" * 80)
    print("测试聊天服务集成")
    print("=" * 80)
    
    try:
        # 初始化聊天服务
        chat_service = ChatService()
        
        # 测试对话
        user_id = "router_test_user"
        session_id = "router_test_session"
        
        test_messages = [
            "你好，我想测试一下新的LLM路由器功能",
            "你现在使用的是什么模型？",
            "能告诉我一些关于RAG技术的信息吗？"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n🔄 第{i}轮对话:")
            print(f"👤 用户: {message}")
            
            request = ChatRequest(
                message=message,
                user_id=user_id,
                session_id=session_id
            )
            
            response = await chat_service.chat(request, use_memory_system=True)
            print(f"🤖 AI: {response.response}")
            print(f"😊 情感: {response.emotion}")
            
            # 检查上下文是否正确传递
            if i > 1 and "路由器" in message and "路由器" not in response.response:
                print(f"⚠️  可能存在上下文传递问题")
            elif i > 1:
                print(f"✅ 上下文传递正常")
        
    except Exception as e:
        print(f"❌ 聊天服务测试失败: {e}")
        import traceback
        traceback.print_exc()

async def test_provider_switching():
    """测试提供商切换功能"""
    print("\n" + "=" * 80)
    print("测试提供商切换")
    print("=" * 80)
    
    try:
        router = LLMRouter()
        
        # 获取可用提供商列表
        providers = router.list_available_providers()
        available_providers = [p for p in providers if p['available']]
        
        if len(available_providers) < 2:
            print(f"⚠️  只有 {len(available_providers)} 个可用提供商，跳过切换测试")
            return
        
        print(f"📋 可用提供商: {[p['name'] for p in available_providers]}")
        
        # 测试切换到不同的提供商
        for provider in available_providers:
            provider_name = provider['name']
            print(f"\n🔄 切换到: {provider_name}")
            
            success = router.switch_provider(provider_name)
            if success:
                current_info = router.get_current_provider_info()
                print(f"✅ 切换成功: {current_info['name']} ({current_info['model']})")
                
                # 测试简单对话
                messages = [LLMMessage(role="user", content="你好")]
                response = await router.chat_completion(messages, max_tokens=50)
                print(f"💬 测试回复: {response.content[:100]}...")
            else:
                print(f"❌ 切换失败")
        
    except Exception as e:
        print(f"❌ 提供商切换测试失败: {e}")
        import traceback
        traceback.print_exc()

async def test_ollama_specific():
    """专门测试Ollama功能"""
    print("\n" + "=" * 80)
    print("测试Ollama本地模型")
    print("=" * 80)
    
    try:
        from backend.modules.llm.providers.ollama_provider import OllamaProvider
        
        # 测试Ollama连接
        config = {
            'base_url': 'http://localhost:11434',
            'model': 'qwen2.5:8b',
            'temperature': 0.7,
            'max_tokens': 1000
        }
        
        provider = OllamaProvider(config)
        
        print(f"🔍 检查Ollama可用性...")
        if provider.is_available():
            print(f"✅ Ollama服务可用")
            
            # 获取模型列表
            models = provider.list_models()
            print(f"📋 可用模型: {models}")
            
            # 测试对话
            messages = [
                LLMMessage(role="system", content="你是一个友善的AI助手，请用中文回答。"),
                LLMMessage(role="user", content="你好，请用一句话介绍自己。")
            ]
            
            print(f"💬 测试Ollama对话...")
            response = await provider.chat_completion(messages)
            print(f"🤖 Ollama回复: {response.content}")
            print(f"📊 Token使用: {response.usage}")
        else:
            print(f"❌ Ollama服务不可用")
            print(f"💡 请确保Ollama已启动并且模型已下载:")
            print(f"   1. 启动Ollama: ollama serve")
            print(f"   2. 下载模型: ollama pull qwen2.5:8b")
        
    except Exception as e:
        print(f"❌ Ollama测试失败: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """主测试函数"""
    print("🚀 LLM路由器功能测试")
    print("=" * 80)
    
    await test_ollama_specific()
    await test_llm_router()
    await test_chat_service_with_router()
    await test_provider_switching()
    
    print("\n" + "=" * 80)
    print("🎯 测试完成")
    print("=" * 80)
    print("\n💡 使用建议:")
    print("1. 🏠 本地开发推荐使用Ollama（免费、隐私、快速）")
    print("2. ☁️  生产环境可以配置多个提供商实现故障转移")
    print("3. 🔧 通过环境变量调整提供商优先级")
    print("4. 📊 监控各提供商的可用性和响应时间")

if __name__ == "__main__":
    asyncio.run(main())