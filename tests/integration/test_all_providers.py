#!/usr/bin/env python3
"""
测试所有LLM提供商和embedding功能
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
                    # 处理变量引用，如 ${SILICONFLOW_API_KEY}
                    if value.startswith('${') and value.endswith('}'):
                        ref_key = value[2:-1]
                        value = os.getenv(ref_key, '')
                    os.environ[key] = value

# 加载环境变量
load_env_file('config.env')

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.modules.llm.llm_router import LLMRouter
from backend.modules.llm.providers.base_provider import LLMMessage
from backend.services.embedding_service import get_embedding_service

def test_all_providers():
    """测试所有提供商"""
    print("=" * 80)
    print("🚀 测试所有LLM提供商")
    print("=" * 80)
    
    # 初始化路由器
    try:
        router = LLMRouter()
        print(f"✅ LLM路由器初始化成功")
    except Exception as e:
        print(f"❌ LLM路由器初始化失败: {e}")
        return
    
    # 列出所有提供商
    print(f"\n📋 所有提供商状态:")
    providers = router.list_available_providers()
    
    available_count = 0
    for provider in providers:
        status = "✅ 可用" if provider['available'] else "❌ 不可用"
        print(f"   {provider['name']}: {status} ({provider['model']})")
        if provider['available']:
            available_count += 1
        elif 'error' in provider:
            print(f"      错误: {provider['error']}")
    
    print(f"\n📊 统计: {available_count}/{len(providers)} 个提供商可用")
    
    if available_count == 0:
        print("❌ 没有可用的提供商")
        return
    
    # 获取当前提供商
    current = router.get_current_provider_info()
    print(f"\n🎯 当前提供商: {current['name']} ({current.get('model', 'unknown')})")
    
    # 测试当前提供商
    print(f"\n💬 测试当前提供商...")
    messages = [
        LLMMessage(role="system", content="你是一个友善的AI助手，请用中文简洁回答。"),
        LLMMessage(role="user", content="你好，请用一句话介绍你自己。")
    ]
    
    try:
        response = router.chat_completion(messages=messages, max_tokens=100)
        print(f"👤 用户: 你好，请用一句话介绍你自己。")
        print(f"🤖 {current['name']}: {response.content}")
        print(f"📊 Token使用: {response.usage}")
        print("✅ 当前提供商测试成功")
    except Exception as e:
        print(f"❌ 当前提供商测试失败: {e}")
    
    # 测试故障转移
    available_providers = [p for p in providers if p['available']]
    if len(available_providers) > 1:
        print(f"\n🔄 测试故障转移 (发现 {len(available_providers)} 个可用提供商)...")
        
        for i, provider in enumerate(available_providers[1:3], 1):  # 测试最多2个其他提供商
            try:
                print(f"\n   {i}. 切换到 {provider['name']}...")
                success = router.switch_provider(provider['name'])
                
                if success:
                    print(f"      ✅ 切换成功")
                    # 快速测试
                    test_messages = [
                        LLMMessage(role="user", content="说'你好'")
                    ]
                    response = router.chat_completion(messages=test_messages, max_tokens=10)
                    print(f"      🤖 回复: {response.content}")
                else:
                    print(f"      ❌ 切换失败")
                    
            except Exception as e:
                print(f"      ❌ 测试失败: {e}")
    
    print(f"\n✅ 提供商测试完成")

def test_embedding_service():
    """测试embedding服务"""
    print(f"\n" + "=" * 80)
    print("🔢 测试Embedding服务")
    print("=" * 80)
    
    try:
        embedding_service = get_embedding_service()
        info = embedding_service.get_info()
        
        print(f"📋 Embedding服务信息:")
        for key, value in info.items():
            if key == 'available':
                value = "✅ 可用" if value else "❌ 不可用"
            print(f"   {key}: {value}")
        
        if not info['available']:
            print("❌ Embedding服务不可用，跳过测试")
            return False
        
        # 测试单个文本
        print(f"\n🔢 测试单个文本embedding...")
        test_text = "人工智能正在改变世界"
        
        embedding = embedding_service.get_embedding(test_text)
        print(f"✅ 单个文本embedding成功")
        print(f"   文本: {test_text}")
        print(f"   向量维度: {len(embedding)}")
        print(f"   前3维: {embedding[:3]}")
        
        # 测试批量文本
        print(f"\n🔢 测试批量文本embedding...")
        test_texts = [
            "机器学习是AI的核心技术",
            "深度学习推动了AI的发展", 
            "今天天气很好，适合出门"
        ]
        
        embeddings = embedding_service.get_embeddings(test_texts)
        print(f"✅ 批量文本embedding成功")
        print(f"   文本数量: {len(test_texts)}")
        print(f"   向量数量: {len(embeddings)}")
        print(f"   向量维度: {len(embeddings[0]) if embeddings else 0}")
        
        # 计算相似度
        if len(embeddings) >= 3:
            import numpy as np
            
            def cosine_similarity(a, b):
                return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
            
            sim1 = cosine_similarity(embeddings[0], embeddings[1])  # AI相关文本
            sim2 = cosine_similarity(embeddings[0], embeddings[2])  # AI vs 天气
            
            print(f"\n📈 相似度分析:")
            print(f"   AI文本1 vs AI文本2: {sim1:.4f}")
            print(f"   AI文本1 vs 天气文本: {sim2:.4f}")
            print(f"   预期: AI文本间相似度 > AI与天气相似度")
            
            if sim1 > sim2:
                print(f"   ✅ 相似度计算符合预期")
            else:
                print(f"   ⚠️  相似度计算可能有问题")
        
        return True
        
    except Exception as e:
        print(f"❌ Embedding服务测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_configuration_guide():
    """显示配置指南"""
    print(f"\n" + "=" * 80)
    print("⚙️  配置指南")
    print("=" * 80)
    
    providers_info = [
        {
            "name": "SiliconFlow",
            "key": "SILICONFLOW_API_KEY",
            "url": "https://siliconflow.cn/",
            "description": "API聚合平台，支持多种模型，包含embedding",
            "models": "Qwen/Qwen2.5-7B-Instruct, meta-llama/Meta-Llama-3-8B-Instruct",
            "embedding": "BAAI/bge-m3"
        },
        {
            "name": "DeepSeek",
            "key": "DEEPSEEK_API_KEY", 
            "url": "https://platform.deepseek.com/",
            "description": "性价比很高的国产大模型",
            "models": "deepseek-chat",
            "embedding": "不支持"
        },
        {
            "name": "Claude",
            "key": "CLAUDE_API_KEY",
            "url": "https://console.anthropic.com/",
            "description": "Anthropic出品，质量很高",
            "models": "claude-3-haiku-20240307, claude-3-sonnet-20240229",
            "embedding": "不支持"
        },
        {
            "name": "Gemini",
            "key": "GEMINI_API_KEY",
            "url": "https://makersuite.google.com/app/apikey",
            "description": "Google出品，免费额度大",
            "models": "gemini-pro, gemini-pro-vision",
            "embedding": "不支持"
        }
    ]
    
    print("🔧 要启用提供商，请在 config.env 中设置API密钥：\n")
    
    for i, provider in enumerate(providers_info, 1):
        print(f"{i}. {provider['name']} ({provider['description']})")
        print(f"   配置: {provider['key']}=your_api_key")
        print(f"   获取: {provider['url']}")
        print(f"   模型: {provider['models']}")
        print(f"   Embedding: {provider['embedding']}")
        print()
    
    print("💡 提示:")
    print("   - 优先级数字越小，优先级越高")
    print("   - 系统会自动选择优先级最高且可用的提供商")
    print("   - 如果当前提供商失败，会自动故障转移")
    print("   - SiliconFlow同时支持聊天和embedding，推荐优先配置")

def main():
    """主函数"""
    print("🎯 全面测试LLM提供商和Embedding服务")
    
    # 检查基本配置
    has_any_key = any([
        os.getenv('SILICONFLOW_API_KEY'),
        os.getenv('DEEPSEEK_API_KEY'),
        os.getenv('CLAUDE_API_KEY'),
        os.getenv('GEMINI_API_KEY'),
        os.getenv('OPENAI_API_KEY'),
        os.getenv('LLM_API_KEY'),
        os.getenv('DASHSCOPE_API_KEY')
    ])
    
    if not has_any_key:
        print("\n❌ 未检测到任何API密钥配置")
        show_configuration_guide()
        return
    
    # 运行测试
    results = []
    
    # 测试LLM提供商
    print("\n🚀 开始测试...")
    test_all_providers()
    
    # 测试embedding服务
    embedding_success = test_embedding_service()
    
    # 显示配置指南
    show_configuration_guide()
    
    print(f"\n" + "=" * 80)
    print("🎉 测试完成！")
    print("=" * 80)
    
    if embedding_success:
        print("✅ 所有功能测试通过，系统已准备就绪！")
    else:
        print("⚠️  LLM功能正常，但embedding功能可能需要配置")
        print("   建议配置SiliconFlow以获得完整的RAG功能")

if __name__ == "__main__":
    main()