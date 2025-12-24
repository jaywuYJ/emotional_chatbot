# Emotional Chat 项目 Makefile

.PHONY: help test quick-test unit-test integration-test e2e-test clean setup lint format

# 默认目标
help:
	@echo "可用命令:"
	@echo "  make test          - 运行完整回归测试"
	@echo "  make quick-test    - 运行快速测试（提交前验证）"
	@echo "  make unit-test     - 只运行单元测试"
	@echo "  make integration-test - 只运行集成测试"
	@echo "  make e2e-test      - 只运行端到端测试"
	@echo "  make clean         - 清理测试文件和缓存"
	@echo "  make setup         - 设置开发环境"
	@echo "  make lint          - 代码检查"
	@echo "  make format        - 代码格式化"

# 运行完整回归测试
test:
	@echo "运行完整回归测试..."
	python run_tests.py --verbose

# 运行快速测试
quick-test:
	@echo "运行快速测试..."
	python quick_test.py

# 运行单元测试
unit-test:
	@echo "运行单元测试..."
	python run_tests.py --type unit --verbose

# 运行集成测试
integration-test:
	@echo "运行集成测试..."
	python run_tests.py --type integration --verbose

# 运行端到端测试
e2e-test:
	@echo "运行端到端测试..."
	python run_tests.py --type e2e --verbose

# 跳过外部 API 的测试
test-offline:
	@echo "运行离线测试（跳过外部 API）..."
	python run_tests.py --skip-external-apis --verbose

# 清理测试文件和缓存
clean:
	@echo "清理测试文件和缓存..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache 2>/dev/null || true
	rm -rf test_*.db test_*.json test_*chroma_db* 2>/dev/null || true
	rm -rf ./tests/fixtures/test_* 2>/dev/null || true
	@echo "清理完成"

# 设置开发环境
setup:
	@echo "设置开发环境..."
	pip install -r requirements.txt
	@echo "创建测试目录..."
	mkdir -p tests/{unit,integration,e2e,fixtures}
	@echo "环境设置完成"

# 代码检查（如果安装了 flake8）
lint:
	@echo "运行代码检查..."
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 backend/ --max-line-length=120 --ignore=E501,W503; \
	else \
		echo "flake8 未安装，跳过代码检查"; \
	fi

# 代码格式化（如果安装了 black）
format:
	@echo "格式化代码..."
	@if command -v black >/dev/null 2>&1; then \
		black backend/ --line-length=120; \
	else \
		echo "black 未安装，跳过代码格式化"; \
	fi

# 提交前检查
pre-commit: clean quick-test
	@echo "提交前检查完成"

# 安装开发依赖
install-dev:
	@echo "安装开发依赖..."
	pip install flake8 black pytest pytest-asyncio pytest-cov
	@echo "开发依赖安装完成"