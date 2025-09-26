# 🤝 贡献指南

感谢您对 FFXIV Combat Data API 项目的关注！我们欢迎各种形式的贡献。

## 📋 如何贡献

### 🐛 报告 Bug
1. 检查 [Issues](https://github.com/YOUR_USERNAME/FFXIV_ACT_Plugin/issues) 确认问题尚未被报告
2. 创建新的 Issue，包含以下信息：
   - 清晰的问题描述
   - 复现步骤
   - 预期行为 vs 实际行为
   - 系统环境信息
   - 错误日志（如有）

### ✨ 功能建议
1. 在 Issues 中创建功能请求
2. 详细描述建议的功能
3. 说明使用场景和价值
4. 如有可能，提供实现思路

### 💻 代码贡献

#### 开发环境设置
```bash
# 1. Fork 项目到您的GitHub账户
# 2. 克隆您的Fork
git clone https://github.com/YOUR_USERNAME/FFXIV_ACT_Plugin.git
cd FFXIV_ACT_Plugin

# 3. 添加上游仓库
git remote add upstream https://github.com/ORIGINAL_OWNER/FFXIV_ACT_Plugin.git

# 4. 创建虚拟环境
python -m venv ffxiv_api_env
source ffxiv_api_env/bin/activate  # Linux/Mac
# 或 ffxiv_api_env\Scripts\activate  # Windows

# 5. 安装开发依赖
cd api_design
pip install -r requirements.txt
```

#### 开发流程
1. **创建功能分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **进行开发**
   - 编写代码
   - 添加测试
   - 更新文档

3. **运行测试**
   ```bash
   python test_api.py          # API功能测试
   python validate_json.py     # JSON格式验证
   ```

4. **提交更改**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **推送并创建PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   然后在GitHub上创建Pull Request

#### 代码规范
- **Python代码**: 遵循 PEP 8 规范
- **提交信息**: 使用清晰的提交信息
  ```
  feat: 添加新功能
  fix: 修复bug
  docs: 更新文档
  style: 代码格式调整
  refactor: 代码重构
  test: 添加测试
  ```
- **注释**: 重要函数添加中文注释
- **类型提示**: 使用Python类型提示

### 📚 文档贡献
- 修正文档中的错误
- 改进现有文档的清晰度
- 添加更多使用示例
- 翻译文档

### 🎨 前端贡献
- 改进Web界面设计
- 添加新的可视化组件
- 优化用户体验
- 响应式设计改进

## 🏗️ 项目结构

### 核心模块
- `main.py` - FastAPI主服务
- `combat_parser.py` - 数据解析引擎
- `api_models.py` - 数据模型定义
- `data_collector.py` - 数据采集器

### 工具脚本
- `test_api.py` - 功能测试
- `validate_json.py` - JSON验证
- `fix_json_batch.py` - 批量修复工具

### 前端
- `frontend_example.html` - 实时仪表板

## 🧪 测试指南

### 运行测试
```bash
# 完整功能测试
python test_api.py

# JSON格式验证
python validate_json.py

# 启动服务并访问
python main.py
# 访问 http://localhost:8000/docs
```

### 添加测试
为新功能添加相应的测试用例：
```python
def test_new_feature():
    # 测试代码
    assert expected == actual
```

## 📝 文档规范

### API文档
- 所有API端点都要有完整的文档
- 包含请求/响应示例
- 说明参数和返回值

### 代码注释
```python
def parse_combat_event(self, raw_data: Dict) -> Dict:
    """
    解析战斗事件数据
    
    Args:
        raw_data: 原始事件数据字典
        
    Returns:
        Dict: 解析后的事件数据
        
    Raises:
        ValueError: 当数据格式不正确时
    """
```

## 🔍 代码审查

### PR审查标准
- [ ] 代码功能正确
- [ ] 遵循项目代码规范
- [ ] 包含必要的测试
- [ ] 文档更新完整
- [ ] 没有引入新的安全问题

### 审查流程
1. 自动化测试通过
2. 至少一位维护者审查
3. 解决所有审查意见
4. 合并到主分支

## 🚀 发布流程

### 版本号规则
使用语义化版本控制 (SemVer):
- MAJOR: 不兼容的API更改
- MINOR: 向后兼容的功能添加
- PATCH: 向后兼容的bug修复

### 发布检查清单
- [ ] 所有测试通过
- [ ] 文档更新
- [ ] 版本号更新
- [ ] 更新日志完善
- [ ] 标签创建

## 🎯 贡献建议

### 新手友好的任务
- 修复文档中的错别字
- 添加更多使用示例
- 改进错误信息
- 优化用户界面

### 高级任务
- 性能优化
- 新API端点开发
- 数据库集成
- 监控和日志改进

## 💬 社区

### 讨论平台
- GitHub Issues: 技术讨论和问题报告
- Discord: 实时讨论和社区交流
- Wiki: 详细文档和教程

### 行为准则
- 保持友善和专业
- 尊重所有贡献者
- 提供建设性的反馈
- 遵守开源精神

## 📞 联系方式

如有疑问，请通过以下方式联系：
- GitHub Issues
- 项目维护者邮箱
- Discord社区

---

再次感谢您的贡献！🎉