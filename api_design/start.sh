#!/bin/bash

echo "=============================================="
echo "   FFXIV Combat Data API 启动脚本"
echo "=============================================="
echo

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到Python3，请先安装Python 3.8+"
    exit 1
fi

echo "[信息] Python已安装: $(python3 --version)"
echo

# 检查是否在正确目录
if [ ! -f "main.py" ]; then
    echo "[错误] 未找到main.py文件，请确保在正确的目录下运行此脚本"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "[信息] 创建虚拟环境..."
    python3 -m venv venv
    echo "[成功] 虚拟环境创建完成"
fi

# 激活虚拟环境
echo "[信息] 激活虚拟环境..."
source venv/bin/activate

# 检查依赖包
echo "[信息] 检查依赖包..."
if ! pip show fastapi &> /dev/null; then
    echo "[警告] 未安装FastAPI，正在安装依赖包..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[错误] 依赖包安装失败"
        exit 1
    fi
    echo "[成功] 依赖包安装完成"
else
    echo "[信息] 依赖包已安装"
fi

echo
echo "[信息] 启动API服务器..."
echo
echo "服务将在以下地址运行:"
echo "  - API文档: http://localhost:8000/docs"
echo "  - 健康检查: http://localhost:8000/health"
echo "  - 前端示例: 请用浏览器打开 frontend_example.html"
echo
echo "按 Ctrl+C 停止服务"
echo

python main.py