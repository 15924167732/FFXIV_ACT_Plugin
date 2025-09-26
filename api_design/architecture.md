# FFXIV Combat Data API 架构设计

## 系统架构

```
游戏数据源 → 数据采集层 → 解析引擎 → API服务层 → 您的应用
```

## 组件说明

### 1. 数据采集层 (Data Collection Layer)
- **网络包捕获**: 使用Npcap/Raw Socket
- **内存读取**: 读取游戏内存数据
- **数据缓冲**: 实时数据流缓存

### 2. 解析引擎 (Parsing Engine)
- **技能ID映射**: 将十六进制ID转换为可读名称
- **威力计算**: 实时计算伤害/治疗数值
- **状态效果处理**: DOT/HOT/Buff/Debuff计算
- **多目标处理**: AOE伤害分配计算

### 3. API服务层 (API Service Layer)
- **RESTful API**: 标准HTTP接口
- **WebSocket**: 实时数据推送
- **数据缓存**: Redis缓存热点数据
- **认证授权**: JWT Token认证

### 4. 数据存储 (Data Storage)
- **实时数据**: 内存存储 (Redis)
- **历史数据**: 数据库存储 (PostgreSQL/MongoDB)
- **配置数据**: JSON文件存储

## 技术栈建议

### 后端服务
- **语言**: C# (.NET 6+) / Python (FastAPI) / Node.js
- **框架**: ASP.NET Core / FastAPI / Express.js
- **数据库**: PostgreSQL + Redis
- **消息队列**: RabbitMQ / Apache Kafka

### API设计
- **协议**: HTTP/HTTPS + WebSocket
- **格式**: JSON
- **认证**: JWT Bearer Token
- **文档**: OpenAPI/Swagger

## 部署方案

### 本地部署
```
[游戏客户端] → [数据采集服务] → [API服务] → [您的应用]
```

### 云端部署
```
[游戏客户端] → [本地采集客户端] → [云端API服务] → [Web应用]
```