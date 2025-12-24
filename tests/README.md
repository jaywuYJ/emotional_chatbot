# 测试系统说明

## 目录结构

```
tests/
├── unit/           # 单元测试
├── integration/    # 集成测试
├── e2e/           # 端到端测试
├── fixtures/      # 测试数据和配置
└── README.md      # 本文档
```

## 测试类型

### 单元测试 (Unit Tests)
- 测试单个模块或函数的功能
- 不依赖外部服务
- 运行速度快
- 位置: `tests/unit/`

### 集成测试 (Integration Tests)
- 测试多个模块之间的交互
- 可能需要数据库或外部 API
- 运行时间较长
- 位置: `tests/integration/`

### 端到端测试 (E2E Tests)
- 测试完整的用户流程
- 包括前端和后端交互
- 位置: `tests/e2e/`

## 运行测试

### 快速测试（推荐用于提交前验证）
```bash
# 运行快速测试
python quick_test.py

# 或使用 make 命令
make quick-test
```

### 完整回归测试
```bash
# 运行所有测试
python run_tests.py

# 或使用 make 命令
make test
```

### 运行特定类型的测试
```bash
# 只运行单元测试
make unit-test

# 只运行集成测试
make integration-test

# 只运行端到端测试
make e2e-test
```

### 离线测试（跳过外部 API）
```bash
# 跳过需要外部 API 的测试
make test-offline
```

## 测试配置

### 环境变量
- `SKIP_EXTERNAL_APIS=true` - 跳过外部 API 测试
- `TEST_TIMEOUT=30` - 测试超时时间（秒）

### 测试数据
测试数据和配置文件存放在 `tests/fixtures/` 目录下。

## 添加新测试

### 单元测试
1. 在 `tests/unit/` 目录下创建 `test_*.py` 文件
2. 测试文件应该可以独立运行
3. 使用标准的 Python 测试模式

### 集成测试
1. 在 `tests/integration/` 目录下创建 `test_*.py` 文件
2. 可以依赖数据库和外部服务
3. 确保测试可以重复运行

### 端到端测试
1. Python 测试放在 `tests/e2e/test_*.py`
2. HTML 测试放在 `tests/e2e/test_*.html`
3. 测试完整的用户场景

## 测试最佳实践

1. **测试命名**: 使用描述性的测试名称
2. **测试隔离**: 每个测试应该独立运行
3. **清理资源**: 测试后清理临时文件和数据
4. **错误处理**: 测试异常情况和边界条件
5. **文档**: 为复杂测试添加注释说明

## 持续集成

在提交代码前，建议运行：
```bash
make pre-commit
```

这会执行：
1. 清理临时文件
2. 运行快速测试
3. 确保核心功能正常

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查 `config.env` 中的数据库配置
   - 确保数据库服务正在运行

2. **外部 API 测试失败**
   - 检查 API 密钥是否正确
   - 使用 `--skip-external-apis` 跳过这些测试

3. **导入错误**
   - 确保在项目根目录运行测试
   - 检查 Python 路径设置

4. **权限错误**
   - 确保有写入测试目录的权限
   - 检查临时文件的权限设置

### 调试测试

使用 `--verbose` 参数查看详细输出：
```bash
python run_tests.py --verbose
```

查看测试报告：
```bash
cat test_report.json
```