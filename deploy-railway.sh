#!/bin/bash
# Railway 部署脚本
echo "🚀 开始部署到 Railway..."

# 安装 Railway CLI (如果尚未安装)
if ! command -v railway &> /dev/null; then
    echo "📦 安装 Railway CLI..."
    npm install -g @railway/cli
fi

# 登录到 Railway
echo "🔐 登录到 Railway..."
railway login

# 创建新项目或连接到现有项目
echo "🏗️ 创建/连接 Railway 项目..."
railway init

# 部署应用
echo "🚀 部署应用到 Railway..."
railway deploy

echo "✅ 部署完成！"
echo "🌐 您的应用现在应该在 Railway 上运行"
echo "💡 使用 'railway status' 检查部署状态"