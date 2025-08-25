#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import re

def parse_tree_file(file_path):
    """
    解析tree命令输出文件，返回目录和文件的详细信息
    返回: (directories_set, files_set, directory_count, file_count)
    """
    if not os.path.exists(file_path):
        print(f"错误: 文件 {file_path} 不存在")
        return None
    
    directories = set()
    files = set()
    current_path = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line in lines:
            # 移除行号前缀 (如 "10→")
            if '→' in line:
                line = line.split('→', 1)[1]
            
            original_line = line.rstrip('\n\r')
            
            # 跳过空行和标题行
            if (not original_line.strip() or 
                original_line.startswith('卷') or 
                original_line.startswith('PS ') or 
                'PATH 列表' in original_line or
                '>tree' in original_line or
                original_line.startswith('D:\\files\\projects\\')):
                continue
            
            # 计算缩进层级
            indent_level = 0
            clean_line = original_line
            
            # 处理tree结构符号
            if re.match(r'^[│\s]*[├└]─', original_line):
                # 计算缩进层级
                prefix = re.match(r'^([│\s]*)[├└]─', original_line).group(1)
                indent_level = len([c for c in prefix if c == '│']) 
                name = re.sub(r'^[│\s]*[├└]─\s*', '', original_line)
                
                # 构建完整路径
                current_path = current_path[:indent_level]
                if name and name != 'D:.':
                    full_path = '/'.join(current_path + [name])
                    
                    # 判断是目录还是文件
                    if '.' in name.split('/')[-1].split('\\')[-1]:
                        files.add(full_path)
                    else:
                        directories.add(full_path)
                        current_path.append(name)
                        
            elif re.match(r'^[│\s]+[^├└│\s]', original_line):
                # 文件行（缩进但不是树结构符号开头）
                name = original_line.strip()
                if name and '.' in name:
                    full_path = '/'.join(current_path + [name])
                    files.add(full_path)
                    
            elif original_line.strip() and not re.match(r'^[│\s]*$', original_line):
                # 根目录或其他项目
                name = original_line.strip()
                if name and name != 'D:.':
                    if '.' in name:
                        files.add(name)
                    else:
                        directories.add(name)
                        if indent_level == 0:
                            current_path = [name]
                            
    except Exception as e:
        print(f"读取文件 {file_path} 时出错: {e}")
        return None
    
    return directories, files, len(directories), len(files)

def compare_directory_counts(file1_path, file2_path):
    """
    比较两个tree文件中的目录数量差异，并显示具体的变化项目
    """
    print(f"正在比较tree文件:")
    print(f"文件1: {file1_path}")
    print(f"文件2: {file2_path}")
    print("=" * 60)
    
    result1 = parse_tree_file(file1_path)
    result2 = parse_tree_file(file2_path)
    
    if result1 is None or result2 is None:
        return
    
    dirs1, files1, dir_count1, file_count1 = result1
    dirs2, files2, dir_count2, file_count2 = result2
    
    print(f"文件1统计:")
    print(f"  - 目录数: {dir_count1}")
    print(f"  - 文件数: {file_count1}")
    print(f"  - 总计: {dir_count1 + file_count1}")
    
    print(f"\n文件2统计:")
    print(f"  - 目录数: {dir_count2}")
    print(f"  - 文件数: {file_count2}")
    print(f"  - 总计: {dir_count2 + file_count2}")
    
    # 计算差异
    added_dirs = dirs2 - dirs1
    removed_dirs = dirs1 - dirs2
    added_files = files2 - files1
    removed_files = files1 - files2
    
    dir_difference = dir_count2 - dir_count1
    file_difference = file_count2 - file_count1
    total_difference = (dir_count2 + file_count2) - (dir_count1 + file_count1)
    
    print(f"\n" + "=" * 60)
    print(f"详细变化分析:")
    print(f"=" * 60)
    
    # 显示目录变化
    if added_dirs:
        print(f"\n[+] 新增目录 ({len(added_dirs)}个):")
        for dir_name in sorted(added_dirs):
            print(f"    + {dir_name}")
    
    if removed_dirs:
        print(f"\n[-] 删除目录 ({len(removed_dirs)}个):")
        for dir_name in sorted(removed_dirs):
            print(f"    - {dir_name}")
            
    if not added_dirs and not removed_dirs:
        print(f"\n[目录] 没有变化")
    
    # 显示文件变化
    if added_files:
        print(f"\n[+] 新增文件 ({len(added_files)}个):")
        for file_name in sorted(added_files):
            print(f"    + {file_name}")
    
    if removed_files:
        print(f"\n[-] 删除文件 ({len(removed_files)}个):")
        for file_name in sorted(removed_files):
            print(f"    - {file_name}")
            
    if not added_files and not removed_files:
        print(f"\n[文件] 没有变化")
    
    # 总结
    print(f"\n" + "=" * 60)
    print(f"变化总结:")
    print(f"=" * 60)
    print(f"目录: {dir_difference:+d} ({dir_count1} → {dir_count2})")
    print(f"文件: {file_difference:+d} ({file_count1} → {file_count2})")
    print(f"总计: {total_difference:+d} ({dir_count1 + file_count1} → {dir_count2 + file_count2})")

def main():
    parser = argparse.ArgumentParser(description='比较两个tree命令输出文件中的目录和文件数差异')
    parser.add_argument('file1', help='第一个tree输出txt文件路径')
    parser.add_argument('file2', help='第二个tree输出txt文件路径')
    
    args = parser.parse_args()
    
    compare_directory_counts(args.file1, args.file2)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("使用方法: python compare_directories.py <tree文件1> <tree文件2>")
        print("\n功能: 比较两个tree命令输出文件中目录和文件数的差异")
        print("\n示例:")
        print("python compare_directories.py tree1.txt tree2.txt")
        print("\n当前目录中的txt文件:")
        for file in os.listdir('.'):
            if file.endswith('.txt'):
                print(f"  - {file}")
        sys.exit(1)
    
    main()