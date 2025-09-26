"""
FFXIV Combat Data API - 接口规范
支持实时战斗数据解析和历史数据查询
"""

from typing import List, Dict, Optional, Union
from datetime import datetime
from pydantic import BaseModel
from enum import Enum

# ==================== 数据模型 ====================

class DamageType(str, Enum):
    PHYSICAL = "physical"
    MAGIC = "magic"
    DARKNESS = "darkness"

class ActionType(str, Enum):
    DAMAGE = "damage"
    HEAL = "heal"
    BUFF = "buff"
    DEBUFF = "debuff"

class JobType(str, Enum):
    TANK = "tank"
    HEALER = "healer"
    MELEE_DPS = "melee_dps"
    RANGED_DPS = "ranged_dps"
    CASTER_DPS = "caster_dps"

class CombatantModel(BaseModel):
    """战斗者信息"""
    id: str
    name: str
    job: str
    job_type: JobType
    level: int
    world: str
    is_player: bool = True

class ActionModel(BaseModel):
    """技能动作信息"""
    id: str
    name: str
    action_type: ActionType
    potency: int
    cast_time: float
    recast_time: float
    range: int
    target_type: str

class DamageEvent(BaseModel):
    """伤害事件"""
    timestamp: datetime
    source_id: str
    target_id: str
    action_id: str
    action_name: str
    damage: int
    damage_type: DamageType
    is_critical: bool = False
    is_direct_hit: bool = False
    is_blocked: bool = False
    block_amount: int = 0

class HealEvent(BaseModel):
    """治疗事件"""
    timestamp: datetime
    source_id: str
    target_id: str
    action_id: str
    action_name: str
    heal_amount: int
    overheal_amount: int = 0
    is_critical: bool = False

class StatusEffectEvent(BaseModel):
    """状态效果事件"""
    timestamp: datetime
    target_id: str
    effect_id: str
    effect_name: str
    stack_count: int = 1
    duration: float
    is_applied: bool  # True=应用, False=移除

class CombatStats(BaseModel):
    """战斗统计数据"""
    combatant_id: str
    duration: float  # 战斗时长(秒)
    
    # DPS统计
    total_damage: int
    dps: float
    rdps: float  # 考虑团队增益的DPS
    
    # 治疗统计
    total_heal: int
    hps: float
    overheal_percent: float
    
    # 技能统计
    total_actions: int
    skill_accuracy: float
    critical_hit_rate: float
    direct_hit_rate: float
    
    # 死亡统计
    death_count: int
    death_times: List[datetime] = []

class EncounterSummary(BaseModel):
    """副本战斗总结"""
    encounter_id: str
    zone_name: str
    boss_name: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    duration: float
    is_success: bool
    
    # 团队统计
    total_dps: float
    total_hps: float
    combatants: List[CombatStats]

# ==================== API 接口 ====================

class FFXIVCombatAPI:
    """FFXIV战斗数据API接口定义"""
    
    # ========== 实时数据接口 ==========
    
    def get_current_encounter(self) -> Optional[EncounterSummary]:
        """获取当前进行中的战斗信息"""
        pass
    
    def get_live_stats(self, combatant_id: Optional[str] = None) -> Union[List[CombatStats], CombatStats]:
        """获取实时战斗统计
        
        Args:
            combatant_id: 指定战斗者ID，为空则返回所有人的数据
        """
        pass
    
    def get_recent_events(self, 
                         event_type: Optional[str] = None,
                         limit: int = 100) -> List[Union[DamageEvent, HealEvent, StatusEffectEvent]]:
        """获取最近的战斗事件
        
        Args:
            event_type: 事件类型 (damage/heal/status)
            limit: 返回数量限制
        """
        pass
    
    # ========== 历史数据接口 ==========
    
    def get_encounter_history(self,
                            zone_name: Optional[str] = None,
                            start_date: Optional[datetime] = None,
                            end_date: Optional[datetime] = None,
                            limit: int = 50) -> List[EncounterSummary]:
        """获取历史战斗记录"""
        pass
    
    def get_encounter_details(self, encounter_id: str) -> EncounterSummary:
        """获取指定战斗的详细信息"""
        pass
    
    def get_combatant_performance(self,
                                combatant_name: str,
                                zone_name: Optional[str] = None,
                                days: int = 30) -> List[CombatStats]:
        """获取指定玩家的表现历史"""
        pass
    
    # ========== 配置和元数据接口 ==========
    
    def get_job_definitions(self, job_name: Optional[str] = None) -> Dict:
        """获取职业技能定义"""
        pass
    
    def get_action_details(self, action_id: str) -> ActionModel:
        """获取技能详细信息"""
        pass
    
    def get_zone_list(self) -> List[Dict[str, str]]:
        """获取支持的区域列表"""
        pass
    
    # ========== WebSocket 实时推送 ==========
    
    def subscribe_live_data(self, callback_url: str, event_types: List[str]):
        """订阅实时数据推送
        
        Args:
            callback_url: 回调URL
            event_types: 订阅的事件类型列表
        """
        pass
    
    def unsubscribe_live_data(self, callback_url: str):
        """取消订阅"""
        pass

# ==================== HTTP API 路由 ==========

"""
REST API 端点设计:

GET /api/v1/combat/current
    获取当前战斗信息

GET /api/v1/combat/live/stats?combatant_id={id}
    获取实时统计数据

GET /api/v1/combat/live/events?type={type}&limit={limit}
    获取最近事件

GET /api/v1/encounters?zone={zone}&start={start}&end={end}&limit={limit}
    获取历史战斗记录

GET /api/v1/encounters/{encounter_id}
    获取战斗详情

GET /api/v1/combatants/{name}/performance?zone={zone}&days={days}
    获取玩家表现

GET /api/v1/definitions/jobs/{job_name}
    获取职业定义

GET /api/v1/definitions/actions/{action_id}
    获取技能信息

GET /api/v1/definitions/zones
    获取区域列表

WebSocket: /ws/live
    实时数据推送
"""

# ==================== 使用示例 ==========

"""
# Python客户端使用示例
import requests
import websocket
import json

# 1. 获取当前战斗数据
response = requests.get("http://localhost:8000/api/v1/combat/current")
current_fight = response.json()

# 2. 获取实时DPS统计
response = requests.get("http://localhost:8000/api/v1/combat/live/stats")
live_stats = response.json()

# 3. 订阅实时数据推送
def on_message(ws, message):
    data = json.loads(message)
    if data['type'] == 'damage_event':
        print(f"{data['source_name']} 对 {data['target_name']} 造成了 {data['damage']} 点伤害")

ws = websocket.WebSocketApp("ws://localhost:8000/ws/live")
ws.on_message = on_message
ws.run_forever()
"""