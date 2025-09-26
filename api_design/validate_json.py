"""
JSON文件验证工具
用于检查和修复Definitions文件夹中的JSON格式问题
"""

import json
import os
import sys
from pathlib import Path

def validate_json_file(filepath):
    """验证单个JSON文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            json.loads(content)
        return True, None
    except json.JSONDecodeError as e:
        return False, f"第{e.lineno}行第{e.colno}列: {e.msg}"
    except Exception as e:
        return False, str(e)

def fix_common_json_issues(filepath):
    """修复常见的JSON问题"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 常见修复：
        # 1. 移除多余的逗号
        content = content.replace(',]', ']')
        content = content.replace(',}', '}')
        
        # 2. 修复单引号为双引号
        import re
        content = re.sub(r"'([^']*)':", r'"\1":', content)
        
        # 3. 确保正确的UTF-8编码
        content = content.encode('utf-8').decode('utf-8')
        
        # 如果有修改，保存修复后的文件
        if content != original_content:
            backup_path = filepath + '.backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ 已修复 {filepath}")
            print(f"   备份保存到: {backup_path}")
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ 修复失败 {filepath}: {e}")
        return False

def validate_definitions_folder():
    """验证整个Definitions文件夹"""
    
    # 获取Definitions文件夹路径
    current_dir = Path(__file__).parent
    definitions_path = current_dir.parent / "Definitions"
    
    if not definitions_path.exists():
        print(f"❌ Definitions文件夹不存在: {definitions_path}")
        return False
    
    print(f"🔍 检查Definitions文件夹: {definitions_path}")
    print("=" * 60)
    
    valid_files = 0
    invalid_files = 0
    fixed_files = 0
    
    json_files = list(definitions_path.glob("*.json"))
    
    if not json_files:
        print("⚠️ 没有找到JSON文件")
        return False
    
    for json_file in json_files:
        print(f"📄 检查: {json_file.name}")
        
        is_valid, error = validate_json_file(json_file)
        
        if is_valid:
            print(f"   ✅ JSON格式正确")
            valid_files += 1
        else:
            print(f"   ❌ JSON格式错误: {error}")
            invalid_files += 1
            
            # 尝试自动修复
            print(f"   🔧 尝试自动修复...")
            if fix_common_json_issues(json_file):
                # 重新验证
                is_valid_after_fix, _ = validate_json_file(json_file)
                if is_valid_after_fix:
                    print(f"   ✅ 修复成功！")
                    fixed_files += 1
                    invalid_files -= 1
                    valid_files += 1
                else:
                    print(f"   ❌ 自动修复失败，需要手动处理")
        
        print()
    
    print("=" * 60)
    print(f"📊 验证结果:")
    print(f"   ✅ 有效文件: {valid_files}")
    print(f"   ❌ 无效文件: {invalid_files}")
    print(f"   🔧 已修复文件: {fixed_files}")
    
    if invalid_files == 0:
        print("🎉 所有JSON文件格式正确！")
        return True
    else:
        print("⚠️ 仍有文件需要手动修复")
        return False

def create_sample_files():
    """创建示例文件"""
    current_dir = Path(__file__).parent
    definitions_path = current_dir.parent / "Definitions"
    
    # 确保目录存在
    definitions_path.mkdir(exist_ok=True)
    
    # 创建一个更完整的示例文件
    sample_data = {
        "job": "test job",
        "actions": [
            {"8D": "fire", "damage": [{"potency": 300}]},
            {"8E": "blizzard", "damage": [{"potency": 280}]},
            {"90": "thunder", "damage": [{"potency": 100}]},
            {"5edc": "diagnosis", "heal": [{"potency": 450}]},
            {"5ede": "prognosis", "heal": [{"potency": 300}]}
        ],
        "statuseffects": [
            {"A1": "thunder", "timeproc": {"type": "dot", "potency": 45, "damagetype": "magic", "maxticks": 8}},
            {"A3": "thunder iii", "timeproc": {"type": "dot", "potency": 50, "damagetype": "magic", "maxticks": 9}}
        ]
    }
    
    sample_file = definitions_path / "TestJob.json"
    with open(sample_file, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 创建示例文件: {sample_file}")

def show_file_content(filepath, start_line=25, end_line=35):
    """显示文件指定行的内容"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"📄 文件内容 ({filepath.name}) 第{start_line}-{end_line}行:")
        print("-" * 50)
        
        for i in range(max(0, start_line-1), min(len(lines), end_line)):
            line_num = i + 1
            line_content = lines[i].rstrip()
            marker = ">>> " if start_line <= line_num <= end_line else "    "
            print(f"{marker}{line_num:3d}: {line_content}")
        
        print("-" * 50)
        
    except Exception as e:
        print(f"❌ 无法读取文件: {e}")

def main():
    """主函数"""
    print("🔧 FFXIV JSON文件验证工具")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "create-sample":
            create_sample_files()
            return
        elif sys.argv[1] == "show-error":
            # 显示出错位置的内容
            current_dir = Path(__file__).parent
            definitions_path = current_dir.parent / "Definitions"
            
            for json_file in definitions_path.glob("*.json"):
                is_valid, error = validate_json_file(json_file)
                if not is_valid and "line 31" in str(error):
                    print(f"🔍 发现第31行错误的文件: {json_file.name}")
                    show_file_content(json_file, 25, 35)
            return
    
    # 默认执行验证
    success = validate_definitions_folder()
    
    if not success:
        print("\n💡 建议操作:")
        print("1. 运行 'python validate_json.py show-error' 查看错误详情")
        print("2. 运行 'python validate_json.py create-sample' 创建示例文件")
        print("3. 手动检查和修复JSON格式错误")
        print("4. 确保所有JSON文件使用UTF-8编码")

if __name__ == "__main__":
    main()