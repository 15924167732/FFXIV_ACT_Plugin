# 📚 GitHub 上传和团队协作完整指南

## 🚀 第一步：创建GitHub仓库

### 1.1 在GitHub上创建新仓库
1. 登录 [GitHub.com](https://github.com)
2. 点击右上角的 "+" → "New repository"
3. 填写仓库信息：
   - **Repository name**: `FFXIV_ACT_Plugin`
   - **Description**: `FFXIV战斗数据解析API - 将ACT Plugin功能封装为现代化REST API`
   - **Visibility**: `Public` (或 `Private` 如果需要私有)
   - **不要勾选** "Add a README file" (我们已经有了)
   - **不要勾选** "Add .gitignore" (我们已经创建了)
   - **License**: 选择 `MIT License`
4. 点击 "Create repository"

### 1.2 记录仓库地址
创建后会得到类似这样的地址：
```
https://github.com/YOUR_USERNAME/FFXIV_ACT_Plugin.git

```
https://github.com/15924167732/FFXIV_ACT_Plugin
## 💻 第二步：本地Git初始化和上传

### 2.1 在项目根目录打开PowerShell
```powershell
# 进入项目目录
cd e:\code\myact\FFXIV_ACT_Plugin
```

### 2.2 初始化Git仓库
```powershell
# 初始化Git仓库
git init

# 配置用户信息（如果还没配置过）
git config user.name "Your Name"
git config user.email "your.email@example.com"

# 或者全局配置
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 2.3 添加文件和提交
```powershell
# 添加所有文件到暂存区
git add .

# 查看文件状态
git status

# 提交文件
git commit -m "🎉 Initial commit: FFXIV Combat Data API

- 完整的FastAPI服务架构
- 实时战斗数据解析引擎  
- WebSocket实时数据推送
- 现代化Web仪表板
- 完整的技能定义数据库
- 批量JSON修复工具
- 详细的文档和使用指南"
```

### 2.4 连接远程仓库并推送
```powershell
# 添加远程仓库（替换为您的仓库地址）
git remote add origin https://github.com/YOUR_USERNAME/FFXIV_ACT_Plugin.git
https://github.com/15924167732/FFXIV_ACT_Plugin

# 推送到GitHub
git push -u origin main

# 如果出现分支名问题，可能需要：
git branch -M main
git push -u origin main
```

## 👥 第三步：设置团队协作

### 3.1 邀请团队成员
1. 在GitHub仓库页面，点击 "Settings"
2. 左侧菜单选择 "Collaborators"
3. 点击 "Add people"
4. 输入团队成员的GitHub用户名或邮箱
5. 选择权限级别：
   - **Read**: 只能查看代码
   - **Triage**: 可以管理Issues和PR
   - **Write**: 可以直接推送代码
   - **Maintain**: 管理仓库设置
   - **Admin**: 完整管理权限

### 3.2 设置分支保护规则
1. 在仓库 Settings → Branches
2. 点击 "Add rule"
3. 配置保护规则：
   - **Branch name pattern**: `main`
   - ✅ **Require a pull request before merging**
   - ✅ **Require approvals** (至少1个)
   - ✅ **Require status checks to pass**
   - ✅ **Require branches to be up to date**

### 3.3 创建开发分支
```powershell
# 创建开发分支
git checkout -b develop
git push -u origin develop

# 创建功能分支示例
git checkout -b feature/new-api-endpoint
git push -u origin feature/new-api-endpoint
```

## 🛠️ 第四步：团队开发工作流

### 4.1 团队成员克隆项目
```powershell
# 克隆项目
git clone https://github.com/YOUR_USERNAME/FFXIV_ACT_Plugin.git
cd FFXIV_ACT_Plugin

# 查看所有分支
git branch -a

# 切换到开发分支
git checkout develop
```

### 4.2 功能开发流程
```powershell
# 1. 更新本地代码
git checkout develop
git pull origin develop

# 2. 创建功能分支
git checkout -b feature/your-feature-name

# 3. 进行开发
# ... 编写代码 ...

# 4. 提交更改
git add .
git commit -m "feat: 添加新功能描述"

# 5. 推送分支
git push origin feature/your-feature-name

# 6. 在GitHub上创建Pull Request
```

### 4.3 Pull Request 流程
1. 在GitHub仓库页面点击 "Compare & pull request"
2. 填写PR信息：
   - **Title**: 简洁描述更改内容
   - **Description**: 详细说明更改和原因
   - **Reviewers**: 指定代码审查者
   - **Labels**: 添加相关标签
3. 点击 "Create pull request"
4. 等待代码审查和合并

## 📊 第五步：项目管理设置

### 5.1 创建Issues模板
在仓库根目录创建 `.github/ISSUE_TEMPLATE/` 文件夹：

**Bug报告模板** (`.github/ISSUE_TEMPLATE/bug_report.md`):
```markdown
---
name: Bug报告
about: 报告项目中的问题
title: '[BUG] '
labels: bug
assignees: ''
---

## 🐛 Bug描述
简洁清晰地描述发现的问题。

## 🔄 复现步骤
1. 进入 '...'
2. 点击 '....'
3. 滚动到 '....'
4. 看到错误

## ✅ 预期行为
描述预期应该发生什么。

## 📱 环境信息
- OS: [例如 Windows 11]
- Python版本: [例如 3.9.0]
- 浏览器: [例如 Chrome, Safari]

## 📝 额外信息
添加任何其他上下文信息。
```

### 5.2 设置GitHub Actions (CI/CD)
创建 `.github/workflows/ci.yml`:
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        cd api_design
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        cd api_design
        python test_api.py
    
    - name: Validate JSON files
      run: |
        cd api_design
        python validate_json.py
```

### 5.3 创建项目看板
1. 在仓库页面点击 "Projects"
2. 点击 "Create a project"
3. 选择 "Board" 模板
4. 添加列：
   - **📋 Backlog**: 待处理任务
   - **🔄 In Progress**: 进行中
   - **👀 Review**: 代码审查
   - **✅ Done**: 完成

## 🔒 第六步：安全和权限管理

### 6.1 设置Secrets（如果需要）
1. Settings → Secrets and variables → Actions
2. 添加必要的密钥（如API密钥、数据库连接等）

### 6.2 代码扫描设置
1. Security → Code scanning alerts
2. 启用GitHub的自动扫描功能

## 📚 第七步：文档和Wiki设置

### 7.1 启用Wiki
1. Settings → Features → Wikis ✅
2. 创建项目Wiki页面

### 7.2 设置GitHub Pages（如果需要）
1. Settings → Pages
2. 选择源分支和文件夹
3. 可以用来托管项目文档网站

## 🎯 团队协作最佳实践

### 代码提交规范
```bash
# 提交信息格式
<type>(<scope>): <subject>

# 示例
feat(api): 添加实时DPS统计接口
fix(parser): 修复JSON解析错误
docs(readme): 更新安装说明
style(frontend): 优化界面样式
```

### 分支命名规范
- `main` - 主分支（生产环境）
- `develop` - 开发分支
- `feature/功能名` - 功能分支
- `bugfix/bug描述` - Bug修复分支
- `hotfix/紧急修复` - 热修复分支

### 代码审查检查清单
- [ ] 代码功能正确实现
- [ ] 遵循项目代码规范
- [ ] 包含必要的测试
- [ ] 文档更新完整
- [ ] 没有安全漏洞
- [ ] 性能影响可接受

## 🚨 常见问题解决

### 认证问题
```powershell
# 如果推送时要求认证，配置Personal Access Token
git remote set-url origin https://YOUR_TOKEN@github.com/YOUR_USERNAME/FFXIV_ACT_Plugin.git
```

### 合并冲突解决
```powershell
# 拉取最新代码
git pull origin main

# 解决冲突后
git add .
git commit -m "resolve merge conflicts"
git push
```

### 回滚更改
```powershell
# 回滚到指定提交
git reset --hard COMMIT_HASH
git push --force-with-lease
```

现在您就可以成功将项目上传到GitHub并设置团队协作了！🎉

## 📞 需要帮助？

如果在上传过程中遇到任何问题，请参考：
1. [GitHub官方文档](https://docs.github.com/)
2. [Git官方教程](https://git-scm.com/docs)
3. 项目的Issues页面寻求帮助