"""
FFXIV Combat Data API Server
基于 FastAPI 实现的实时战斗数据API服务
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import asyncio
import json
import logging
from datetime import datetime, timedelta
import uvicorn

from combat_parser import FFXIVCombatParser
from api_models import *

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="FFXIV Combat Data API",
    description="Final Fantasy XIV 实时战斗数据解析API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量
combat_parser: Optional[FFXIVCombatParser] = None
websocket_connections: List[WebSocket] = []
current_encounter_data = None

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    global combat_parser
    try:
        # 初始化战斗数据解析器
        import os
        
        # 获取项目根目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        
        definitions_path = os.path.join(project_root, "Definitions")
        overrides_path = os.path.join(project_root, "Overrides")
        
        # 检查路径是否存在
        if not os.path.exists(definitions_path):
            logger.warning(f"Definitions 目录不存在: {definitions_path}")
            logger.info("创建示例 Definitions 目录...")
            os.makedirs(definitions_path, exist_ok=True)
            
        if not os.path.exists(overrides_path):
            logger.warning(f"Overrides 目录不存在: {overrides_path}")
            logger.info("创建示例 Overrides 目录...")
            os.makedirs(overrides_path, exist_ok=True)
        
        combat_parser = FFXIVCombatParser(
            definitions_path=definitions_path,
            overrides_path=overrides_path
        )
        logger.info("FFXIV Combat Parser 初始化成功")
        
        # 启动数据采集任务（模拟）
        asyncio.create_task(simulate_combat_data())
        
    except Exception as e:
        logger.error(f"应用启动失败: {e}")

# ==================== 实时数据接口 ====================

@app.get("/api/v1/combat/current", response_model=Optional[EncounterSummary])
async def get_current_encounter():
    """获取当前进行中的战斗信息"""
    try:
        if not combat_parser:
            raise HTTPException(status_code=503, detail="Combat parser not ready")
        
        summary = combat_parser.get_combat_summary()
        if not summary:
            return None
            
        # 转换为EncounterSummary格式
        encounter = EncounterSummary(
            encounter_id=f"encounter_{int(datetime.now().timestamp())}",
            zone_name="测试区域",
            boss_name="训练木人",
            start_time=summary.get('start_time', datetime.now()),
            end_time=summary.get('end_time'),
            duration=(summary.get('end_time', datetime.now()) - summary.get('start_time', datetime.now())).total_seconds(),
            is_success=True,
            total_dps=summary.get('total_damage', 0) / max(1, summary.get('duration', 1)),
            total_hps=summary.get('total_healing', 0) / max(1, summary.get('duration', 1)),
            combatants=[]
        )
        
        return encounter
        
    except Exception as e:
        logger.error(f"获取当前战斗失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/combat/live/stats")
async def get_live_stats(combatant_id: Optional[str] = None):
    """获取实时战斗统计"""
    try:
        if not combat_parser:
            raise HTTPException(status_code=503, detail="Combat parser not ready")
        
        if combatant_id:
            # 获取指定战斗者的统计
            stats = combat_parser.calculate_dps_stats(combatant_id)
            return stats
        else:
            # 获取所有战斗者的统计
            summary = combat_parser.get_combat_summary()
            return summary.get('participant_stats', {})
            
    except Exception as e:
        logger.error(f"获取实时统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/combat/live/events")
async def get_recent_events(
    event_type: Optional[str] = None,
    limit: int = 100
):
    """获取最近的战斗事件"""
    try:
        if not combat_parser:
            raise HTTPException(status_code=503, detail="Combat parser not ready")
        
        events = combat_parser.combat_events
        
        # 按类型筛选
        if event_type:
            events = [e for e in events if e.get('type') == event_type]
        
        # 按时间排序并限制数量
        events = sorted(events, key=lambda x: x.get('timestamp', datetime.now()), reverse=True)
        events = events[:limit]
        
        return events
        
    except Exception as e:
        logger.error(f"获取事件列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 配置和元数据接口 ====================

@app.get("/api/v1/definitions/jobs")
async def get_job_definitions(job_name: Optional[str] = None):
    """获取职业技能定义"""
    try:
        if not combat_parser:
            raise HTTPException(status_code=503, detail="Combat parser not ready")
        
        if job_name:
            definition = combat_parser.get_job_definition(job_name)
            if not definition:
                raise HTTPException(status_code=404, detail=f"Job '{job_name}' not found")
            return definition
        else:
            return {job: definition for job, definition in combat_parser.job_definitions.items()}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取职业定义失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/definitions/actions/{action_id}")
async def get_action_details(action_id: str):
    """获取技能详细信息"""
    try:
        if not combat_parser:
            raise HTTPException(status_code=503, detail="Combat parser not ready")
        
        action_info = combat_parser.get_action_info(action_id)
        if not action_info:
            raise HTTPException(status_code=404, detail=f"Action '{action_id}' not found")
        
        return {
            "id": action_info.id,
            "name": action_info.name,
            "damage_potency": action_info.damage_potency,
            "heal_potency": action_info.heal_potency
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取技能信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/definitions/zones")
async def get_zone_list():
    """获取支持的区域列表"""
    # 这里可以根据实际需求返回支持的区域
    zones = [
        {"id": "test_zone", "name": "测试区域"},
        {"id": "p10s", "name": "Pandæmonium: Abyssos (Savage) - Pandæmonium Anabaseios: Deathweaver"},
        {"id": "p11s", "name": "Pandæmonium: Abyssos (Savage) - Pandæmonium Anabaseios: Themis"},
        {"id": "p12s", "name": "Pandæmonium: Abyssos (Savage) - Pandæmonium Anabaseios: Athena"},
    ]
    return zones

@app.get("/api/v1/search/actions")
async def search_actions(keyword: str):
    """搜索技能"""
    try:
        if not combat_parser:
            raise HTTPException(status_code=503, detail="Combat parser not ready")
        
        if len(keyword) < 2:
            raise HTTPException(status_code=400, detail="Keyword must be at least 2 characters")
        
        results = combat_parser.search_actions(keyword)
        return [
            {
                "id": action.id,
                "name": action.name,
                "damage_potency": action.damage_potency,
                "heal_potency": action.heal_potency
            }
            for action in results[:50]  # 限制返回数量
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"搜索技能失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== WebSocket 实时推送 ====================

@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 实时数据推送"""
    await websocket.accept()
    websocket_connections.append(websocket)
    
    try:
        while True:
            # 保持连接，等待客户端消息
            data = await websocket.receive_text()
            # 可以根据客户端消息进行不同的处理
            logger.info(f"Received WebSocket message: {data}")
            
    except WebSocketDisconnect:
        websocket_connections.remove(websocket)
        logger.info("WebSocket 连接断开")

