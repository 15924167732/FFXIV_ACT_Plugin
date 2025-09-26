"""
FFXIV Combat Data API 测试脚本
用于验证API功能是否正常工作
"""

import requests
import json
import time
import random
import threading
import websocket

API_BASE = "http://localhost:8000"

def test_api_health():
    """测试API健康状态"""
    print("🔍 测试API健康状态...")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API服务正常运行")
            print(f"   状态: {data.get('status')}")
            print(f"   解析器就绪: {data.get('parser_ready')}")
            return True
        else:
            print(f"❌ API响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到API服务: {e}")
        print("💡 请确保API服务正在运行 (python main.py)")
        return False

def test_api_status():
    """测试API状态信息"""
    print("\n🔍 测试API状态...")
    try:
        response = requests.get(f"{API_BASE}/api/v1/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API状态正常")
            print(f"   职业定义: {data.get('jobs_loaded')} 个")
            print(f"   技能定义: {data.get('actions_loaded')} 个")
            print(f"   状态效果: {data.get('status_effects_loaded')} 个")
            print(f"   名称覆盖: {data.get('name_overrides_loaded')} 个")
            return True
        else:
            print(f"❌ 获取状态失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 状态检查失败: {e}")
        return False

def test_job_definitions():
    """测试职业定义接口"""
    print("\n🔍 测试职业定义...")
    try:
        response = requests.get(f"{API_BASE}/api/v1/definitions/jobs")
        if response.status_code == 200:
            jobs = response.json()
            print(f"✅ 成功获取职业定义")
            print(f"   支持的职业: {list(jobs.keys())}")
            
            # 测试获取特定职业
            if 'black mage' in jobs:
                response = requests.get(f"{API_BASE}/api/v1/definitions/jobs/black mage")
                if response.status_code == 200:
                    bm_data = response.json()
                    actions_count = len(bm_data.get('actions', []))
                    status_count = len(bm_data.get('statuseffects', []))
                    print(f"   黑魔法师: {actions_count} 个技能, {status_count} 个状态效果")
            return True
        else:
            print(f"❌ 获取职业定义失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 职业定义测试失败: {e}")
        return False

def test_action_search():
    """测试技能搜索"""
    print("\n🔍 测试技能搜索...")
    try:
        response = requests.get(f"{API_BASE}/api/v1/search/actions?keyword=fire")
        if response.status_code == 200:
            actions = response.json()
            print(f"✅ 成功搜索技能")
            print(f"   找到 {len(actions)} 个包含'fire'的技能")
            if actions:
                first_action = actions[0]
                print(f"   示例: {first_action['name']} (ID: {first_action['id']})")
            return True
        else:
            print(f"❌ 技能搜索失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 技能搜索测试失败: {e}")
        return False

def test_data_injection():
    """测试数据注入"""
    print("\n🔍 测试数据注入...")
    try:
        # 注入伤害事件
        damage_data = {
            'source_id': 'test_player_001',
            'source_name': '测试玩家',
            'target_id': 'test_enemy_001',
            'target_name': '训练木人',
            'action_id': '8D',  # Fire
            'damage': 1500,
            'is_critical': True,
            'is_direct_hit': False
        }
        
        response = requests.post(f"{API_BASE}/api/v1/inject/damage", json=damage_data)
        if response.status_code == 200:
            print("✅ 成功注入伤害事件")
            result = response.json()
            event = result.get('event', {})
            print(f"   事件: {event.get('source_name')} → {event.get('target_name')}")
            print(f"   伤害: {event.get('damage')} (暴击: {event.get('is_critical')})")
        else:
            print(f"❌ 伤害事件注入失败: {response.status_code}")
            return False
        
        # 注入治疗事件
        heal_data = {
            'source_id': 'test_healer_001',
            'source_name': '测试治疗',
            'target_id': 'test_player_001',
            'target_name': '测试玩家',
            'action_id': '5edc',  # Diagnosis
            'heal_amount': 800,
            'overheal_amount': 100
        }
        
        response = requests.post(f"{API_BASE}/api/v1/inject/heal", json=heal_data)
        if response.status_code == 200:
            print("✅ 成功注入治疗事件")
            result = response.json()
            event = result.get('event', {})
            print(f"   事件: {event.get('source_name')} → {event.get('target_name')}")
            print(f"   治疗: {event.get('heal_amount')} (过量: {event.get('overheal_amount', 0)})")
            return True
        else:
            print(f"❌ 治疗事件注入失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 数据注入测试失败: {e}")
        return False

