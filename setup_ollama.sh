#!/bin/bash

# 心语机器人 - Ollama设置脚本
# 自动安装和配置Ollama本地LLM

set -e

echo "🚀 心语机器人 - Ollama设置脚本"
echo "=================================="

# 检查操作系统
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

echo "📋 检测到操作系统: $MACHINE"

# 安装Ollama
install_ollama() {
    echo "📦 安装Ollama..."
    
    if command -v ollama &> /dev/null; then
        echo "✅ Ollama已安装"
        ollama --version
        return
    fi
    
    case $MACHINE in
        Mac)
            if command -v brew &> /dev/null; then
                echo "🍺 使用Homebrew安装Ollama..."
                brew install ollama
            else
                echo "⚠️  请手动安装Ollama: https://ollama.ai/download"
                exit 1
            fi
            ;;
        Linux)
            echo "🐧 在Linux上安装Ollama..."
            curl -fsSL https://ollama.ai/install.sh | sh
            ;;
        *)
            echo "❌ 不支持的操作系统: $MACHINE"
            echo "请手动安装Ollama: https://ollama.ai/download"
            exit 1
            ;;
    esac
}

# 启动Ollama服务
start_ollama() {
    echo "🔄 启动Ollama服务..."
    
    # 检查服务是否已运行
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama服务已运行"
        return
    fi
    
    # 启动服务
    echo "🚀 启动Ollama服务..."
    if [[ "$MACHINE" == "Mac" ]]; then
        # macOS上使用brew services
        if command -v brew &> /dev/null; then
            brew services start ollama
        else
            nohup ollama serve > /dev/null 2>&1 &
        fi
    else
        # Linux上后台启动
        nohup ollama serve > /dev/null 2>&1 &
    fi
    
    # 等待服务启动
    echo "⏳ 等待服务启动..."
    for i in {1..30}; do
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            echo "✅ Ollama服务启动成功"
            return
        fi
        sleep 1
    done
    
    echo "❌ Ollama服务启动失败"
    exit 1
}

# 下载推荐模型
download_models() {
    echo "📥 下载推荐模型..."
    
    # 检查可用内存
    if [[ "$MACHINE" == "Mac" ]]; then
        MEMORY_GB=$(( $(sysctl -n hw.memsize) / 1024 / 1024 / 1024 ))
    else
        MEMORY_GB=$(( $(grep MemTotal /proc/meminfo | awk '{print $2}') / 1024 / 1024 ))
    fi
    
    echo "💾 检测到内存: ${MEMORY_GB}GB"
    
    # 根据内存选择模型
    if [ $MEMORY_GB -ge 16 ]; then
        MODEL="qwen2.5:14b"
        echo "🧠 推荐使用14B模型（内存充足）"
    elif [ $MEMORY_GB -ge 8 ]; then
        MODEL="qwen2.5:8b"
        echo "🧠 推荐使用8B模型（内存适中）"
    else
        MODEL="qwen2.5:7b"
        echo "🧠 推荐使用7B模型（内存较少）"
    fi
    
    # 检查模型是否已存在
    if ollama list | grep -q "$MODEL"; then
        echo "✅ 模型 $MODEL 已存在"
    else
        echo "📥 下载模型 $MODEL（这可能需要几分钟）..."
        ollama pull "$MODEL"
        echo "✅ 模型下载完成"
    fi
    
    # 更新配置文件
    update_config "$MODEL"
}

# 更新配置文件
update_config() {
    local model=$1
    local config_file="config.env"
    
    echo "⚙️  更新配置文件..."
    
    if [ ! -f "$config_file" ]; then
        echo "❌ 配置文件 $config_file 不存在"
        return
    fi
    
    # 备份原配置
    cp "$config_file" "${config_file}.backup.$(date +%Y%m%d_%H%M%S)"
    
    # 更新Ollama配置
    sed -i.tmp "s/^OLLAMA_ENABLED=.*/OLLAMA_ENABLED=true/" "$config_file"
    sed -i.tmp "s/^OLLAMA_MODEL=.*/OLLAMA_MODEL=$model/" "$config_file"
    
    # 注释掉其他API密钥（可选）
    sed -i.tmp "s/^LLM_API_KEY=/#LLM_API_KEY=/" "$config_file"
    sed -i.tmp "s/^DASHSCOPE_API_KEY=/#DASHSCOPE_API_KEY=/" "$config_file"
    sed -i.tmp "s/^OPENAI_API_KEY=/#OPENAI_API_KEY=/" "$config_file"
    
    # 清理临时文件
    rm -f "${config_file}.tmp"
    
    echo "✅ 配置文件已更新"
}

# 测试安装
test_installation() {
    echo "🧪 测试安装..."
    
    # 测试Ollama服务
    if ! curl -s http://localhost:11434/api/tags > /dev/null; then
        echo "❌ Ollama服务测试失败"
        return 1
    fi
    
    # 测试Python集成
    if command -v python3 &> /dev/null; then
        echo "🐍 测试Python集成..."
        if python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from backend.modules.llm.providers.ollama_provider import OllamaProvider
    provider = OllamaProvider({'base_url': 'http://localhost:11434', 'model': 'qwen2.5:8b'})
    print('✅ Python集成测试成功' if provider.is_available() else '❌ Python集成测试失败')
except Exception as e:
    print(f'❌ Python集成测试失败: {e}')
"; then
            echo "✅ 所有测试通过"
        else
            echo "⚠️  Python集成测试失败，但Ollama服务正常"
        fi
    else
        echo "⚠️  未找到Python3，跳过Python集成测试"
    fi
}

# 显示使用说明
show_usage() {
    echo ""
    echo "🎉 Ollama设置完成！"
    echo "=================="
    echo ""
    echo "📋 使用说明:"
    echo "1. 启动心语机器人后端服务"
    echo "2. 系统将自动使用Ollama本地模型"
    echo "3. 享受免费、隐私、快速的AI对话体验"
    echo ""
    echo "🔧 常用命令:"
    echo "  ollama list                    # 查看已下载的模型"
    echo "  ollama run qwen2.5:8b         # 直接与模型对话"
    echo "  ollama pull <model>           # 下载新模型"
    echo "  python test_llm_router.py     # 测试LLM路由器"
    echo ""
    echo "📚 更多信息请查看: OLLAMA_SETUP_GUIDE.md"
}

# 主函数
main() {
    echo "开始设置Ollama..."
    
    install_ollama
    start_ollama
    download_models
    test_installation
    show_usage
    
    echo ""
    echo "✅ 设置完成！现在可以使用本地LLM了。"
}

# 运行主函数
main "$@"