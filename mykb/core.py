import os
import time
import pandas as pd
from tqdm import tqdm
from datetime import datetime
import wikipedia
from .utils import (
    setup_wikipedia, 
    get_related_terms, 
    fetch_page_content, 
    save_failed_terms,
    load_failed_terms,
    is_valid_term
)

def analyze_mode(topic, count_flag, list_flag):
    """分析模式：只统计和列出术语，不获取内容"""
    print(f"=== 分析模式 ===")
    print(f"主题: {topic}")
    
    # 设置中文环境
    setup_wikipedia("zh")
    
    # 获取相关术语
    terms, total_count = get_related_terms(topic)
    
    if not terms:
        print("未获取到相关术语")
        return
    
    # 显示统计信息
    if count_flag:
        print(f"\n相关术语总数: {total_count}")
        print(f"筛选后术语数: {len(terms)}")
    
    # 显示术语列表
    if list_flag:
        print(f"\n相关术语列表:")
        print("-" * 50)
        for i, term in enumerate(terms, 1):
            print(f"{i:3d}. {term}")
        print("-" * 50)
    
    # 询问是否保存到文件
    if list_flag:
        save_choice = input("\n是否将术语列表保存到文件？(y/n): ").strip().lower()
        if save_choice == 'y':
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            list_file = f"{topic}_术语列表_{timestamp}.txt"
            with open(list_file, 'w', encoding='utf-8') as f:
                f.write(f"主题: {topic}\n")
                f.write(f"相关术语总数: {total_count}\n")
                f.write(f"筛选后术语数: {len(terms)}\n")
                f.write("\n术语列表:\n")
                for i, term in enumerate(terms, 1):
                    f.write(f"{i:3d}. {term}\n")
            print(f"术语列表已保存到: {list_file}")

def normal_mode(topic):
    """正常模式：根据主题获取相关术语并生成词库"""
    print(f"开始处理主题: {topic}")
    
    # 设置中文环境
    setup_wikipedia("zh")
    
    try:
        # 抓取主词条
        print("获取主词条页面...")
        page = wikipedia.page(topic)
        
        # 获取相关术语
        print("获取相关术语...")
        related_terms = page.links
        
        # 术语筛选
        terms = list({t for t in related_terms if is_valid_term(t)})
        print(f"共获取术语: {len(terms)}")
        
        # 结果存储
        results = []
        failed_terms = []
        
        # 请求间隔
        REQUEST_INTERVAL = 1.2
        
        # 遍历抓取每个术语
        for term in tqdm(terms, desc="抓取词条内容"):
            content_md = fetch_page_content(term)
            if content_md:
                results.append({
                    "title": term,
                    "content": content_md
                })
            else:
                failed_terms.append(term)
            
            time.sleep(REQUEST_INTERVAL)
        
        # 输出Excel
        if results:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"{topic}_术语词库_{timestamp}.xlsx"
            df = pd.DataFrame(results)
            df.to_excel(output_file, index=False)
            print(f"成功获取 {len(results)} 个词条，已输出到: {output_file}")
        else:
            print("未成功获取任何词条")
        
        # 保存失败词条
        if failed_terms:
            failed_file = save_failed_terms(failed_terms, topic)
            print(f"有 {len(failed_terms)} 个词条获取失败，已保存到: {failed_file}")
        else:
            print("所有词条都成功获取！")
        
        return len(results), len(failed_terms)
        
    except Exception as e:
        print(f"处理主题 '{topic}' 时发生错误: {e}")
        return 0, 0

def patch_mode():
    """补丁模式：处理之前失败的词条"""
    print("=== 补丁模式 ===")
    
    # 获取所有失败词条文件
    failed_files = [f for f in os.listdir('.') if f.endswith('_failed_terms.txt')]
    
    if not failed_files:
        print("未找到失败词条文件")
        return
    
    for failed_file in failed_files:
        # 从文件名提取主题
        topic = failed_file.replace('_failed_terms.txt', '')
        print(f"\n处理主题: {topic}")
        
        # 加载失败词条
        failed_terms = load_failed_terms(topic)
        if not failed_terms:
            print(f"没有失败词条需要处理")
            continue
        
        # 设置中文环境
        setup_wikipedia("zh")
        
        # 结果存储
        results = []
        new_failed_terms = []
        
        # 请求间隔
        REQUEST_INTERVAL = 1.5
        
        # 遍历抓取失败词条
        for term in tqdm(failed_terms, desc="抓取失败词条"):
            content_md = fetch_page_content(term)
            if content_md:
                results.append({
                    "title": term,
                    "content": content_md
                })
            else:
                new_failed_terms.append(term)
            
            time.sleep(REQUEST_INTERVAL)
        
        # 输出补丁Excel
        if results:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            patch_file = f"{topic}_补丁_{timestamp}.xlsx"
            df_patch = pd.DataFrame(results)
            df_patch.to_excel(patch_file, index=False)
            print(f"补丁文件已生成: {patch_file}")
            
            # 尝试合并到原文件
            try:
                # 查找最新的原文件
                original_files = [f for f in os.listdir('.') if f.startswith(f"{topic}_术语词库_") and f.endswith('.xlsx')]
                if original_files:
                    # 按修改时间排序，取最新的
                    original_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
                    original_file = original_files[0]
                    
                    df_original = pd.read_excel(original_file)
                    df_merged = pd.concat([df_original, df_patch], ignore_index=True)
                    
                    merged_file = f"{topic}_术语词库_合并_{timestamp}.xlsx"
                    df_merged.to_excel(merged_file, index=False)
                    print(f"合并文件已生成: {merged_file}")
                else:
                    print(f"未找到原始词库文件，跳过合并")
            except Exception as e:
                print(f"合并文件时出错: {e}")
        
        # 更新失败词条文件
        if new_failed_terms:
            save_failed_terms(new_failed_terms, topic)
            print(f"仍有 {len(new_failed_terms)} 个词条失败，已更新失败词条文件")
        else:
            # 所有词条都成功，删除失败词条文件
            os.remove(failed_file)
            print(f"所有词条都成功获取，已删除失败词条文件: {failed_file}")
        
        print(f"处理完成: 成功 {len(results)}, 失败 {len(new_failed_terms)}")