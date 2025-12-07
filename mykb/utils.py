import os
import time
import wikipedia
from markdownify import markdownify as md

# 记录原始语言环境
ORIGINAL_LANG = "zh"

def setup_wikipedia(lang="zh"):
    """设置Wikipedia语言环境"""
    global ORIGINAL_LANG
    ORIGINAL_LANG = lang
    wikipedia.set_lang(lang)

def is_valid_term(term):
    """术语筛选规则"""
    if len(term) > 20:
        return False
    if '列表' in term:
        return False
    if '分类:' in term:
        return False
    if '索引' in term:
        return False
    return True

def fetch_page_content(term, retries=3):
    """尝试获取页面内容，失败重试（支持中英文回退）"""
    current_lang = wikipedia.languages()[ORIGINAL_LANG]  # 获取当前语言
    
    for attempt in range(retries):
        try:
            # 主要尝试：使用当前语言获取页面
            page = wikipedia.page(term)
            return md(page.content)
            
        except wikipedia.exceptions.DisambiguationError:
            print(f"歧义页跳过: {term}")
            return None
            
        except wikipedia.exceptions.PageError as e:
            # 如果是中文环境下找不到页面，尝试切换到英文
            if ORIGINAL_LANG == "zh":
                print(f"中文页面不存在 {term}，尝试英文...")
                
                try:
                    # 切换到英文环境
                    wikipedia.set_lang("en")
                    
                    # 获取英文页面
                    page = wikipedia.page(term)
                    content = md(page.content)
                    
                    print(f"英文页面找到: {term}")
                    
                    # 恢复原始语言环境
                    wikipedia.set_lang(ORIGINAL_LANG)
                    return content
                    
                # except wikipedia.exceptions.DisambiguationError:
                #     print(f"英文歧义页跳过: {term}")
                #     wikipedia.set_lang(ORIGINAL_LANG)
                #     return None
                except wikipedia.exceptions.DisambiguationError:
                    fallback = term  # 你 term 已经是 "Matt Stephens (author)"
                    try:
                        page = wikipedia.page(fallback, auto_suggest=False)
                        return md(page.content)
                    except Exception:
                        print(f"英文歧义页跳过: {term}")
                        return None
                    finally:
                        wikipedia.set_lang(ORIGINAL_LANG)
                    
                except wikipedia.exceptions.PageError:
                    print(f"英文页面也不存在: {term}")
                    wikipedia.set_lang(ORIGINAL_LANG)
                    
                    # 英文也没有，检查是否要重试
                    if attempt < retries - 1:
                        wait_time = 2 * (attempt + 1)
                        print(f"尝试 {attempt+1}/{retries}，等待 {wait_time}秒")
                        time.sleep(wait_time)
                    else:
                        return None
                        
                except Exception as e:
                    print(f"英文页面获取异常 {term}: {e}")
                    wikipedia.set_lang(ORIGINAL_LANG)
                    return None
                    
            else:
                # 当前不是中文环境，直接返回None
                print(f"页面不存在: {term}")
                return None
                
        except Exception as e:
            if attempt < retries - 1:
                wait_time = 2 * (attempt + 1)
                print(f"抓取失败 {term}, 尝试 {attempt+1}/{retries}, 等待 {wait_time}秒: {e}")
                time.sleep(wait_time)
            else:
                print(f"抓取失败 {term}, 放弃: {e}")
                return None
                
    return None

def fetch_page_content_with_backup(term, retries=3, backup_langs=["en"]):
    """更灵活的多语言回退版本，可以指定备用语言列表"""
    original_lang = wikipedia.languages()[ORIGINAL_LANG]
    tried_langs = [ORIGINAL_LANG]
    
    for attempt in range(retries):
        try:
            # 尝试当前语言
            page = wikipedia.page(term)
            return md(page.content)
            
        except wikipedia.exceptions.DisambiguationError:
            print(f"歧义页跳过: {term} (语言: {tried_langs[-1]})")
            return None
            
        except wikipedia.exceptions.PageError as e:
            # 检查是否有备用语言可以尝试
            available_backup_langs = [lang for lang in backup_langs if lang not in tried_langs]
            
            if available_backup_langs:
                # 切换到下一个备用语言
                next_lang = available_backup_langs[0]
                print(f"{tried_langs[-1]}页面不存在 {term}，尝试{next_lang}...")
                
                try:
                    wikipedia.set_lang(next_lang)
                    tried_langs.append(next_lang)
                    
                    page = wikipedia.page(term)
                    content = md(page.content)
                    
                    print(f"{next_lang}页面找到: {term}")
                    return content
                    
                except (wikipedia.exceptions.DisambiguationError, 
                       wikipedia.exceptions.PageError, Exception):
                    # 如果这个备用语言也失败，继续循环会尝试下一个备用语言
                    continue
                    
            else:
                # 所有语言都尝试过了，都没有找到
                print(f"在所有语言中均未找到: {term} ({', '.join(tried_langs)})")
                wikipedia.set_lang(ORIGINAL_LANG)  # 恢复原始语言
                return None
                
        except Exception as e:
            if attempt < retries - 1:
                wait_time = 2 * (attempt + 1)
                print(f"抓取失败 {term} (语言: {tried_langs[-1]}), 尝试 {attempt+1}/{retries}, 等待 {wait_time}秒: {e}")
                time.sleep(wait_time)
            else:
                print(f"抓取失败 {term}, 放弃: {e}")
                wikipedia.set_lang(ORIGINAL_LANG)  # 恢复原始语言
                return None
                
    wikipedia.set_lang(ORIGINAL_LANG)  # 确保最后恢复原始语言
    return None

