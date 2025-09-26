@echo off
echo ========================================
echo    FFXIV ACT Plugin GitHub 上传脚本
echo ========================================
echo.

REM 检查是否已经初始化Git
if not exist ".git" (
    echo [信息] 初始化Git仓库...
    git init
    echo.
) else (
    echo [信息] Git仓库已存在
    echo.
)

REM 检查Git配置
echo [信息] 检查Git配置...
git config user.name >nul 2>&1
if errorlevel 1 (
    set /p username="请输入您的Git用户名: "
    git config user.name "%username%"
)

git config user.email >nul 2>&1
if errorlevel 1 (
    set /p email="请输入您的Git邮箱: "
    git config user.email "%email%"
)

echo 当前Git配置:
git config user.name
git config user.email
echo.

REM 添加文件
echo [信息] 添加文件到Git...
git add .

REM 提交更改
echo [信息] 提交更改...
git commit -m "🎉 Initial commit: FFXIV Combat Data API

- 完整的FastAPI服务架构
- 实时战斗数据解析引擎  
- WebSocket实时数据推送
- 现代化Web仪表板
- 完整的技能定义数据库
- 批量JSON修复工具
- 详细的文档和使用指南"

REM 检查是否已经设置远程仓库
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo [重要] 请先在GitHub上创建仓库！
    echo.
    echo 步骤:
    echo 1. 访问 https://github.com
    echo 2. 点击右上角 + 号 → New repository  
    echo 3. 仓库名称: FFXIV_ACT_Plugin
    echo 4. 描述: FFXIV战斗数据解析API
    echo 5. 选择 Public 或 Private
    echo 6. 不要勾选任何额外选项
    echo 7. 点击 Create repository
    echo.
    set /p repo_url="请输入GitHub仓库地址(https://github.com/username/FFXIV_ACT_Plugin.git): "
    git remote add origin "%repo_url%"
) else (
    echo [信息] 远程仓库已配置
    git remote -v
    echo.
)

REM 推送到GitHub
echo [信息] 推送到GitHub...
git branch -M main
git push -u origin main

if errorlevel 1 (
    echo.
    echo [错误] 推送失败！可能的原因：
    echo 1. 网络连接问题
    echo 2. 认证失败 - 需要Personal Access Token
    echo 3. 仓库地址错误
    echo.
    echo 解决方案：
    echo 1. 检查网络连接
    echo 2. 设置Personal Access Token:
    echo    - 访问 GitHub Settings → Developer settings → Personal access tokens
    echo    - 生成新token，勾选 repo 权限
    echo    - 使用token作为密码进行推送
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo           上传成功！ 🎉
echo ========================================
echo.
echo 您的项目已成功上传到GitHub!
echo.
echo 接下来可以:
echo 1. 邀请团队成员协作
echo 2. 设置分支保护规则  
echo 3. 创建Issues和Projects
echo 4. 配置GitHub Actions
echo.
echo 详细指南请查看: GitHub上传指南.md
echo.
pause