"""
FFXIV ACT 数据采集客户端
通过 ACT Plugin 的 log parsing 接口获取真实战斗数据
"""

import asyncio
import json
import re
import websockets
import requests
from typing import Dict, List, Optional
import logging
from datetime import datetime
import threading
import time
import os
import sqlite3

logger = logging.getLogger(__name__)

class ACTLogParser:
    """ACT 日志解析器"""
    
    def __init__(self, api_endpoint: str = "http://localhost:8000"):
        self.api_endpoint = api_endpoint
        self.is_running = False
        self.log_patterns = self._compile_patterns()
        
    def _compile_patterns(self):
        """编译日志解析正则表达式"""
        patterns = {
            # 伤害事件: [timestamp] [source] uses [action] on [target] for [damage] damage
            'damage': re.compile(
                r'\[(?P<timestamp>[^\]]+)\] (?P<source>.+?) uses (?P<action>.+?) on (?P<target>.+?) for (?P<damage>\d+) damage'
            ),
            
            # 治疗事件: [timestamp] [source] uses [action] on [target] for [heal] heal
            'heal': re.compile(
                r'\[(?P<timestamp>[^\]]+)\] (?P<source>.+?) uses (?P<action>.+?) on (?P<target>.+?) for (?P<heal>\d+) heal'
            ),
            
            # 状态效果: [timestamp] [target] gains/loses [effect]
            'status_gain': re.compile(
                r'\[(?P<timestamp>[^\]]+)\] (?P<target>.+?) gains (?P<effect>.+)'
            ),
            'status_lose': re.compile(
                r'\[(?P<timestamp>[^\]]+)\] (?P<target>.+?) loses (?P<effect>.+)'
            ),
            
            # 死亡事件: [timestamp] [target] dies
            'death': re.compile(
                r'\[(?P<timestamp>[^\]]+)\] (?P<target>.+?) dies'
            )
        }
        return patterns
    
    def parse_act_log_line(self, line: str) -> Optional[Dict]:
        """解析单行 ACT 日志"""
        try:
            # 尝试匹配伤害事件
            match = self.log_patterns['damage'].match(line)
            if match:
                return {
                    'type': 'damage',
                    'timestamp': match.group('timestamp'),
                    'source_name': match.group('source'),
                    'target_name': match.group('target'),
                    'action_name': match.group('action'),
                    'damage': int(match.group('damage'))
                }
            
            # 尝试匹配治疗事件
            match = self.log_patterns['heal'].match(line)
            if match:
                return {
                    'type': 'heal',
                    'timestamp': match.group('timestamp'),
                    'source_name': match.group('source'),
                    'target_name': match.group('target'),
                    'action_name': match.group('action'),
                    'heal_amount': int(match.group('heal'))
                }
            
            # 其他事件类型...
            
        except Exception as e:
            logger.error(f"解析日志行失败: {e}, 行内容: {line}")
        
        return None

