#!/usr/bin/env python3
"""
测试SiliconFlow API功能
包括聊天和embedding功能
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

from backend.modules.llm.providers.siliconflow_provider import SiliconFlowProvider
from backend.modules.llm.providers.base_provider import LLMMessage
from backend.services.embedding_service import get_embedding_service

def test_siliconflow_chat():
    """测试SiliconFlow聊天功能"""
    print("=" * 60)
    print("测试SiliconFlow聊天功能")
    print("=" * 60)
    
    api_key = os.getenv('SILICONFLOW_API_KEY')
    if not api_key:
        print("❌ 请先设置 SILICONFLOW_API_KEY 环境变量")
        return False
    
    # 初始化提供商
    config = {
        'api_key': api_key,
        'base_url': 'https://api.siliconflow.cn/v1',
        'model': 'Qwen/Qwen2.5-7B-Instruct',
        'temperature': 0.7,
        'max_tokens': 2000
    }
    
    try:
        provider = SiliconFlowProvider(config)
        print(f"✅ SiliconFlow提供商初始化成功")
    except Exception as e:
        print(f"❌ SiliconFlow提供商初始化失败: {e}")
        return False
    
    # 检查可用性
    if not provider.is_available():
        print("❌ SiliconFlow服务不可用")
        return False
    
    print("✅ SiliconFlow服务可用")
    
    # 获取模型列表
    print("\n📋 获取可用模型列表...")
    try:
        models = provider.list_models()
        if models:
            print(f"✅ 找到 {len(models)} 个可用模型:")
            for model in models[:10]:  # 只显示前10个
                model_id = model.get('id', 'unknown')
                print(f"   - {model_id}")
            if len(models) > 10:
                print(f"   ... 还有 {len(models) - 10} 个模型")
        else:
            print("⚠️  未获取到模型列表")
    except Exception as e:
        print(f"⚠️  获取模型列表失败: {e}")
    
    # 测试聊天
    print(f"\n💬 测试聊天功能...")
    messages = [
        LLMMessage(role="system", content="你是一个友善的AI助手，请用中文回答。"),
        LLMMessage(role="user", content="你好，请简单介绍一下SiliconFlow平台。")
    ]
    
    try:
        response = provider.chat_completion_sync(messages, max_tokens=200)
        print(f"👤 用户: 你好，请简单介绍一下SiliconFlow平台。")
        print(f"🤖 AI: {response.content}")
        print(f"📊 Token使用: {response.usage}")
        print("✅ 聊天测试成功")
        return True
    except Exception as e:
        print(f"❌ 聊天测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_siliconflow_embedding():
    """测试SiliconFlow embedding功能"""
    print("\n" + "=" * 60)
    print("测试SiliconFlow Embedding功能")
    print("=" * 60)
    
    api_key = os.getenv('SILICONFLOW_API_KEY')
    if not api_key:
        print("❌ 请先设置 SILICONFLOW_API_KEY 环境变量")
        return False
    
    # 初始化提供商
    config = {
        'api_key': api_key,
        'base_url': 'https://api.siliconflow.cn/v1',
        'model': 'BAAI/bge-m3'
    }
    
    try:
        provider = SiliconFlowProvider(config)
        print(f"✅ SiliconFlow提供商初始化成功")
    except Exception as e:
        print(f"❌ SiliconFlow提供商初始化失败: {e}")
        return False
    
    # 测试embedding
    test_texts = [
        "你好，世界！",
        "SiliconFlow是一个优秀的AI API平台",
        "机器学习和深度学习是人工智能的重要分支"
    ]
    
    print(f"\n🔢 测试embedding功能...")
    print(f"测试文本数量: {len(test_texts)}")
    
    try:
        embeddings = provider.get_embedding(test_texts, model="BAAI/bge-m3")
        print(f"✅ Embedding获取成功")
        print(f"📊 结果统计:")
        print(f"   - 文本数量: {len(test_texts)}")
        print(f"   - 向量数量: {len(embeddings)}")
        if embeddings:
            print(f"   - 向量维度: {len(embeddings[0])}")
            print(f"   - 第一个向量前5维: {embeddings[0][:5]}")
        
        # 测试相似度计算
        if len(embeddings) >= 2:
            import numpy as np
            
            def cosine_similarity(a, b):
                return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
            
            sim1 = cosine_similarity(embeddings[0], embeddings[1])
            sim2 = cosine_similarity(embeddings[0], embeddings[2])
            
            print(f"\n📈 相似度测试:")
            print(f"   - 文本1 vs 文本2: {sim1:.4f}")
            print(f"   - 文本1 vs 文本3: {sim2:.4f}")
        
        return True
    except Exception as e:
        print(f"❌ Embedding测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_embedding_service():
    """测试embedding服务"""
    print("\n" + "=" * 60)
    print("测试Embedding服务")
    print("=" * 60)
    
    try:
        embedding_service = get_embedding_service()
        info = embedding_service.get_info()
        
        print(f"📋 Embedding服务信息:")
        print(f"   - 提供商: {info['provider']}")
        print(f"   - 模型: {info['model']}")
        print(f"   - 可用性: {'✅' if info['available'] else '❌'}")
        print(f"   - 基础URL: {info['base_url']}")
        
        if not info['available']:
            print("❌ Embedding服务不可用")
            return False
        
        # 测试单个文本embedding
        test_text = "这是一个测试文本"
        print(f"\n🔢 测试单个文本embedding...")
        
        embedding = embedding_service.get_embedding(test_text)
        print(f"✅ 单个文本embedding获取成功")
        print(f"   - 文本: {test_text}")
        print(f"   - 向量维度: {len(embedding)}")
        print(f"   - 前5维: {embedding[:5]}")
        
        # 测试批量文本embedding
        test_texts = [
            "人工智能是未来的趋势",
            "机器学习改变了世界",
            "今天天气很好"
        ]
        
        print(f"\n🔢 测试批量文本embedding...")
        embeddings = embedding_service.get_embeddings(test_texts)
        print(f"✅ 批量文本embedding获取成功")
        print(f"   - 文本数量: {len(test_texts)}")
        print(f"   - 向量数量: {len(embeddings)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Embedding服务测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🚀 SiliconFlow功能测试")
    
    # 检查API密钥
    api_key = os.getenv('SILICONFLOW_API_KEY')
    if not api_key:
        print("\n❌ 未设置 SILICONFLOW_API_KEY")
        print("请在 config.env 中设置:")
        print("SILICONFLOW_API_KEY=your_siliconflow_api_key")
        print("\n获取API密钥: https://siliconflow.cn/")
        return
    
    # 运行测试
    results = []
    
    # 测试聊天功能
    results.append(("聊天功能", test_siliconflow_chat()))
    
    # 测试embedding功能
    results.append(("Embedding功能", test_siliconflow_embedding()))
    
    # 测试embedding服务
    results.append(("Embedding服务", test_embedding_service()))
    
    # 显示测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    if all_passed:
        print("\n🎉 所有测试通过！SiliconFlow集成成功！")
    else:
        print("\n⚠️  部分测试失败，请检查配置和网络连接")

if __name__ == "__main__":
    main()