def test_live_stats():
    """测试实时统计"""
    print("\n🔍 测试实时统计...")
    try:
        response = requests.get(f"{API_BASE}/api/v1/combat/live/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ 成功获取实时统计")
            if stats:
                print(f"   活跃玩家: {len(stats)} 人")
                for player_id, player_stats in stats.items():
                    dps = player_stats.get('dps', 0)
                    damage = player_stats.get('total_damage', 0)
                    print(f"   {player_id}: DPS {dps:.1f}, 总伤害 {damage:,}")
            else:
                print("   当前没有战斗数据")
            return True
        else:
            print(f"❌ 获取实时统计失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 实时统计测试失败: {e}")
        return False

def test_websocket():
    """测试WebSocket连接"""
    print("\n🔍 测试WebSocket连接...")
    
    websocket_success = [False]
    messages_received = [0]
    
    def on_message(ws, message):
        messages_received[0] += 1
        data = json.loads(message)
        print(f"   📨 收到WebSocket消息 #{messages_received[0]}: {data.get('type', 'unknown')}")
    
    def on_open(ws):
        websocket_success[0] = True
        print("✅ WebSocket连接成功")
    
    def on_error(ws, error):
        print(f"❌ WebSocket错误: {error}")
    
    def on_close(ws, close_status_code, close_msg):
        print(f"🔌 WebSocket连接关闭")
    
    try:
        ws = websocket.WebSocketApp(
            "ws://localhost:8000/ws/live",
            on_message=on_message,
            on_open=on_open,
            on_error=on_error,
            on_close=on_close
        )
        
        # 在单独线程中运行WebSocket
        ws_thread = threading.Thread(target=ws.run_forever, daemon=True)
        ws_thread.start()
        
        # 等待连接建立
        time.sleep(2)
        
        if websocket_success[0]:
            # 注入一些测试数据来触发WebSocket消息
            print("   📤 注入测试数据以触发WebSocket消息...")
            for i in range(3):
                test_damage = {
                    'source_id': f'ws_test_{i}',
                    'source_name': f'WebSocket测试{i+1}',
                    'target_id': 'ws_target',
                    'target_name': 'WebSocket目标',
                    'action_id': '8D',
                    'damage': random.randint(1000, 2000),
                    'is_critical': random.choice([True, False])
                }
                requests.post(f"{API_BASE}/api/v1/inject/damage", json=test_damage)
                time.sleep(0.5)
            
            # 等待消息接收
            time.sleep(2)
            ws.close()
            
            if messages_received[0] > 0:
                print(f"✅ WebSocket测试成功，收到 {messages_received[0]} 条消息")
                return True
            else:
                print("⚠️ WebSocket连接成功但未收到消息")
                return False
        else:
            print("❌ WebSocket连接失败")
            return False
            
    except Exception as e:
        print(f"❌ WebSocket测试失败: {e}")
        return False

