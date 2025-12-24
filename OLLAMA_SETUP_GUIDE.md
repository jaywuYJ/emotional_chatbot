# Ollama本地LLM设置指南

## 什么是Ollama？

Ollama是一个轻量级、可扩展的框架，用于在本地运行大型语言模型。它支持多种开源模型，包括Llama、Qwen、CodeLlama等。

## 安装Ollama

### macOS
```bash
# 使用Homebrew安装
brew install ollama

# 或者下载安装包
# 访问 https://ollama.ai/download
```

### Linux
```bash
# 使用安装脚本
curl -fsSL https://ollama.ai/install.sh | sh
```

### Windows
访问 https://ollama.ai/download 下载Windows安装包

## 启动Ollama服务

```bash
# 启动Ollama服务（后台运行）
ollama serve
```

服务将在 `http://localhost:11434` 启动

## 下载和使用模型

### 推荐模型

1. **Qwen2.5:8B** (推荐) - 阿里巴巴的中文优化模型
```bash
ollama pull qwen2.5:8b
```

2. **Qwen2.5:14B** - 更大的模型，效果更好但需要更多内存
```bash
ollama pull qwen2.5:14b
```

3. **Llama3.1:8B** - Meta的开源模型
```bash
ollama pull llama3.1:8b
```

### 模型管理命令

```bash
# 列出已下载的模型
ollama list

# 运行模型（交互式）
ollama run qwen2.5:8b

# 删除模型
ollama rm qwen2.5:8b

# 查看模型信息
ollama show qwen2.5:8b
```

## 配置心语机器人使用Ollama

### 1. 更新配置文件

编辑 `config.env` 文件：

```env
# 启用Ollama（优先级最高）
OLLAMA_ENABLED=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:8b
OLLAMA_TEMPERATURE=0.7
OLLAMA_MAX_TOKENS=2000
OLLAMA_PRIORITY=1

# 禁用其他提供商（可选）
# LLM_API_KEY=
# DASHSCOPE_API_KEY=
# OPENAI_API_KEY=
```

### 2. 测试连接

```bash
# 测试Ollama服务是否正常
curl http://localhost:11434/api/tags

# 测试聊天功能
python test_llm_router.py
```

## 性能优化

### 系统要求

- **最小内存**: 8GB RAM (适用于7B模型)
- **推荐内存**: 16GB+ RAM (适用于13B+模型)
- **存储空间**: 每个模型约4-8GB

### 优化建议

1. **选择合适的模型大小**
   - 8B模型：适合大多数对话场景
   - 14B+模型：更好的理解能力，但需要更多资源

2. **调整并发设置**
```bash
# 设置并发数量
export OLLAMA_NUM_PARALLEL=2
```

3. **GPU加速**（如果有NVIDIA GPU）
```bash
# Ollama会自动检测并使用GPU
# 确保安装了CUDA驱动
```

## 故障排除

### 常见问题

1. **连接失败**
```bash
# 检查服务是否运行
ps aux | grep ollama

# 重启服务
pkill ollama
ollama serve
```

2. **模型下载失败**
```bash
# 使用代理下载
export HTTP_PROXY=http://your-proxy:port
export HTTPS_PROXY=http://your-proxy:port
ollama pull qwen2.5:8b
```

3. **内存不足**
```bash
# 使用更小的模型
ollama pull qwen2.5:7b

# 或者调整模型参数
ollama run qwen2.5:8b --memory 4096
```

### 日志查看

```bash
# 查看Ollama日志
ollama logs

# 或者查看系统日志
journalctl -u ollama
```

## 与其他提供商对比

| 特性 | Ollama | 阿里云通义千问 | OpenAI |
|------|--------|----------------|--------|
| 成本 | 免费 | 按使用付费 | 按使用付费 |
| 隐私 | 完全本地 | 云端处理 | 云端处理 |
| 速度 | 取决于硬件 | 网络延迟 | 网络延迟 |
| 模型选择 | 开源模型 | 通义千问系列 | GPT系列 |
| 离线使用 | 支持 | 不支持 | 不支持 |

## 最佳实践

1. **开发环境**: 使用Ollama进行快速迭代和测试
2. **生产环境**: 配置多个提供商实现故障转移
3. **成本控制**: 本地处理敏感数据，云端处理复杂任务
4. **性能监控**: 定期检查各提供商的响应时间和可用性

## 进阶配置

### 自定义模型

```bash
# 创建自定义模型配置
cat > Modelfile << EOF
FROM qwen2.5:8b
PARAMETER temperature 0.7
PARAMETER top_p 0.9
SYSTEM "你是心语，一个温暖的AI伙伴..."
EOF

# 构建自定义模型
ollama create xinyu -f Modelfile
```

### API调用示例

```python
import requests

response = requests.post('http://localhost:11434/api/chat', 
    json={
        'model': 'qwen2.5:8b',
        'messages': [
            {'role': 'user', 'content': '你好'}
        ]
    }
)
print(response.json())
```

## 支持和社区

- 官方文档: https://ollama.ai/docs
- GitHub: https://github.com/ollama/ollama
- 模型库: https://ollama.ai/library
- 社区论坛: https://github.com/ollama/ollama/discussions