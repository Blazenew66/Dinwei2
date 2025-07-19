#!/usr/bin/env python3
"""
AI副业方向推荐工具 - 启动脚本
"""

import os
import sys
import subprocess
import argparse

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import streamlit
        import requests
        print("✅ 依赖检查通过")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def check_api_key():
    """检查API密钥是否配置"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("⚠️  警告: 未设置DEEPSEEK_API_KEY环境变量")
        print("请设置环境变量或创建.env文件")
        return False
    return True

def run_app(version="enhanced", port=8501):
    """运行应用"""
    if version == "basic":
        app_file = "app.py"
    else:
        app_file = "app_enhanced.py"
    
    if not os.path.exists(app_file):
        print(f"❌ 应用文件 {app_file} 不存在")
        return False
    
    print(f"🚀 启动 {version} 版本...")
    print(f"📱 应用将在 http://localhost:{port} 运行")
    print("按 Ctrl+C 停止应用")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            app_file, "--server.port", str(port)
        ])
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False
    
    return True

def main():
    parser = argparse.ArgumentParser(description="AI副业方向推荐工具")
    parser.add_argument(
        "--version", 
        choices=["basic", "enhanced"], 
        default="enhanced",
        help="选择应用版本 (默认: enhanced)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8501,
        help="端口号 (默认: 8501)"
    )
    parser.add_argument(
        "--check-only", 
        action="store_true",
        help="仅检查环境，不启动应用"
    )
    
    args = parser.parse_args()
    
    print("🚀 AI副业方向推荐工具")
    print("=" * 40)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 检查API密钥
    if not check_api_key():
        print("💡 提示: 可以在运行时设置API密钥")
    
    if args.check_only:
        print("✅ 环境检查完成")
        return
    
    # 运行应用
    run_app(args.version, args.port)

if __name__ == "__main__":
    main() 