def save_failed_terms(failed_terms, topic):
    """保存失败词条到文件"""
    failed_file = f"{topic}_failed_terms.txt"
    with open(failed_file, 'w', encoding='utf-8') as f:
        for term in failed_terms:
            f.write(f"{term}\n")
    print(f"失败词条已保存到: {failed_file}")
    return failed_file

def load_failed_terms(topic):
    """加载失败词条文件"""
    failed_file = f"{topic}_failed_terms.txt"
    if not os.path.exists(failed_file):
        print(f"未找到失败词条文件: {failed_file}")
        return []
    
    with open(failed_file, 'r', encoding='utf-8') as f:
        failed_terms = [line.strip() for line in f if line.strip()]
    print(f"从文件加载了 {len(failed_terms)} 个失败词条")
    return failed_terms

def get_related_terms(topic, lang="zh"):
    """获取相关术语列表，支持指定语言"""
    original_lang = ORIGINAL_LANG
    try:
        # 临时切换到指定语言
        if lang != ORIGINAL_LANG:
            wikipedia.set_lang(lang)
            
        print(f"获取主题 '{topic}' 的相关术语（语言: {lang}）...")
        page = wikipedia.page(topic, auto_suggest=False)
        related_terms = page.links
        terms = list({t for t in related_terms if is_valid_term(t)})
        
        # 恢复原始语言
        if lang != ORIGINAL_LANG:
            wikipedia.set_lang(original_lang)
            
        return terms, len(terms)
    except Exception as e:
        print(f"获取相关术语时出错（语言: {lang}）: {e}")
        # 确保恢复原始语言
        wikipedia.set_lang(original_lang)
        return [], 0

def get_related_terms_multilingual(topic, langs=["zh", "en"]):
    """从多个语言获取相关术语，合并结果"""
    all_terms = []
    
    for lang in langs:
        try:
            wikipedia.set_lang(lang)
            page = wikipedia.page(topic, auto_suggest=False)
            related_terms = page.links
            valid_terms = [t for t in related_terms if is_valid_term(t)]
            all_terms.extend(valid_terms)
            print(f"从{lang}获取到{len(valid_terms)}个相关术语")
        except Exception as e:
            print(f"从{lang}获取相关术语时出错: {e}")
            continue
    
    # 恢复原始语言
    wikipedia.set_lang(ORIGINAL_LANG)
    
    # 去重
    unique_terms = list(set(all_terms))
    return unique_terms, len(unique_terms)

# 使用示例
if __name__ == "__main__":
    # 设置语言
    setup_wikipedia("zh")
    
    # 测试术语
    test_terms = [
        "Python (programming language)",  # 英文有，中文也有
        "Machine learning",               # 英文有，中文也有
        "Quantum computing",              # 英文有，中文也有
        "Symmetric monoidal category",    # 英文有，中文可能没有
        "Non-commutative geometry",       # 英文有，中文可能没有
    ]
    
    print("测试中英文回退机制:")
    print("-" * 50)
    
    for term in test_terms:
        print(f"\n处理术语: {term}")
        content = fetch_page_content(term)
        
        if content:
            print(f"✓ 获取成功，内容长度: {len(content)} 字符")
            # 保存内容到文件
            filename = f"data/{term.replace(' ', '_').replace('(', '').replace(')', '')}.md"
            os.makedirs("data", exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"# {term}\n\n")
                f.write(content)
            print(f"  已保存到: {filename}")
        else:
            print(f"✗ 获取失败")
    
    print("\n" + "=" * 50)
    print("测试多语言版本:")
    
    for term in ["Category theory", "Homological algebra"]:
        print(f"\n处理术语: {term}")
        content = fetch_page_content_with_backup(term, backup_langs=["zh", "en", "fr", "de"])
        
        if content:
            print(f"✓ 获取成功")
        else:
            print(f"✗ 获取失败")