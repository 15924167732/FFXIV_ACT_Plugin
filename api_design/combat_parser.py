"""
FFXIV 战斗数据解析引擎
基于现有的 JSON 定义文件实现实时战斗数据解析
"""

import json
import os
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import logging

@dataclass
class ActionDefinition:
    """技能定义"""
    id: str
    name: str
    damage_potency: List[Dict]
    heal_potency: List[Dict]

@dataclass
class StatusEffectDefinition:
    """状态效果定义"""
    id: str
    name: str
    effect_type: str
    potency: int
    duration: int
    damage_type: Optional[str] = None

class FFXIVCombatParser:
    """FFXIV战斗数据解析器"""
    
    def __init__(self, definitions_path: str, overrides_path: str):
        """
        初始化解析器
        
        Args:
            definitions_path: 技能定义文件目录路径
            overrides_path: 名称覆盖文件目录路径
        """
        self.definitions_path = definitions_path
        self.overrides_path = overrides_path
        
        # 数据存储
        self.job_definitions: Dict[str, Dict] = {}
        self.action_lookup: Dict[str, ActionDefinition] = {}
        self.status_lookup: Dict[str, StatusEffectDefinition] = {}
        self.name_overrides: Dict[str, str] = {}
        
        # 战斗状态
        self.current_encounter = None
        self.combatants: Dict[str, Dict] = {}
        self.combat_events: List[Dict] = []
        
        self.logger = logging.getLogger(__name__)
        self._load_definitions()
        self._load_overrides()
    
    def _load_definitions(self):
        """加载所有职业技能定义"""
        try:
            definitions_loaded = 0
            actions_loaded = 0
            status_loaded = 0
            
            for filename in os.listdir(self.definitions_path):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.definitions_path, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            job_name = data.get('job', '')
                            self.job_definitions[job_name] = data
                            definitions_loaded += 1
                            
                            # 建立技能查找表
                            for action in data.get('actions', []):
                                for action_id, action_data in action.items():
                                    if isinstance(action_data, str):
                                        # 简单格式: {"8D": "fire"}
                                        self.action_lookup[action_id.upper()] = ActionDefinition(
                                            id=action_id,
                                            name=action_data,
                                            damage_potency=[],
                                            heal_potency=[]
                                        )
                                        actions_loaded += 1
                                    else:
                                        # 复杂格式: {"8D": "fire", "damage": [...]}
                                        self.action_lookup[action_id.upper()] = ActionDefinition(
                                            id=action_id,
                                            name=action_data,
                                            damage_potency=action.get('damage', []),
                                            heal_potency=action.get('heal', [])
                                        )
                                        actions_loaded += 1
                            
                            # 建立状态效果查找表
                            for status in data.get('statuseffects', []):
                                for status_id, status_data in status.items():
                                    if isinstance(status_data, str):
                                        self.status_lookup[status_id.upper()] = StatusEffectDefinition(
                                            id=status_id,
                                            name=status_data,
                                            effect_type="unknown",
                                            potency=0,
                                            duration=0
                                        )
                                        status_loaded += 1
                                    else:
                                        timeproc = status_data.get('timeproc', {})
                                        self.status_lookup[status_id.upper()] = StatusEffectDefinition(
                                            id=status_id,
                                            name=list(status.keys())[0],
                                            effect_type=timeproc.get('type', 'unknown'),
                                            potency=timeproc.get('potency', 0),
                                            duration=timeproc.get('maxticks', 0),
                                            damage_type=timeproc.get('damagetype')
                                        )
                                        status_loaded += 1
                                        
                    except json.JSONDecodeError as e:
                        self.logger.error(f"JSON格式错误 in {filename}: 第{e.lineno}行第{e.colno}列 - {e.msg}")
                        self.logger.error(f"错误位置: {e.doc[max(0, e.pos-50):e.pos+50]}")
                        continue
                    except Exception as e:
                        self.logger.error(f"加载文件失败 {filename}: {e}")
                        continue
            
            self.logger.info(f"成功加载 {definitions_loaded} 个职业定义")
            self.logger.info(f"成功加载 {actions_loaded} 个技能定义")
            self.logger.info(f"成功加载 {status_loaded} 个状态效果定义")
            
        except Exception as e:
            self.logger.error(f"加载技能定义失败: {e}")
    
    def _load_overrides(self):
        """加载名称覆盖配置"""
        try:
            for filename in os.listdir(self.overrides_path):
                if filename.endswith('.txt'):
                    filepath = os.path.join(self.overrides_path, filename)
                    with open(filepath, 'r', encoding='utf-8-sig') as f:
                        for line in f:
                            line = line.strip()
                            if line and '|' in line and not line.startswith('#'):
                                parts = line.split('|', 1)
                                if len(parts) == 2:
                                    old_name, new_name = parts
                                    self.name_overrides[old_name] = new_name
            
            self.logger.info(f"加载了 {len(self.name_overrides)} 个名称覆盖")
            
        except Exception as e:
            self.logger.error(f"加载名称覆盖失败: {e}")
    
    def get_action_info(self, action_id: str) -> Optional[ActionDefinition]:
        """根据技能ID获取技能信息"""
        return self.action_lookup.get(action_id.upper())
    
    def get_status_info(self, status_id: str) -> Optional[StatusEffectDefinition]:
        """根据状态ID获取状态效果信息"""
        return self.status_lookup.get(status_id.upper())
    
    def apply_name_override(self, original_name: str) -> str:
        """应用名称覆盖"""
        # 查找匹配的覆盖规则
        for pattern, replacement in self.name_overrides.items():
            if pattern in original_name:
                return replacement
        return original_name
    
    def parse_damage_event(self, raw_data: Dict) -> Dict:
        """解析伤害事件"""
        try:
            action_id = raw_data.get('action_id', '').upper()
            action_info = self.get_action_info(action_id)
            
            event = {
                'type': 'damage',
                'timestamp': datetime.now(),
                'source_id': raw_data.get('source_id'),
                'source_name': raw_data.get('source_name'),
                'target_id': raw_data.get('target_id'),
                'target_name': raw_data.get('target_name'),
                'action_id': action_id,
                'action_name': action_info.name if action_info else f"Unknown_{action_id}",
                'damage': raw_data.get('damage', 0),
                'damage_type': raw_data.get('damage_type', 'physical'),
                'is_critical': raw_data.get('is_critical', False),
                'is_direct_hit': raw_data.get('is_direct_hit', False),
                'is_blocked': raw_data.get('is_blocked', False),
                'block_amount': raw_data.get('block_amount', 0)
            }
            
            # 应用名称覆盖
            event['action_name'] = self.apply_name_override(event['action_name'])
            
            return event
            
        except Exception as e:
            self.logger.error(f"解析伤害事件失败: {e}")
            return {}
    
    def parse_heal_event(self, raw_data: Dict) -> Dict:
        """解析治疗事件"""
        try:
            action_id = raw_data.get('action_id', '').upper()
            action_info = self.get_action_info(action_id)
            
            event = {
                'type': 'heal',
                'timestamp': datetime.now(),
                'source_id': raw_data.get('source_id'),
                'source_name': raw_data.get('source_name'),
                'target_id': raw_data.get('target_id'),
                'target_name': raw_data.get('target_name'),
                'action_id': action_id,
                'action_name': action_info.name if action_info else f"Unknown_{action_id}",
                'heal_amount': raw_data.get('heal_amount', 0),
                'overheal_amount': raw_data.get('overheal_amount', 0),
                'is_critical': raw_data.get('is_critical', False)
            }
            
            # 应用名称覆盖
            event['action_name'] = self.apply_name_override(event['action_name'])
            
            return event
            
        except Exception as e:
            self.logger.error(f"解析治疗事件失败: {e}")
            return {}
    
    def parse_status_event(self, raw_data: Dict) -> Dict:
        """解析状态效果事件"""
        try:
            status_id = raw_data.get('status_id', '').upper()
            status_info = self.get_status_info(status_id)
            
            event = {
                'type': 'status',
                'timestamp': datetime.now(),
                'target_id': raw_data.get('target_id'),
                'target_name': raw_data.get('target_name'),
                'status_id': status_id,
                'status_name': status_info.name if status_info else f"Unknown_{status_id}",
                'stack_count': raw_data.get('stack_count', 1),
                'duration': raw_data.get('duration', 0),
                'is_applied': raw_data.get('is_applied', True)
            }
            
            # 应用名称覆盖
            event['status_name'] = self.apply_name_override(event['status_name'])
            
            return event
            
        except Exception as e:
            self.logger.error(f"解析状态事件失败: {e}")
            return {}
    
    def calculate_dps_stats(self, combatant_id: str, time_window: int = 60) -> Dict:
        """计算DPS统计数据"""
        try:
            now = datetime.now()
            cutoff_time = now.timestamp() - time_window
            
            # 筛选时间窗口内的伤害事件
            damage_events = [
                event for event in self.combat_events
                if (event.get('type') == 'damage' and 
                    event.get('source_id') == combatant_id and
                    event.get('timestamp', now).timestamp() > cutoff_time)
            ]
            
            if not damage_events:
                return {
                    'combatant_id': combatant_id,
                    'total_damage': 0,
                    'dps': 0.0,
                    'hit_count': 0,
                    'critical_hits': 0,
                    'critical_rate': 0.0,
                    'direct_hits': 0,
                    'direct_hit_rate': 0.0
                }
            
            total_damage = sum(event.get('damage', 0) for event in damage_events)
            hit_count = len(damage_events)
            critical_hits = sum(1 for event in damage_events if event.get('is_critical', False))
            direct_hits = sum(1 for event in damage_events if event.get('is_direct_hit', False))
            
            actual_duration = min(time_window, 
                                (now - min(event.get('timestamp', now) for event in damage_events)).total_seconds())
            
            return {
                'combatant_id': combatant_id,
                'total_damage': total_damage,
                'dps': total_damage / max(actual_duration, 1),
                'hit_count': hit_count,
                'critical_hits': critical_hits,
                'critical_rate': critical_hits / max(hit_count, 1) * 100,
                'direct_hits': direct_hits,
                'direct_hit_rate': direct_hits / max(hit_count, 1) * 100
            }
            
        except Exception as e:
            self.logger.error(f"计算DPS统计失败: {e}")
            return {}
    
    def add_combat_event(self, event: Dict):
        """添加战斗事件"""
        if event:
            self.combat_events.append(event)
            
            # 限制事件数量，避免内存溢出
            if len(self.combat_events) > 10000:
                self.combat_events = self.combat_events[-5000:]
    
    def get_job_definition(self, job_name: str) -> Dict:
        """获取职业定义"""
        return self.job_definitions.get(job_name, {})
    
    def get_all_jobs(self) -> List[str]:
        """获取所有支持的职业列表"""
        return list(self.job_definitions.keys())
    
    def search_actions(self, keyword: str) -> List[ActionDefinition]:
        """搜索技能"""
        results = []
        keyword_lower = keyword.lower()
        
        for action in self.action_lookup.values():
            if keyword_lower in action.name.lower():
                results.append(action)
        
        return results
    
    def get_combat_summary(self) -> Dict:
        """获取当前战斗总结"""
        if not self.combat_events:
            return {}
        
        # 统计各种数据
        damage_events = [e for e in self.combat_events if e.get('type') == 'damage']
        heal_events = [e for e in self.combat_events if e.get('type') == 'heal']
        
        # 获取所有参与者
        participants = set()
        for event in self.combat_events:
            if event.get('source_id'):
                participants.add(event['source_id'])
            if event.get('target_id'):
                participants.add(event['target_id'])
        
        # 计算各参与者的统计
        participant_stats = {}
        for participant in participants:
            participant_stats[participant] = self.calculate_dps_stats(participant)
        
        return {
            'start_time': min(e.get('timestamp', datetime.now()) for e in self.combat_events) if self.combat_events else datetime.now(),
            'end_time': max(e.get('timestamp', datetime.now()) for e in self.combat_events) if self.combat_events else datetime.now(),
            'total_events': len(self.combat_events),
            'damage_events': len(damage_events),
            'heal_events': len(heal_events),
            'participants': len(participants),
            'participant_stats': participant_stats,
            'total_damage': sum(e.get('damage', 0) for e in damage_events),
            'total_healing': sum(e.get('heal_amount', 0) for e in heal_events)
        }

# 使用示例
if __name__ == "__main__":
    # 初始化解析器
    parser = FFXIVCombatParser(
        definitions_path="../Definitions",
        overrides_path="../Overrides"
    )
    
    # 模拟解析事件
    damage_data = {
        'source_id': 'player_001',
        'source_name': 'TestPlayer',
        'target_id': 'enemy_001', 
        'target_name': 'Training Dummy',
        'action_id': '8D',  # Fire
        'damage': 1200,
        'is_critical': True
    }
    
    damage_event = parser.parse_damage_event(damage_data)
    parser.add_combat_event(damage_event)
    
    # 获取统计数据
    stats = parser.calculate_dps_stats('player_001')
    print(f"DPS统计: {stats}")
    
    # 获取技能信息
    fire_info = parser.get_action_info('8D')
    print(f"技能信息: {fire_info}")