async def broadcast_event(event: Dict):
    """向所有WebSocket连接广播事件"""
    if websocket_connections:
        message = json.dumps(event, default=str)
        disconnected = []
        
        for websocket in websocket_connections:
            try:
                await websocket.send_text(message)
            except:
                disconnected.append(websocket)
        
        # 清理断开的连接
        for ws in disconnected:
            if ws in websocket_connections:
                websocket_connections.remove(ws)

# ==================== 数据注入接口 (用于测试) ====================

@app.post("/api/v1/inject/damage")
async def inject_damage_event(damage_data: Dict[str, Any]):
    """注入伤害事件 (测试用)"""
    try:
        if not combat_parser:
            raise HTTPException(status_code=503, detail="Combat parser not ready")
        
        event = combat_parser.parse_damage_event(damage_data)
        combat_parser.add_combat_event(event)
        
        # 广播到WebSocket
        await broadcast_event(event)
        
        return {"status": "success", "event": event}
        
    except Exception as e:
        logger.error(f"注入伤害事件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/inject/heal")
async def inject_heal_event(heal_data: Dict[str, Any]):
    """注入治疗事件 (测试用)"""
    try:
        if not combat_parser:
            raise HTTPException(status_code=503, detail="Combat parser not ready")
        
        event = combat_parser.parse_heal_event(heal_data)
        combat_parser.add_combat_event(event)
        
        # 广播到WebSocket
        await broadcast_event(event)
        
        return {"status": "success", "event": event}
        
    except Exception as e:
        logger.error(f"注入治疗事件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 健康检查和状态接口 ====================

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "parser_ready": combat_parser is not None,
        "websocket_connections": len(websocket_connections)
    }

@app.get("/api/v1/status")
async def get_api_status():
    """获取API状态信息"""
    if not combat_parser:
        return {"status": "parser_not_ready"}
    
    return {
        "status": "ready",
        "jobs_loaded": len(combat_parser.job_definitions),
        "actions_loaded": len(combat_parser.action_lookup),
        "status_effects_loaded": len(combat_parser.status_lookup),
        "name_overrides_loaded": len(combat_parser.name_overrides),
        "current_events": len(combat_parser.combat_events),
        "websocket_connections": len(websocket_connections)
    }

# ==================== 模拟数据生成 (仅用于测试) ====================

async def simulate_combat_data():
    """模拟生成战斗数据用于测试"""
    import random
    
    await asyncio.sleep(5)  # 等待初始化完成
    
    player_names = ["Warrior Tank", "White Mage", "Black Mage", "Dragoon"]
    action_ids = ["8D", "1F", "5edb", "25"]  # Fire, Heavy Swing, Dosis, Maim
    
    while True:
        try:
            if combat_parser and random.random() < 0.3:  # 30% 概率生成事件
                # 随机生成伤害事件
                damage_data = {
                    'source_id': f"player_{random.randint(1, 4)}",
                    'source_name': random.choice(player_names),
                    'target_id': 'enemy_001',
                    'target_name': 'Training Dummy',
                    'action_id': random.choice(action_ids),
                    'damage': random.randint(800, 2500),
                    'is_critical': random.random() < 0.25,
                    'is_direct_hit': random.random() < 0.25
                }
                
                event = combat_parser.parse_damage_event(damage_data)
                combat_parser.add_combat_event(event)
                
                # 广播事件
                await broadcast_event(event)
                
        except Exception as e:
            logger.error(f"模拟数据生成失败: {e}")
        
        await asyncio.sleep(random.uniform(1, 3))  # 随机间隔

# ==================== 启动服务器 ====================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )