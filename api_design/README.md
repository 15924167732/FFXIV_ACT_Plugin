# 🗡️ FFXIV Combat Data API

将 FFXIV ACT Plugin 的战斗数据解析功能封装为现代化的 REST API 服务。

## ⚡ 30秒快速开始

### 🎯 一键启动

**Windows用户:**
```bash
# 双击运行
start.bat
```

**Linux/Mac用户:**
```bash
# 运行启动脚本
chmod +x start.sh
./start.sh
```

**手动启动:**
```bash
pip install -r requirements.txt
python main.py
```

### ✅ 验证功能
```bash
# 运行完整测试
python test_api.py
```

### 🎮 查看效果
- **API文档**: http://localhost:8000/docs  
- **实时面板**: 打开 `frontend_example.html`
- **健康检查**: http://localhost:8000/health

## 🚀 详细安装

### 环境要求
- Python 3.8+
- FastAPI
- uvicorn
- websockets

### 安装依赖
```bash
pip install fastapi uvicorn websockets python-multipart
```

### 启动服务
```bash
# 开发环境
python main.py

# 生产环境
uvicorn main:app --host 0.0.0.0 --port 8000
```

服务启动后访问：
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

## 📡 API 接口
 
### 实时数据接口

#### 获取当前战斗信息
```http
GET /api/v1/combat/current
```

#### 获取实时统计数据
```http
GET /api/v1/combat/live/stats?combatant_id=player_001
```

#### 获取最近事件
```http
GET /api/v1/combat/live/events?type=damage&limit=50
```

### 配置和元数据接口

#### 获取职业定义
```http
GET /api/v1/definitions/jobs
GET /api/v1/definitions/jobs/black_mage
```

#### 获取技能信息
```http
GET /api/v1/definitions/actions/8D
```

#### 搜索技能
```http
GET /api/v1/search/actions?keyword=fire
```

### WebSocket 实时推送
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/live');
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('实时事件:', data);
};
```

## 🔧 使用示例

### Python 客户端
```python
import requests
import websocket
import json

# 1. 获取当前战斗数据
response = requests.get("http://localhost:8000/api/v1/combat/current")
current_fight = response.json()
print(f"当前战斗: {current_fight}")

# 2. 获取实时DPS统计
response = requests.get("http://localhost:8000/api/v1/combat/live/stats")
live_stats = response.json()
print(f"实时统计: {live_stats}")

# 3. 获取技能信息
response = requests.get("http://localhost:8000/api/v1/definitions/actions/8D")
action_info = response.json()
print(f"Fire技能信息: {action_info}")

# 4. WebSocket 实时监听
def on_message(ws, message):
    data = json.loads(message)
    if data.get('type') == 'damage':
        print(f"{data['source_name']} 对 {data['target_name']} 造成 {data['damage']} 伤害")

ws = websocket.WebSocketApp("ws://localhost:8000/ws/live")
ws.on_message = on_message
ws.run_forever()
```

### JavaScript 客户端
```javascript
// 获取实时统计
async function getLiveStats() {
    const response = await fetch('/api/v1/combat/live/stats');
    const stats = await response.json();
    return stats;
}

// WebSocket 连接
const ws = new WebSocket('ws://localhost:8000/ws/live');
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    if (data.type === 'damage') {
        updateDamageChart(data);
    } else if (data.type === 'heal') {
        updateHealChart(data);
    }
};

// 搜索技能
async function searchActions(keyword) {
    const response = await fetch(`/api/v1/search/actions?keyword=${keyword}`);
    const actions = await response.json();
    return actions;
}
```

### React Hook 示例
```jsx
import { useState, useEffect } from 'react';

function useLiveCombatData() {
    const [stats, setStats] = useState({});
    const [events, setEvents] = useState([]);
    
    useEffect(() => {
        const ws = new WebSocket('ws://localhost:8000/ws/live');
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setEvents(prev => [data, ...prev.slice(0, 99)]);
        };
        
        // 定期获取统计数据
        const interval = setInterval(async () => {
            const response = await fetch('/api/v1/combat/live/stats');
            const newStats = await response.json();
            setStats(newStats);
        }, 1000);
        
        return () => {
            ws.close();
            clearInterval(interval);
        };
    }, []);
    
    return { stats, events };
}

function CombatDashboard() {
    const { stats, events } = useLiveCombatData();
    
    return (
        <div>
            <h2>实时战斗统计</h2>
            {Object.entries(stats).map(([playerId, playerStats]) => (
                <div key={playerId}>
                    <h3>{playerId}</h3>
                    <p>DPS: {playerStats.dps?.toFixed(2)}</p>
                    <p>总伤害: {playerStats.total_damage}</p>
                </div>
            ))}
            
            <h2>最近事件</h2>
            {events.slice(0, 10).map((event, index) => (
                <div key={index}>
                    {event.type === 'damage' && (
                        <p>{event.source_name} → {event.target_name}: {event.damage} 伤害</p>
                    )}
                </div>
            ))}
        </div>
    );
}
```

## 🧪 测试数据注入

API 提供了测试接口用于模拟战斗数据：

```python
import requests

# 注入伤害事件
damage_data = {
    'source_id': 'player_001',
    'source_name': 'Test Player',
    'target_id': 'enemy_001',
    'target_name': 'Training Dummy',
    'action_id': '8D',  # Fire
    'damage': 1200,
    'is_critical': True
}

response = requests.post(
    "http://localhost:8000/api/v1/inject/damage",
    json=damage_data
)
print(response.json())

# 注入治疗事件
heal_data = {
    'source_id': 'healer_001',
    'source_name': 'Test Healer',
    'target_id': 'player_001',
    'target_name': 'Test Player',
    'action_id': '5edc',  # Diagnosis
    'heal_amount': 800,
    'overheal_amount': 200
}

response = requests.post(
    "http://localhost:8000/api/v1/inject/heal",
    json=heal_data
)
print(response.json())
```

## 🏗️ 架构说明

### 数据流
```
游戏数据 → 数据采集 → 解析引擎 → API服务 → 您的应用
```

### 核心组件
1. **CombatParser**: 战斗数据解析引擎
2. **FastAPI App**: REST API 服务
3. **WebSocket**: 实时数据推送
4. **Definition Loader**: 技能定义加载器

### 扩展建议
- 添加 Redis 缓存提升性能
- 集成数据库存储历史数据
- 添加用户认证和权限控制
- 实现数据聚合和分析功能

## ⚠️ 注意事项

1. **合规使用**: 遵守 SE 官方政策，不要在游戏内讨论数据
2. **性能考虑**: 实时数据量大时考虑数据采样
3. **安全性**: 生产环境需要添加认证授权
4. **稳定性**: 处理网络中断和异常情况

## 📊 集成到您的项目

这个 API 可以轻松集成到各种类型的项目中：

- **Web应用**: React/Vue/Angular 前端
- **移动应用**: React Native/Flutter
- **桌面应用**: Electron/Tauri
- **数据分析**: Jupyter Notebook/BI工具
- **Discord Bot**: 团队战斗统计机器人
- **OBS插件**: 直播覆盖层显示DPS数据