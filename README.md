# 🎮 FFXIV Combat Data API

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)

一个现代化的 Final Fantasy XIV 战斗数据解析API，将 ACT Plugin 功能封装为 RESTful API 服务。

## ✨ 主要特性

- 🔄 **实时数据流**: WebSocket 实时推送战斗事件
- 📊 **完整统计**: DPS、HPS、技能使用率等详细数据
- 🎯 **技能数据库**: 基于官方数据的完整技能定义
- 🌐 **跨平台API**: 支持Web、移动端、桌面应用集成
- 📱 **现代化界面**: 响应式实时仪表板
- 🔧 **易于部署**: 一键启动脚本

## 🚀 快速开始

### 一键启动
```bash
# Windows用户
start.bat

# Linux/Mac用户
chmod +x start.sh && ./start.sh
```

### 手动安装
```bash
# 1. 克隆项目
git clone https://github.com/YOUR_USERNAME/FFXIV_ACT_Plugin.git
cd FFXIV_ACT_Plugin/api_design

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动服务
python main.py
```

### 验证安装
```bash
# 运行完整测试
python test_api.py

# 访问API文档
# http://localhost:8000/docs
```

## 📁 项目结构

```
FFXIV_ACT_Plugin/
├── Definitions/              # 游戏技能定义文件
│   ├── BlackMage.json       # 各职业技能数据
│   ├── WhiteMage.json
│   └── ...
├── Overrides/               # 技能名称覆盖规则
│   ├── global_P10S.txt     # 各副本特定覆盖
│   └── ...
├── api_design/              # API服务核心代码
│   ├── main.py             # FastAPI主服务
│   ├── combat_parser.py    # 战斗数据解析引擎
│   ├── frontend_example.html # 实时仪表板示例
│   ├── test_api.py         # 功能测试脚本
│   └── ...
└── README.md
```

## 🎯 API 接口

### 实时数据
- `GET /api/v1/combat/current` - 当前战斗信息
- `GET /api/v1/combat/live/stats` - 实时DPS统计
- `GET /api/v1/combat/live/events` - 战斗事件流
- `WebSocket /ws/live` - 实时数据推送

### 数据查询
- `GET /api/v1/definitions/jobs` - 职业技能定义
- `GET /api/v1/search/actions?keyword=fire` - 技能搜索
- `GET /api/v1/definitions/zones` - 支持的区域列表

## 💡 使用示例

### Python客户端
```python
import requests
import websocket

# 获取实时DPS
stats = requests.get("http://localhost:8000/api/v1/combat/live/stats").json()
print(f"团队总DPS: {sum(s.get('dps', 0) for s in stats.values())}")

# WebSocket实时监听
ws = websocket.WebSocketApp("ws://localhost:8000/ws/live")
ws.run_forever()
```

### JavaScript集成
```javascript
// 获取实时数据
const stats = await fetch('/api/v1/combat/live/stats').then(r => r.json());

// WebSocket连接
const ws = new WebSocket('ws://localhost:8000/ws/live');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('战斗事件:', data);
};
```

## 🛠️ 开发指南

### 环境设置
```bash
# 创建虚拟环境
python -m venv ffxiv_api_env
source ffxiv_api_env/bin/activate  # Linux/Mac
# 或 ffxiv_api_env\Scripts\activate  # Windows

# 安装开发依赖
pip install -r requirements.txt
```

### 运行测试
```bash
python test_api.py          # 功能测试
python validate_json.py     # JSON格式验证
python fix_json_batch.py    # 批量修复工具
```

### 添加新功能
1. 在 `main.py` 中添加新的API端点
2. 在 `combat_parser.py` 中扩展数据解析逻辑
3. 运行测试确保功能正常

## 🎮 应用场景

- **团队DPS监控**: 实时显示团队成员输出排行
- **Discord机器人**: 自动发送战斗统计到团队频道
- **直播插件**: OBS覆盖层显示实时数据
- **移动应用**: 手机端查看战斗状态
- **数据分析**: 战斗表现分析和优化建议

## 🤝 贡献指南

我们欢迎任何形式的贡献！

### 提交代码
1. Fork 这个仓库
2. 创建功能分支: `git checkout -b feature/amazing-feature`
3. 提交更改: `git commit -m 'Add amazing feature'`
4. 推送分支: `git push origin feature/amazing-feature`
5. 创建 Pull Request

### 报告问题
- 使用 [Issues](https://github.com/YOUR_USERNAME/FFXIV_ACT_Plugin/issues) 报告bug
- 提供详细的错误信息和复现步骤
- 包含系统环境信息

### 改进文档
- 修正错误或不清楚的说明
- 添加更多使用示例
- 翻译文档到其他语言

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## ⚠️ 免责声明

本工具仅供学习和研究使用。Square Enix 不允许使用第三方工具，使用本工具的风险由用户自行承担。请遵守游戏服务条款，不要在游戏内讨论解析数据或用其骚扰其他玩家。

## 🙏 致谢

- [Advanced Combat Tracker](http://advancedcombattracker.com/) - 原始ACT插件
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化API框架
- [Final Fantasy XIV](https://www.finalfantasyxiv.com/) - 游戏本体
- 所有贡献者和用户的支持

## 📞 联系我们

- 项目主页: [GitHub Repository](https://github.com/YOUR_USERNAME/FFXIV_ACT_Plugin)
- 问题反馈: [Issues](https://github.com/YOUR_USERNAME/FFXIV_ACT_Plugin/issues)
- Discord: [加入我们的Discord服务器](#)

---

⭐ 如果这个项目对您有帮助，请给我们一个Star！