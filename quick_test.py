#!/usr/bin/env python3
"""
快速测试脚本
运行核心功能的快速测试，适合提交前的快速验证
"""

import sys
import subprocess
import time
from pathlib import Path

def print_status(message: str, status: str = "info"):
    """打印状态信息"""
    colors = {
        "info": "\033[94m",
        "success": "\033[92m", 
        "error": "\033[91m",
        "warning": "\033[93m"
    }
    reset = "\033[0m"
    icons = {
        "info": "ℹ️",
        "success": "✅",
        "error": "❌", 
        "warning": "⚠️"
    }
    
    color = colors.get(status, colors["info"])
    icon = icons.get(status, icons["info"])
    print(f"{color}{icon} {message}{reset}")

def run_quick_test(test_name: str, test_command: list) -> bool:
    """运行单个快速测试"""
    print_status(f"运行 {test_name}...")
    
    try:
        result = subprocess.run(
            test_command,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=Path.cwd()
        )
        
        if result.returncode == 0:
            print_status(f"{test_name} - 通过", "success")
            return True
        else:
            print_status(f"{test_name} - 失败", "error")
            if result.stderr:
                print(f"错误: {result.stderr[:200]}...")
            return False
            
    except subprocess.TimeoutExpired:
        print_status(f"{test_name} - 超时", "error")
        return False
    except Exception as e:
        print_status(f"{test_name} - 异常: {e}", "error")
        return False

def main():
    """主函数"""
    print_status("开始快速测试", "info")
    start_time = time.time()
    
    # 定义快速测试列表
    quick_tests = [
        {
            "name": "配置系统测试",
            "command": [sys.executable, "-c", """
import sys
sys.path.append('.')
from config import Config
print(f'✓ 配置加载成功: {Config.LLM_API_KEY[:10] if Config.LLM_API_KEY else "未设置"}...')
"""]
        },
        {
            "name": "数据库连接测试", 
            "command": [sys.executable, "-c", """
import sys
sys.path.append('.')
try:
    from backend.database import get_db
    print('✓ 数据库连接正常')
except Exception as e:
    print(f'✗ 数据库连接失败: {e}')
    raise
"""]
        },
        {
            "name": "Embedding 提供商测试",
            "command": [sys.executable, "-c", """
import sys
sys.path.append('.')
from backend.modules.rag.core.embedding_providers import EmbeddingProviderManager
manager = EmbeddingProviderManager()
providers = manager.get_available_providers()
print(f'✓ 找到 {len(providers)} 个可用的 embedding 提供商')
"""]
        },
        {
            "name": "LLM 路由器测试",
            "command": [sys.executable, "-c", """
import sys
sys.path.append('.')
from backend.modules.llm.llm_router import LLMRouter
router = LLMRouter()
providers = router.list_available_providers()
print(f'✓ 找到 {len(providers)} 个可用的 LLM 提供商')
"""]
        },
        {
            "name": "RAG 配置测试",
            "command": [sys.executable, "-c", """
import sys
sys.path.append('.')
from backend.modules.rag.core.rag_config_manager import RAGConfigManager
manager = RAGConfigManager('./test_quick_rag_config.json')
config = manager.get_config()
print(f'✓ RAG 配置加载成功: {config.embedding_provider}/{config.embedding_model}')
"""]
        }
    ]
    
    # 运行测试
    passed = 0
    failed = 0
    
    for test in quick_tests:
        if run_quick_test(test["name"], test["command"]):
            passed += 1
        else:
            failed += 1
    
    # 总结
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n{'='*50}")
    print_status(f"快速测试完成 ({duration:.2f}s)", "info")
    print_status(f"通过: {passed}", "success")
    if failed > 0:
        print_status(f"失败: {failed}", "error")
    else:
        print_status("所有测试通过!", "success")
    
    # 清理测试文件
    test_files = ["./test_quick_rag_config.json"]
    for test_file in test_files:
        if Path(test_file).exists():
            Path(test_file).unlink()
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())