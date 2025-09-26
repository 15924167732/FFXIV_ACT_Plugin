"""
批量修复 FFXIV Definitions JSON 文件格式问题
专门处理当前发现的 actions 和 statuseffects 之间的格式错误
"""

import os
import json
import re
from pathlib import Path
import shutil

def fix_json_format(content):
    """修复JSON格式问题"""
    
    # 1. 修复 actions 数组结束后缺少闭合的问题
    # 寻找 ],\n"statuseffects" 模式并修复
    pattern1 = r'(\],)\s*\n\s*("statuseffects"\s*:\s*\[)'
    content = re.sub(pattern1, r'\1\n\2', content)
    
    # 2. 修复字符串被截断的问题（从错误信息可以看出很多字符串被截断）
    # 这个需要手动处理，但我们可以先尝试基本的修复
    
    # 3. 确保所有的双引号都是配对的
    # 修复常见的引号问题
    
    # 4. 移除多余的逗号
    content = re.sub(r',(\s*[}\]])', r'\1', content)
    
    # 5. 确保JSON结构完整
    # 检查是否有未闭合的括号或大括号
    
    return content

def backup_and_fix_file(filepath):
    """备份并修复单个文件"""
    try:
        # 创建备份
        backup_path = str(filepath) + '.backup'
        shutil.copy2(filepath, backup_path)
        
        # 读取文件内容
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 尝试解析原始JSON以确认是否有错误
        try:
            json.loads(content)
            print(f"✅ {filepath.name} - JSON格式正确，跳过")
            os.remove(backup_path)  # 删除不必要的备份
            return True, "文件格式正确"
        except json.JSONDecodeError as e:
            print(f"🔧 {filepath.name} - 发现JSON错误：第{e.lineno}行第{e.colno}列")
            
            # 应用修复
            fixed_content = fix_json_format(content)
            
            # 检查修复后的内容
            try:
                json.loads(fixed_content)
                # 修复成功，保存文件
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                print(f"✅ {filepath.name} - 修复成功")
                return True, "修复成功"
            except json.JSONDecodeError as e2:
                print(f"❌ {filepath.name} - 自动修复失败：第{e2.lineno}行第{e2.colno}列")
                # 恢复原文件
                shutil.copy2(backup_path, filepath)
                return False, f"修复失败：{e2.msg}"
                
    except Exception as e:
        print(f"❌ {filepath.name} - 处理文件时出错：{e}")
        return False, str(e)

def create_minimal_working_files():
    """为有问题的文件创建最小工作版本"""
    
    current_dir = Path(__file__).parent
    definitions_path = current_dir.parent / "Definitions"
    
    # 基本的职业模板
    job_templates = {
        "Astrologian": {
            "job": "astrologian",
            "actions": [
                {"1CF": "benefic", "heal": [{"potency": 500}]},
                {"3200": "aspected benefic", "heal": [{"potency": 250}]}
            ],
            "statuseffects": [
                {"343": "aspected benefic", "timeproc": {"type": "hot", "potency": 250, "maxticks": 5}}
            ]
        },
        "BlackMage": {
            "job": "black mage", 
            "actions": [
                {"8D": "fire", "damage": [{"potency": 300}]},
                {"8E": "blizzard", "damage": [{"potency": 280}]}
            ],
            "statuseffects": [
                {"A1": "thunder", "timeproc": {"type": "dot", "potency": 45, "damagetype": "magic", "maxticks": 8}}
            ]
        },
        "WhiteMage": {
            "job": "white mage",
            "actions": [
                {"78": "cure", "heal": [{"potency": 500}]},
                {"85": "medica", "heal": [{"potency": 400}]}
            ],
            "statuseffects": [
                {"8F": "aero", "timeproc": {"type": "dot", "potency": 35, "damagetype": "magic", "maxticks": 6}}
            ]
        }
    }
    
    # 为每个有问题的文件创建最小版本
    problem_files = [
        "Astrologian.json", "Bard.json", "BlackMage.json", "Chocobo.json",
        "Dancer.json", "DarkKnight.json", "Dragoon.json", "Eureka.json",
        "Gunbreaker.json", "JobRole.json", "Machinist.json", "Monk.json",
        "Ninja.json", "NPC.json", "Paladin.json", "Pictomancer.json",
        "Reaper.json", "RedMage.json", "Sage.json", "Samurai.json",
        "Scholar.json", "Summoner.json", "Viper.json", "Warrior.json",
        "WhiteMage.json"
    ]
    
    for filename in problem_files:
        filepath = definitions_path / filename
        job_name = filename.replace('.json', '')
        
        # 使用模板或创建基本结构
        if job_name in job_templates:
            template = job_templates[job_name]
        else:
            template = {
                "job": job_name.lower(),
                "actions": [
                    {"8D": "basic attack", "damage": [{"potency": 100}]}
                ],
                "statuseffects": []
            }
        
        # 保存最小工作版本
        minimal_file = definitions_path / f"{job_name}_minimal.json"
        with open(minimal_file, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
        
        print(f"📝 创建最小版本：{minimal_file.name}")

def main():
    """主修复流程"""
    print("🔧 FFXIV JSON 批量修复工具")
    print("=" * 60)
    
    current_dir = Path(__file__).parent
    definitions_path = current_dir.parent / "Definitions"
    
    if not definitions_path.exists():
        print(f"❌ Definitions目录不存在：{definitions_path}")
        return
    
    # 获取所有JSON文件
    json_files = list(definitions_path.glob("*.json"))
    
    if not json_files:
        print("❌ 没有找到JSON文件")
        return
    
    print(f"📁 找到 {len(json_files)} 个JSON文件")
    print()
    
    success_count = 0
    fail_count = 0
    
    # 处理每个文件
    for json_file in sorted(json_files):
        if json_file.name.endswith('_minimal.json') or json_file.name.endswith('_backup'):
            continue
            
        success, message = backup_and_fix_file(json_file)
        if success:
            success_count += 1
        else:
            fail_count += 1
    
    print()
    print("=" * 60)
    print(f"📊 处理结果：")
    print(f"   ✅ 成功：{success_count} 个文件")
    print(f"   ❌ 失败：{fail_count} 个文件")
    
    if fail_count > 0:
        print()
        print("🆘 由于JSON文件损坏严重，建议使用最小工作版本：")
        choice = input("是否创建最小工作版本文件？(y/n): ").lower()
        
        if choice in ['y', 'yes', '是']:
            create_minimal_working_files()
            print()
            print("💡 使用说明：")
            print("1. 最小版本文件已创建（*_minimal.json）")
            print("2. 可以重命名 *_minimal.json 为 *.json 来替换损坏的文件")
            print("3. 或者从原始的FFXIV_ACT_Plugin项目复制完整的定义文件")
    
    print()
    print("🚀 现在可以重新启动API服务了：")
    print("   python main.py")

if __name__ == "__main__":
    main()