#!/usr/bin/env python3
"""
测试 RAG 系统与新的 Embedding 提供商集成
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.modules.rag.core.knowledge_base import KnowledgeBaseManager, PsychologyKnowledgeLoader
from backend.modules.rag.core.embedding_providers import get_embedding_instance
from config import Config

def test_rag_with_siliconflow():
    """测试使用 SiliconFlow embedding 的完整 RAG 流程"""
    print("=== 测试 RAG 系统与 SiliconFlow Embedding ===\n")
    
    try:
        # 创建知识库管理器
        print("1. 创建知识库管理器...")
        kb_manager = KnowledgeBaseManager(
            persist_directory="./test_rag_chroma_db",
            embedding_provider="siliconflow",
            embedding_model="BAAI/bge-m3"
        )
        
        # 加载示例知识
        print("2. 加载心理健康知识...")
        loader = PsychologyKnowledgeLoader(kb_manager)
        loader.load_sample_knowledge()
        
        # 获取统计信息
        stats = kb_manager.get_stats()
        print("3. 知识库统计信息:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        print()
        
        # 测试检索功能
        test_queries = [
            "我最近总是失眠，怎么办？",
            "感到很焦虑，有什么缓解方法？",
            "如何进行正念练习？",
            "认知行为疗法是什么？",
            "怎样建立心理韧性？"
        ]
        
        print("4. 测试知识检索功能:")
        for i, query in enumerate(test_queries, 1):
            print(f"\n查询 {i}: {query}")
            try:
                # 使用向量搜索
                results = kb_manager.search_similar(query, k=2)
                print(f"找到 {len(results)} 个相关文档:")
                
                for j, doc in enumerate(results, 1):
                    print(f"\n  结果 {j}:")
                    print(f"    来源: {doc.metadata.get('source', '未知')}")
                    print(f"    主题: {doc.metadata.get('topic', '未知')}")
                    print(f"    内容预览: {doc.page_content[:150]}...")
                    
                # 测试带评分的搜索
                if kb_manager.embeddings:
                    scored_results = kb_manager.search_with_score(query, k=1)
                    if scored_results:
                        doc, score = scored_results[0]
                        print(f"    最高相似度分数: {score:.4f}")
                        
            except Exception as e:
                print(f"    ❌ 检索失败: {e}")
        
        print("\n✅ RAG 系统测试完成！")
        
    except Exception as e:
        print(f"❌ RAG 系统测试失败: {e}")
        import traceback
        traceback.print_exc()


def test_different_embedding_providers():
    """测试不同的 embedding 提供商"""
    print("\n=== 测试不同 Embedding 提供商的 RAG 性能 ===\n")
    
    providers_to_test = [
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
    
    test_query = "我感到很焦虑，有什么方法可以缓解？"
    
    for config in providers_to_test:
        print(f"测试 {config['name']}:")
        try:
            # 创建知识库
            kb_manager = KnowledgeBaseManager(
                persist_directory=f"./test_rag_{config['name'].replace(' ', '_').replace('/', '_')}",
                embedding_provider=config['provider'],
                embedding_model=config['model']
            )
            
            # 加载知识
            loader = PsychologyKnowledgeLoader(kb_manager)
            loader.load_sample_knowledge()
            
            # 测试检索
            import time
            start_time = time.time()
            results = kb_manager.search_similar(test_query, k=3)
            search_time = time.time() - start_time
            
            print(f"  检索时间: {search_time:.3f}秒")
            print(f"  找到结果: {len(results)}个")
            
            if results:
                print(f"  最佳匹配: {results[0].metadata.get('topic', '未知')}")
                print(f"  内容预览: {results[0].page_content[:100]}...")
            
            print("  ✅ 测试成功\n")
            
        except Exception as e:
            print(f"  ❌ 测试失败: {e}\n")


def test_embedding_model_comparison():
    """比较不同 embedding 模型的效果"""
    print("=== Embedding 模型效果比较 ===\n")
    
    # 测试不同的 SiliconFlow 模型
    models_to_test = [
        "BAAI/bge-m3",
        "BAAI/bge-large-zh-v1.5",
        "sentence-transformers/all-MiniLM-L6-v2"
    ]
    
    test_text = "我感到焦虑和压力，需要一些放松的方法"
    
    for model in models_to_test:
        print(f"测试模型: {model}")
        try:
            embeddings = get_embedding_instance(
                provider="siliconflow",
                model=model
            )
            
            if embeddings:
                vector = embeddings.embed_query(test_text)
                print(f"  ✅ 成功生成向量，维度: {len(vector)}")
                print(f"  向量范围: [{min(vector):.4f}, {max(vector):.4f}]")
            else:
                print("  ❌ 无法创建 embedding 实例")
                
        except Exception as e:
            print(f"  ❌ 测试失败: {e}")
        print()


if __name__ == "__main__":
    test_rag_with_siliconflow()
    test_different_embedding_providers()
    test_embedding_model_comparison()