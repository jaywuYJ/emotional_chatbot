#!/usr/bin/env python3
"""
测试Ollama连接
"""

import requests
import sys
import os

def test_ollama_connection():
    """测试Ollama服务连接"""
    print("🔍 测试Ollama连接...")
    
    try:
        # 测试Ollama服务是否运行
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            print(f"✅ Ollama服务正常运行")
            print(f"📋 可用模型数量: {len(models)}")
            
            for model in models:
                name = model.get('name', 'unknown')
                size = model.get('size', 0)
                size_mb = size / (1024 * 1024) if size else 0
                print(f"   - {name} ({size_mb:.1f}MB)")
            
            # 推荐模型检查
            recommended_models = ['qwen2.5:8b', 'qwen2.5:7b', 'qwen2.5:14b']
            available_recommended = [m['name'] for m in models if any(rec in m['name'] for rec in recommended_models)]
            
            if available_recommended:
                print(f"✅ 找到推荐模型: {available_recommended}")
                return True, available_recommended[0]
            else:
                print(f"⚠️  未找到推荐模型，可用模型: {[m['name'] for m in models]}")
                if models:
                    return True, models[0]['name']
                else:
                    print(f"❌ 没有可用模型")
                    return False, None
        else:
            print(f"❌ Ollama服务响应异常: {response.status_code}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print(f"❌ 无法连接到Ollama服务 (http://localhost:11434)")
        print(f"💡 请确保Ollama已启动:")
        print(f"   1. 安装Ollama: brew install ollama")
        print(f"   2. 启动服务: ollama serve")
        print(f"   3. 下载模型: ollama pull qwen2.5:8b")
        return False, None
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        return False, None

def test_simple_chat(model_name):
    """测试简单对话"""
    print(f"\n💬 测试与模型 {model_name} 的对话...")
    
    try:
        data = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": "你是一个友善的AI助手，请用中文简短回答。"},
                {"role": "user", "content": "你好，请用一句话介绍自己。"}
            ],
            "stream": False
        }
        
        response = requests.post("http://localhost:11434/api/chat", json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('message', {}).get('content', '')
            print(f"👤 用户: 你好，请用一句话介绍自己。")
            print(f"🤖 AI: {content}")
            print(f"✅ 对话测试成功")
            return True
        else:
            print(f"❌ 对话测试失败: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 对话测试异常: {e}")
        return False

def main():
    print("🚀 Ollama连接测试")
    print("=" * 50)
    
    # 测试连接
    is_connected, model_name = test_ollama_connection()
    
    if is_connected and model_name:
        # 测试对话
        chat_success = test_simple_chat(model_name)
        
        if chat_success:
            print(f"\n🎉 Ollama测试完全成功！")
            print(f"📝 建议配置:")
            print(f"   OLLAMA_ENABLED=true")
            print(f"   OLLAMA_MODEL={model_name}")
            print(f"   OLLAMA_BASE_URL=http://localhost:11434")
        else:
            print(f"\n⚠️  Ollama服务可用，但对话测试失败")
    else:
        print(f"\n❌ Ollama不可用，请按照上述提示进行安装和配置")
        print(f"\n🔧 快速设置命令:")
        print(f"   brew install ollama")
        print(f"   ollama serve &")
        print(f"   ollama pull qwen2.5:8b")

if __name__ == "__main__":
    main()