class FFLogsDataCollector:
    """FF Logs 数据采集器 (如果有API访问权限)"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.fflogs.com/api/v2/client"
    
    async def fetch_encounter_data(self, encounter_id: str) -> Dict:
        """从 FF Logs 获取战斗数据"""
        # 这里需要实现 FF Logs API 调用
        # 注意：需要申请 API 权限
        pass

class RealTimeDataCollector:
    """实时数据采集器 - 连接到实际的FFXIV数据源"""
    
    def __init__(self, api_endpoint: str = "http://localhost:8000"):
        self.api_endpoint = api_endpoint
        self.is_running = False
        self.data_buffer = []
        self.websocket = None
        
    async def connect_to_act(self):
        """连接到 ACT 数据源"""
        # 这里需要根据实际的ACT插件接口进行实现
        # 可能的连接方式：
        # 1. 读取ACT日志文件
        # 2. 连接ACT的WebSocket接口 (如果有)
        # 3. 通过共享内存读取数据
        # 4. 通过 OverlayPlugin 的 WebSocket
        
        try:
            # 示例：连接到 OverlayPlugin 的 WebSocket
            uri = "ws://localhost:10501/ws"  # OverlayPlugin 默认端口
            async with websockets.connect(uri) as websocket:
                self.websocket = websocket
                await self._listen_for_data()
                
        except Exception as e:
            logger.error(f"连接到ACT失败: {e}")
            # 降级到文件监控模式
            await self._monitor_log_files()
    
    async def _listen_for_data(self):
        """监听数据流"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                await self._process_act_data(data)
                
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket连接断开")
        except Exception as e:
            logger.error(f"数据监听失败: {e}")
    
    async def _monitor_log_files(self):
        """监控ACT日志文件"""
        # ACT 日志文件通常在 ACT 安装目录下的 Logs 文件夹
        log_paths = [
            r"C:\Program Files (x86)\Advanced Combat Tracker\Logs",
            r"C:\Users\{username}\AppData\Local\Advanced Combat Tracker\Logs",
            # 添加更多可能的路径
        ]
        
        for log_path in log_paths:
            if os.path.exists(log_path):
                await self._tail_log_file(log_path)
                break
    
    async def _tail_log_file(self, log_path: str):
        """实时读取日志文件"""
        import glob
        
        # 找到最新的日志文件
        log_files = glob.glob(os.path.join(log_path, "*.log"))
        if not log_files:
            logger.error("未找到ACT日志文件")
            return
        
        latest_log = max(log_files, key=os.path.getmtime)
        logger.info(f"监控日志文件: {latest_log}")
        
        parser = ACTLogParser(self.api_endpoint)
        
        with open(latest_log, 'r', encoding='utf-8') as f:
            # 移到文件末尾
            f.seek(0, 2)
            
            while self.is_running:
                line = f.readline()
                if line:
                    event = parser.parse_act_log_line(line.strip())
                    if event:
                        await self._send_to_api(event)
                else:
                    await asyncio.sleep(0.1)  # 没有新数据时短暂等待
    
    async def _process_act_data(self, data: Dict):
        """处理来自ACT的数据"""
        try:
            # 根据数据类型进行处理
            if data.get('type') == 'CombatData':
                await self._process_combat_data(data)
            elif data.get('type') == 'LogLine':
                await self._process_log_line(data)
                
        except Exception as e:
            logger.error(f"处理ACT数据失败: {e}")
    
    async def _process_combat_data(self, combat_data: Dict):
        """处理战斗数据"""
        # 转换ACT格式到API格式
        if 'Combatant' in combat_data:
            for combatant in combat_data['Combatant']:
                # 提取DPS、治疗等统计数据
                event = {
                    'type': 'stats_update',
                    'combatant_name': combatant.get('Name'),
                    'dps': combatant.get('EncDPS'),
                    'damage': combatant.get('Damage'),
                    'healing': combatant.get('Healed'),
                    'deaths': combatant.get('Deaths', 0)
                }
                await self._send_to_api(event)
    
    async def _process_log_line(self, log_data: Dict):
        """处理日志行数据"""
        line = log_data.get('line', '')
        parser = ACTLogParser(self.api_endpoint)
        event = parser.parse_act_log_line(line)
        
        if event:
            await self._send_to_api(event)
    
    async def _send_to_api(self, event: Dict):
        """发送事件到API服务器"""
        try:
            if event['type'] == 'damage':
                endpoint = f"{self.api_endpoint}/api/v1/inject/damage"
            elif event['type'] == 'heal':
                endpoint = f"{self.api_endpoint}/api/v1/inject/heal"
            else:
                return  # 暂不支持的事件类型
            
            # 转换格式以匹配API
            api_data = self._convert_to_api_format(event)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(endpoint, json=api_data) as response:
                    if response.status != 200:
                        logger.error(f"发送数据到API失败: {response.status}")
                        
        except Exception as e:
            logger.error(f"发送事件到API失败: {e}")
    
    def _convert_to_api_format(self, event: Dict) -> Dict:
        """转换事件格式以匹配API"""
        if event['type'] == 'damage':
            return {
                'source_id': f"player_{hash(event['source_name']) % 1000}",
                'source_name': event['source_name'],
                'target_id': f"target_{hash(event['target_name']) % 1000}",
                'target_name': event['target_name'],
                'action_id': '8D',  # 需要从动作名称映射到ID
                'damage': event['damage'],
                'is_critical': False,  # 需要从日志中解析
                'is_direct_hit': False
            }
        elif event['type'] == 'heal':
            return {
                'source_id': f"player_{hash(event['source_name']) % 1000}",
                'source_name': event['source_name'],
                'target_id': f"target_{hash(event['target_name']) % 1000}",
                'target_name': event['target_name'],
                'action_id': '5edc',  # 需要映射
                'heal_amount': event['heal_amount'],
                'overheal_amount': 0
            }
        
        return {}
    
    async def start(self):
        """启动数据采集"""
        self.is_running = True
        logger.info("启动实时数据采集")
        
        try:
            await self.connect_to_act()
        except Exception as e:
            logger.error(f"数据采集启动失败: {e}")
    
    def stop(self):
        """停止数据采集"""
        self.is_running = False
        if self.websocket:
            asyncio.create_task(self.websocket.close())

class DataCollectorManager:
    """数据采集管理器"""
    
    def __init__(self, api_endpoint: str = "http://localhost:8000"):
        self.api_endpoint = api_endpoint
        self.collectors = []
        self.is_running = False
    
    def add_collector(self, collector):
        """添加数据采集器"""
        self.collectors.append(collector)
    
    async def start_all(self):
        """启动所有采集器"""
        self.is_running = True
        tasks = []
        
        for collector in self.collectors:
            if hasattr(collector, 'start'):
                tasks.append(asyncio.create_task(collector.start()))
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    def stop_all(self):
        """停止所有采集器"""
        self.is_running = False
        for collector in self.collectors:
            if hasattr(collector, 'stop'):
                collector.stop()

# 使用示例
async def main():
    # 创建数据采集管理器
    manager = DataCollectorManager("http://localhost:8000")
    
    # 添加实时数据采集器
    real_time_collector = RealTimeDataCollector("http://localhost:8000")
    manager.add_collector(real_time_collector)
    
    try:
        # 启动所有采集器
        await manager.start_all()
    except KeyboardInterrupt:
        logger.info("收到停止信号")
    finally:
        manager.stop_all()

if __name__ == "__main__":
    import aiohttp
    
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())