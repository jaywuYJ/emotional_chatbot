#!/usr/bin/env python3
"""
测试新的LLM提供商（DeepSeek、Claude、Gemini）
"""
import os
import sys

# 手动加载config.env文件
def load_env_file(file_path):
    """手动加载.env文件"""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

# 加载环境变量
load_env_file('config.env')

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.modules.llm.llm_router import LLMRouter
from backend.modules.llm.providers.base_provider import LLMMessage

def test_providers():
    print("=" * 60)
    print("测试新的LLM提供商")
    print("=" * 60)
    
    # 初始化路由器
    try:
        router = LLMRouter()
        print(f"✅ LLM路由器初始化成功")
    except Exception as e:
        print(f"❌ LLM路由器初始化失败: {e}")
        return
    
    # 列出所有可用的提供商
    print("\n📋 可用的提供商:")
    providers = router.list_available_providers()
    for provider in providers:
        status = "✅" if provider['available'] else "❌"
        print(f"   {status} {provider['name']}: {provider['model']}")
        if not provider['available'] and 'error' in provider:
            print(f"      错误: {provider['error']}")
    
    # 获取当前提供商信息
    current_provider = router.get_current_provider_info()
    print(f"\n🎯 当前选择的提供商: {current_provider['name']}")
    if current_provider['available']:
        print(f"   模型: {current_provider.get('model', 'unknown')}")
    else:
        print("   状态: 不可用")
        return
    
    # 测试对话
    print(f"\n💬 测试与 {current_provider['name']} 的对话...")
    
    messages = [
        LLMMessage(role="system", content="你是一个友善的AI助手，请用中文回答。"),
        LLMMessage(role="user", content="你好，请简单介绍一下自己。")
    ]
    
    try:
        response = router.chat_completion(messages=messages, max_tokens=100)
        print(f"👤 用户: 你好，请简单介绍一下自己。")
        print(f"🤖 AI: {response.content}")
        print(f"📊 Token使用: {response.usage}")
        print("✅ 对话测试成功")
    except Exception as e:
        print(f"❌ 对话测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试故障转移
    print(f"\n🔄 测试故障转移功能...")
    available_providers = [p for p in providers if p['available']]
    
    if len(available_providers) > 1:
        print(f"发现 {len(available_providers)} 个可用提供商，测试切换...")
        
        for provider in available_providers[1:2]:  # 只测试第二个提供商
            try:
                success = router.switch_provider(provider['name'])
                if success:
                    print(f"✅ 成功切换到: {provider['name']}")
                    
                    # 测试新提供商
                    response = router.chat_completion(messages=messages, max_tokens=50)
                    print(f"🤖 {provider['name']}: {response.content[:100]}...")
                else:
                    print(f"❌ 切换到 {provider['name']} 失败")
            except Exception as e:
                print(f"❌ 测试 {provider['name']} 失败: {e}")
    else:
        print("只有一个可用提供商，无法测试故障转移")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

def show_config_help():
    """显示配置帮助"""
    print("\n" + "=" * 60)
    print("配置说明")
    print("=" * 60)
    
    print("\n🔧 要启用新的提供商，请在 config.env 中配置相应的API密钥：")
    
    print("\n1. SiliconFlow (推荐，API聚合平台，支持多种模型):")
    print("   SILICONFLOW_API_KEY=your_siliconflow_api_key")
    print("   获取地址: https://siliconflow.cn/")
    print("   支持模型: Qwen/Qwen2.5-7B-Instruct, meta-llama/Meta-Llama-3-8B-Instruct 等")
    print("   Embedding: BAAI/bge-m3")
    
    print("\n2. DeepSeek (性价比高):")
    print("   DEEPSEEK_API_KEY=your_deepseek_api_key")
    print("   获取地址: https://platform.deepseek.com/")
    
    print("\n3. Claude (质量很高):")
    print("   CLAUDE_API_KEY=your_claude_api_key")
    print("   获取地址: https://console.anthropic.com/")
    
    print("\n4. Gemini (免费额度大):")
    print("   GEMINI_API_KEY=your_gemini_api_key")
    print("   获取地址: https://makersuite.google.com/app/apikey")
    
    print("\n💡 提示:")
    print("   - 优先级数字越小，优先级越高")
    print("   - 系统会自动选择优先级最高且可用的提供商")
    print("   - 如果当前提供商失败，会自动故障转移到下一个可用提供商")

if __name__ == "__main__":
    test_providers()
    show_config_help()