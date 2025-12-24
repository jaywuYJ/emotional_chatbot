#!/usr/bin/env python3
"""
测试 Embedding 提供商系统
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.modules.rag.core.embedding_providers import EmbeddingProviderManager, get_embedding_instance
from backend.modules.rag.core.knowledge_base import KnowledgeBaseManager
from config import Config

def test_embedding_providers():
    """测试所有可用的 embedding 提供商"""
    print("=== 测试 Embedding 提供商系统 ===\n")
    
    # 显示当前配置
    print("当前配置:")
    print(f"  EMBEDDING_PROVIDER: {Config.EMBEDDING_PROVIDER}")
    print(f"  EMBEDDING_MODEL: {Config.EMBEDDING_MODEL}")
    print(f"  EMBEDDING_API_KEY: {'已设置' if Config.EMBEDDING_API_KEY else '未设置'}")
    print(f"  EMBEDDING_BASE_URL: {Config.EMBEDDING_BASE_URL}")
    print()
    
    # 创建管理器
    manager = EmbeddingProviderManager()
    
    # 获取可用提供商
    print("检查可用的提供商:")
    available_providers = manager.get_available_providers()
    if available_providers:
        for provider in available_providers:
            print(f"  ✓ {provider}")
    else:
        print("  ❌ 没有可用的提供商")
    print()
    
    # 测试默认配置
    print("测试默认配置的 embedding:")
    try:
        embeddings = get_embedding_instance()
        if embeddings:
            print("  ✓ 成功创建 embedding 实例")
            
            # 测试嵌入功能
            test_text = "这是一个测试文本，用于验证 embedding 功能"
            print(f"  测试文本: {test_text}")
            
            vector = embeddings.embed_query(test_text)
            if vector and len(vector) > 0:
                print(f"  ✓ 成功生成向量，维度: {len(vector)}")
                print(f"  向量前5个值: {vector[:5]}")
            else:
                print("  ❌ 向量生成失败")
        else:
            print("  ❌ 创建 embedding 实例失败")
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
    print()
    
    # 测试不同提供商
    test_configs = [
        {
            "name": "SiliconFlow (BAAI/bge-m3)",
            "provider": "siliconflow",
            "model": "BAAI/bge-m3"
        },
        {
            "name": "SiliconFlow (text-embedding-ada-002)",
            "provider": "siliconflow", 
            "model": "text-embedding-ada-002"
        },
        {
            "name": "OpenAI (text-embedding-ada-002)",
            "provider": "openai",
            "model": "text-embedding-ada-002"
        },
        {
            "name": "Ollama (nomic-embed-text)",
            "provider": "ollama",
            "model": "nomic-embed-text"
        }
    ]
    
    print("测试不同的提供商配置:")
    for config in test_configs:
        print(f"\n测试 {config['name']}:")
        try:
            success = manager.test_embedding(config['provider'], config['model'])
            if success:
                print(f"  ✓ {config['name']} 测试成功")
            else:
                print(f"  ❌ {config['name']} 测试失败")
        except Exception as e:
            print(f"  ❌ {config['name']} 测试异常: {e}")


def test_knowledge_base_with_embedding():
    """测试知识库与 embedding 的集成"""
    print("\n=== 测试知识库与 Embedding 集成 ===\n")
    
    try:
        # 使用默认配置创建知识库
        print("创建知识库管理器（使用默认 embedding 配置）:")
        kb_manager = KnowledgeBaseManager(
            persist_directory="./test_chroma_db",
            embedding_provider=Config.EMBEDDING_PROVIDER,
            embedding_model=Config.EMBEDDING_MODEL
        )
        
        # 获取统计信息
        stats = kb_manager.get_stats()
        print("知识库统计信息:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        print()
        
        # 测试不同的 embedding 配置
        test_configs = [
            {
                "name": "SiliconFlow BAAI/bge-m3",
                "provider": "siliconflow",
                "model": "BAAI/bge-m3"
            },
            {
                "name": "文本匹配模式",
                "provider": None,
                "model": None
            }
        ]
        
        for config in test_configs:
            print(f"测试配置: {config['name']}")
            try:
                kb = KnowledgeBaseManager(
                    persist_directory=f"./test_chroma_db_{config['name'].replace(' ', '_').replace('/', '_')}",
                    embedding_provider=config['provider'],
                    embedding_model=config['model']
                )
                
                stats = kb.get_stats()
                print(f"  状态: {stats.get('status', '未知')}")
                print(f"  Embedding 提供商: {stats.get('embedding_provider', '未知')}")
                print(f"  Embedding 模型: {stats.get('embedding_model', '未知')}")
                print("  ✓ 创建成功")
                
            except Exception as e:
                print(f"  ❌ 创建失败: {e}")
            print()
            
    except Exception as e:
        print(f"❌ 知识库测试失败: {e}")


if __name__ == "__main__":
    test_embedding_providers()
    test_knowledge_base_with_embedding()