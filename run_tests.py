#!/usr/bin/env python3
"""
回归测试脚本
运行所有测试以确保功能没有被破坏
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path
from typing import List, Dict, Any
import argparse

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_colored(text: str, color: str = Colors.WHITE):
    """打印彩色文本"""
    print(f"{color}{text}{Colors.END}")

def print_header(text: str):
    """打印标题"""
    print_colored(f"\n{'='*60}", Colors.CYAN)
    print_colored(f"{text:^60}", Colors.CYAN + Colors.BOLD)
    print_colored(f"{'='*60}", Colors.CYAN)

def print_success(text: str):
    """打印成功信息"""
    print_colored(f"✅ {text}", Colors.GREEN)

def print_error(text: str):
    """打印错误信息"""
    print_colored(f"❌ {text}", Colors.RED)

def print_warning(text: str):
    """打印警告信息"""
    print_colored(f"⚠️  {text}", Colors.YELLOW)

def print_info(text: str):
    """打印信息"""
    print_colored(f"ℹ️  {text}", Colors.BLUE)

class TestRunner:
    """测试运行器"""
    
    def __init__(self, skip_external_apis: bool = False, verbose: bool = False):
        self.skip_external_apis = skip_external_apis
        self.verbose = verbose
        self.results = {
            "unit": [],
            "integration": [],
            "e2e": [],
            "total_passed": 0,
            "total_failed": 0,
            "total_skipped": 0,
            "start_time": time.time(),
            "end_time": None
        }
        
        # 设置环境变量
        if skip_external_apis:
            os.environ["SKIP_EXTERNAL_APIS"] = "true"
    
    def run_python_test(self, test_file: Path, test_type: str = "unit") -> Dict[str, Any]:
        """运行单个 Python 测试文件"""
        print_info(f"运行测试: {test_file.name}")
        
        start_time = time.time()
        try:
            # 运行测试
            result = subprocess.run(
                [sys.executable, str(test_file)],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=Path.cwd()
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            test_result = {
                "name": test_file.name,
                "type": test_type,
                "passed": result.returncode == 0,
                "duration": duration,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
            
            if result.returncode == 0:
                print_success(f"{test_file.name} - 通过 ({duration:.2f}s)")
                self.results["total_passed"] += 1
            else:
                print_error(f"{test_file.name} - 失败 ({duration:.2f}s)")
                self.results["total_failed"] += 1
                if self.verbose:
                    print_colored(f"STDOUT:\n{result.stdout}", Colors.YELLOW)
                    print_colored(f"STDERR:\n{result.stderr}", Colors.RED)
            
            return test_result
            
        except subprocess.TimeoutExpired:
            print_error(f"{test_file.name} - 超时")
            self.results["total_failed"] += 1
            return {
                "name": test_file.name,
                "type": test_type,
                "passed": False,
                "duration": 60,
                "stdout": "",
                "stderr": "Test timeout",
                "return_code": -1
            }
        except Exception as e:
            print_error(f"{test_file.name} - 异常: {e}")
            self.results["total_failed"] += 1
            return {
                "name": test_file.name,
                "type": test_type,
                "passed": False,
                "duration": 0,
                "stdout": "",
                "stderr": str(e),
                "return_code": -1
            }
    
    def run_unit_tests(self) -> None:
        """运行单元测试"""
        print_header("运行单元测试")
        
        unit_test_dir = Path("tests/unit")
        if not unit_test_dir.exists():
            print_warning("单元测试目录不存在")
            return
        
        test_files = list(unit_test_dir.glob("test_*.py"))
        if not test_files:
            print_warning("没有找到单元测试文件")
            return
        
        print_info(f"找到 {len(test_files)} 个单元测试文件")
        
        for test_file in test_files:
            result = self.run_python_test(test_file, "unit")
            self.results["unit"].append(result)
    
    def run_integration_tests(self) -> None:
        """运行集成测试"""
        print_header("运行集成测试")
        
        integration_test_dir = Path("tests/integration")
        if not integration_test_dir.exists():
            print_warning("集成测试目录不存在")
            return
        
        test_files = list(integration_test_dir.glob("test_*.py"))
        if not test_files:
            print_warning("没有找到集成测试文件")
            return
        
        print_info(f"找到 {len(test_files)} 个集成测试文件")
        
        for test_file in test_files:
            result = self.run_python_test(test_file, "integration")
            self.results["integration"].append(result)
    
    def run_e2e_tests(self) -> None:
        """运行端到端测试"""
        print_header("运行端到端测试")
        
        e2e_test_dir = Path("tests/e2e")
        if not e2e_test_dir.exists():
            print_warning("端到端测试目录不存在")
            return
        
        # 检查 HTML 测试文件
        html_files = list(e2e_test_dir.glob("test_*.html"))
        if html_files:
            print_info(f"找到 {len(html_files)} 个 HTML 测试文件")
            print_warning("HTML 测试需要手动在浏览器中运行")
            for html_file in html_files:
                print_info(f"  - {html_file.name}")
        
        # 运行 Python E2E 测试
        py_files = list(e2e_test_dir.glob("test_*.py"))
        if py_files:
            print_info(f"找到 {len(py_files)} 个 Python E2E 测试文件")
            for test_file in py_files:
                result = self.run_python_test(test_file, "e2e")
                self.results["e2e"].append(result)
    
    def check_environment(self) -> bool:
        """检查测试环境"""
        print_header("检查测试环境")
        
        checks = []
        
        # 检查 Python 版本
        python_version = sys.version_info
        if python_version >= (3, 8):
            print_success(f"Python 版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
            checks.append(True)
        else:
            print_error(f"Python 版本过低: {python_version.major}.{python_version.minor}.{python_version.micro}")
            checks.append(False)
        
        # 检查必要的包
        required_packages = [
            "fastapi", "uvicorn", "sqlalchemy", "pydantic", 
            "langchain", "chromadb", "openai"
        ]
        
        for package in required_packages:
            try:
                __import__(package)
                print_success(f"包 {package} 已安装")
                checks.append(True)
            except ImportError:
                print_error(f"包 {package} 未安装")
                checks.append(False)
        
        # 检查配置文件
        config_files = ["config.env", "config.py"]
        for config_file in config_files:
            if Path(config_file).exists():
                print_success(f"配置文件 {config_file} 存在")
                checks.append(True)
            else:
                print_warning(f"配置文件 {config_file} 不存在")
                checks.append(False)
        
        # 检查数据库连接
        try:
            from backend.database import get_db
            print_success("数据库连接正常")
            checks.append(True)
        except Exception as e:
            print_error(f"数据库连接失败: {e}")
            checks.append(False)
        
        return all(checks)
    
    def generate_report(self) -> None:
        """生成测试报告"""
        self.results["end_time"] = time.time()
        total_duration = self.results["end_time"] - self.results["start_time"]
        
        print_header("测试报告")
        
        # 总体统计
        total_tests = self.results["total_passed"] + self.results["total_failed"]
        print_info(f"总测试数: {total_tests}")
        print_success(f"通过: {self.results['total_passed']}")
        print_error(f"失败: {self.results['total_failed']}")
        print_info(f"总耗时: {total_duration:.2f}秒")
        
        # 详细报告
        for test_type in ["unit", "integration", "e2e"]:
            tests = self.results[test_type]
            if tests:
                print_colored(f"\n{test_type.upper()} 测试:", Colors.PURPLE + Colors.BOLD)
                for test in tests:
                    status = "✅" if test["passed"] else "❌"
                    print(f"  {status} {test['name']} ({test['duration']:.2f}s)")
        
        # 保存 JSON 报告
        report_file = Path("test_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print_info(f"详细报告已保存到: {report_file}")
        
        # 返回退出码
        return 0 if self.results["total_failed"] == 0 else 1
    
    def run_all_tests(self) -> int:
        """运行所有测试"""
        print_header("开始回归测试")
        
        # 检查环境
        if not self.check_environment():
            print_error("环境检查失败，部分测试可能无法正常运行")
        
        # 运行测试
        self.run_unit_tests()
        self.run_integration_tests()
        self.run_e2e_tests()
        
        # 生成报告
        return self.generate_report()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="回归测试脚本")
    parser.add_argument("--skip-external-apis", action="store_true", 
                       help="跳过需要外部 API 的测试")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="显示详细输出")
    parser.add_argument("--type", choices=["unit", "integration", "e2e", "all"], 
                       default="all", help="运行特定类型的测试")
    
    args = parser.parse_args()
    
    runner = TestRunner(
        skip_external_apis=args.skip_external_apis,
        verbose=args.verbose
    )
    
    if args.type == "unit":
        runner.run_unit_tests()
    elif args.type == "integration":
        runner.run_integration_tests()
    elif args.type == "e2e":
        runner.run_e2e_tests()
    else:
        exit_code = runner.run_all_tests()
        sys.exit(exit_code)


if __name__ == "__main__":
    main()