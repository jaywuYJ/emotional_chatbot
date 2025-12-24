#!/usr/bin/env python3
"""
测试包初始化文件
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 测试配置
TEST_CONFIG = {
    "test_db_path": "./tests/fixtures/test.db",
    "test_chroma_path": "./tests/fixtures/test_chroma_db",
    "test_config_path": "./tests/fixtures/test_config.json",
    "skip_external_apis": os.getenv("SKIP_EXTERNAL_APIS", "false").lower() == "true",
    "test_timeout": 30,
}