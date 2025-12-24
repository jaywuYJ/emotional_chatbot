#!/usr/bin/env python3
"""
测试 RAG 系统的文本匹配模式（不依赖外部 embedding API）
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.modules.rag.core.knowledge_base import KnowledgeBaseManager, PsychologyKnowledgeLoader

def test_text_matching_mode():
    """测试文本匹配模式的 RAG 系统"""
    print("=== 测试文本匹配模式的 RAG 系统 ===\n")
    
    try:
        # 创建知识库管理器（强制使用文本匹配模式）
        print("1. 创建知识库管理器（文本匹配模式）...")
        kb_manager = KnowledgeBaseManager(
            persist_directory="./test_text_mode_chroma_db",
            embedding_provider=None,  # 强制不使用 embedding
            embedding_model=None
        )
        
        # 手动设置为文本匹配模式
        kb_manager.embeddings = None
        
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
        
        print("4. 测试文本匹配检索功能:")
        for i, query in enumerate(test_queries, 1):
            print(f"\n查询 {i}: {query}")
            try:
                import time
                start_time = time.time()
                results = kb_manager.search_similar(query, k=3)
                search_time = time.time() - start_time
                
                print(f"检索时间: {search_time:.3f}秒")
                print(f"找到 {len(results)} 个相关文档:")
                
                for j, doc in enumerate(results, 1):
                    print(f"\n  结果 {j}:")
                    print(f"    来源: {doc.metadata.get('source', '未知')}")
                    print(f"    主题: {doc.metadata.get('topic', '未知')}")
                    print(f"    内容预览: {doc.page_content[:150]}...")
                    
            except Exception as e:
                print(f"    ❌ 检索失败: {e}")
        
        print("\n✅ 文本匹配模式 RAG 系统测试完成！")
        
    except Exception as e:
        print(f"❌ RAG 系统测试失败: {e}")
        import traceback
        traceback.print_exc()


def create_text_mode_knowledge_base():
    """创建一个专门的文本匹配模式知识库类"""
    
    class TextModeKnowledgeBase(KnowledgeBaseManager):
        """文本匹配模式的知识库"""
        
        def __init__(self, persist_directory: str = "./text_mode_kb"):
            super().__init__(persist_directory=persist_directory)
            # 强制使用文本匹配模式
            self.embeddings = None
            self.text_storage = []
            print("✓ 初始化文本匹配模式知识库")
        
        def create_vectorstore(self, chunks):
            """重写向量存储创建，使用简单文本存储"""
            print(f"使用文本存储模式，存储 {len(chunks)} 个文档块")
            
            # 为每个文档块添加元数据
            for i, chunk in enumerate(chunks):
                if 'chunk_id' not in chunk.metadata:
                    chunk.metadata['chunk_id'] = i
                if 'timestamp' not in chunk.metadata:
                    chunk.metadata['timestamp'] = "2025-12-23T17:26:00"
            
            # 直接存储文本块
            self.text_storage = chunks
            self.vectorstore = None
            print("✓ 文本存储创建完成")
            return None
        
        def search_similar(self, query: str, k: int = 3):
            """重写搜索方法，使用关键词匹配"""
            print(f"执行文本匹配搜索: {query[:50]}...")
            
            query_lower = query.lower()
            results = []
            
            # 关键词提取和匹配
            keywords = self._extract_keywords(query_lower)
            
            # 为每个文档计算匹配分数
            scored_docs = []
            for doc in self.text_storage:
                score = self._calculate_text_similarity(query_lower, doc.page_content.lower(), keywords)
                if score > 0:
                    scored_docs.append((doc, score))
            
            # 按分数排序
            scored_docs.sort(key=lambda x: x[1], reverse=True)
            
            # 返回前k个结果
            results = [doc for doc, score in scored_docs[:k]]
            
            print(f"文本匹配搜索完成，返回 {len(results)} 个结果")
            return results
        
        def _extract_keywords(self, text: str):
            """提取关键词"""
            # 简单的关键词提取
            stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
            words = []
            for word in text.split():
                if len(word) > 1 and word not in stop_words:
                    words.append(word)
            return words
        
        def _calculate_text_similarity(self, query: str, content: str, keywords: list):
            """计算文本相似度分数"""
            score = 0
            
            # 直接包含查询的加分
            if query in content:
                score += 10
            
            # 关键词匹配加分
            for keyword in keywords:
                if keyword in content:
                    score += 5
            
            # 部分匹配加分
            query_words = query.split()
            for word in query_words:
                if len(word) > 2 and word in content:
                    score += 2
            
            return score
    
    return TextModeKnowledgeBase


def test_enhanced_text_mode():
    """测试增强的文本匹配模式"""
    print("\n=== 测试增强的文本匹配模式 ===\n")
    
    try:
        # 创建增强的文本模式知识库
        TextModeKB = create_text_mode_knowledge_base()
        kb_manager = TextModeKB("./enhanced_text_mode_kb")
        
        # 加载知识
        loader = PsychologyKnowledgeLoader(kb_manager)
        loader.load_sample_knowledge()
        
        # 测试查询
        test_queries = [
            "失眠怎么办",
            "焦虑缓解方法",
            "正念练习",
            "认知行为疗法",
            "心理韧性"
        ]
        
        print("测试增强文本匹配:")
        for query in test_queries:
            print(f"\n查询: {query}")
            results = kb_manager.search_similar(query, k=2)
            
            for i, doc in enumerate(results, 1):
                print(f"  结果 {i}: {doc.metadata.get('topic', '未知')}")
                print(f"    内容: {doc.page_content[:100]}...")
        
        print("\n✅ 增强文本匹配模式测试完成！")
        
    except Exception as e:
        print(f"❌ 增强文本匹配测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_text_matching_mode()
    test_enhanced_text_mode()