def generate_test_data():
    """生成一些测试数据"""
    print("\n🎮 生成测试战斗数据...")
    
    players = [
        {'id': 'tank_001', 'name': '圣骑坦克', 'actions': ['1F', '25']},  # Heavy Swing, Maim
        {'id': 'healer_001', 'name': '白魔治疗', 'actions': ['5edc', '5ede']},  # Diagnosis, Prognosis
        {'id': 'dps_001', 'name': '黑魔输出', 'actions': ['8D', '8E']},  # Fire, Blizzard
        {'id': 'dps_002', 'name': '武士输出', 'actions': ['1D50', '1D51']}  # Riposte, Verthunder
    ]
    
    enemies = [
        {'id': 'boss_001', 'name': '石卫塔'},
        {'id': 'add_001', 'name': '石像兵'}
    ]
    
    print(f"   模拟 {len(players)} 个玩家 vs {len(enemies)} 个敌人的战斗...")
    
    events_generated = 0
    
    # 生成30秒的战斗数据
    for second in range(30):
        for player in players:
            # 70%概率攻击，30%概率治疗
            if random.random() < 0.7:
                # 攻击事件
                target = random.choice(enemies)
                damage_data = {
                    'source_id': player['id'],
                    'source_name': player['name'],
                    'target_id': target['id'],
                    'target_name': target['name'],
                    'action_id': random.choice(player['actions']),
                    'damage': random.randint(800, 2500),
                    'is_critical': random.random() < 0.25,
                    'is_direct_hit': random.random() < 0.25
                }
                
                try:
                    requests.post(f"{API_BASE}/api/v1/inject/damage", json=damage_data, timeout=1)
                    events_generated += 1
                except:
                    pass
            
            elif player['name'].endswith('治疗'):
                # 治疗事件
                target = random.choice(players)
                heal_data = {
                    'source_id': player['id'],
                    'source_name': player['name'],
                    'target_id': target['id'],
                    'target_name': target['name'],
                    'action_id': random.choice(player['actions']),
                    'heal_amount': random.randint(600, 1200),
                    'overheal_amount': random.randint(0, 200)
                }
                
                try:
                    requests.post(f"{API_BASE}/api/v1/inject/heal", json=heal_data, timeout=1)
                    events_generated += 1
                except:
                    pass
        
        time.sleep(0.1)  # 模拟实时数据流
        if second % 5 == 0:
            print(f"   📊 已生成 {events_generated} 个事件...")
    
    print(f"✅ 测试数据生成完成，共 {events_generated} 个事件")
    
    # 显示最终统计
    try:
        response = requests.get(f"{API_BASE}/api/v1/combat/live/stats")
        if response.status_code == 200:
            stats = response.json()
            print("\n📈 最终战斗统计:")
            sorted_stats = sorted(stats.items(), key=lambda x: x[1].get('dps', 0), reverse=True)
            for i, (player_id, data) in enumerate(sorted_stats):
                dps = data.get('dps', 0)
                damage = data.get('total_damage', 0)
                print(f"   {i+1}. {player_id}: {dps:.1f} DPS ({damage:,} 总伤害)")
    except:
        pass

def main():
    """主测试函数"""
    print("🚀 FFXIV Combat Data API 功能测试")
    print("=" * 50)
    
    tests = [
        ("API健康检查", test_api_health),
        ("API状态检查", test_api_status),
        ("职业定义测试", test_job_definitions),
        ("技能搜索测试", test_action_search),
        ("数据注入测试", test_data_injection),
        ("实时统计测试", test_live_stats),
        ("WebSocket测试", test_websocket),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except KeyboardInterrupt:
            print("\n⚠️ 测试被用户中断")
            break
        except Exception as e:
            print(f"❌ {test_name} 执行出错: {e}")
    
    print(f"\n📊 测试结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！API功能正常")
        
        # 询问是否生成测试数据
        try:
            choice = input("\n是否要生成测试战斗数据？(y/n): ").lower()
            if choice in ['y', 'yes', '是']:
                generate_test_data()
                print("\n💡 现在可以:")
                print("   1. 访问 http://localhost:8000/docs 查看API文档")
                print("   2. 用浏览器打开 frontend_example.html 查看实时数据")
                print("   3. 使用提供的Python客户端代码连接API")
        except KeyboardInterrupt:
            print("\n👋 测试完成")
    else:
        print("⚠️ 部分测试失败，请检查API服务状态")

if __name__ == "__main__":
    main()