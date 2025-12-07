# mykb - Wikipedia 术语词库生成工具

**作者**：Marshal Wu  
**邮箱**：marshal.wu@gmail.com  
**版本**：1.0.0  
**源码地址**：https://github.com/marshal/mykb（暂未发布至 PyPI，需本地克隆使用）

---

## 一、功能一句话
输入一个主题词，自动把 Wikipedia 上所有相关术语抓下来，整理成 Excel 词库；失败词条可补丁重跑；也能只统计/列出相关术语。

---

## 二、第一次运行（本地安装）
```bash
# 1. 克隆代码
git clone https://github.com/marshal/mykb.git
cd mykb

# 2. 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate        # Windows 用 venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt
# 或者
pip install wikipedia markdownify pandas openpyxl tqdm

# 4. 以“可编辑”方式安装本工具，生成命令行入口
pip install -e .
```

安装完成后，命令行任意目录即可使用 `mykb` 指令。  
（若提示找不到命令，请确认虚拟环境已激活，或改用 `python -m mykb.cli …` 临时调用。）

---

## 三、核心用法速查
| 目的 | 命令示例 | 说明 |
|---|---|---|
| 完整生成词库 | `mykb 深度学习` | 自动抓相关术语→获取正文→输出 `深度学习_术语词库_*.xlsx` |
| 只统计/列表 | `mykb 深度学习 -c -l` | 不抓正文，仅显示术语数量与列表；可追加保存到 txt |
| 补丁重跑 | `mykb 深度学习 -p` | 读取上次失败的词条，重新抓取并合并到原词库 |
| 查看帮助 | `mykb -h` | 更多参数说明 |

---

## 四、典型工作流
1. **首轮抓取**  
   `mykb 深度学习`  
   → 生成 `深度学习_术语词库_20251207_143000.xlsx`  
   → 若部分词条失败，会自动生成 `深度学习_failed_terms.txt`

2. **人工消歧/删减**  
   打开 `深度学习_failed_terms.txt`，  
   - 对歧义页自行指定更精确词条，如把 `苹果` 改成 `苹果 (水果)`  
   - 把确实不存在的词条行直接删除  
   保存文件。

3. **补丁补抓**  
   `mykb 深度学习 -p`  
   → 仅重跑列表里剩下的词条  
   → 生成 `深度学习_补丁_*.xlsx` 并自动与最新原词库合并成 `深度学习_术语词库_合并_*.xlsx`  
   → 若全部成功，自动删除 `failed_terms.txt`

4. **只想看看有啥词**  
   `mykb 深度学习 -l -c`  
   终端会列出术语并统计数量，询问是否保存为 txt。

---

## 五、文件命名规则
- 主词库：`{topic}_术语词库_{时间戳}.xlsx`  
- 补丁文件：`{topic}_补丁_{时间戳}.xlsx`  
- 合并文件：`{topic}_术语词库_合并_{时间戳}.xlsx`  
- 失败列表：`{topic}_failed_terms.txt`  
- 术语列表：`{topic}_术语列表_{时间戳}.txt`（分析模式保存）

---

## 六、常见问题
1. **抓取中途报 `PageError` 或 `DisambiguationError` 正常吗？**  
   正常；失败词条会被记录，按流程 2→3 手动修复后补丁即可。

2. **想抓英文维基？**  
   代码已内置中英文回退，优先中文→自动试英文。如需纯英文，可在 `utils.py` 里把 `setup_wikipedia("zh")` 改成 `"en"`。

3. **网络走代理**  
   已在 `cli.py` 默认写入  
   `os.environ["HTTP_PROXY"]=os.environ["HTTPS_PROXY"]="http://myproxy:7890"`  
   如不需要，请把这两行删掉或改成自己的代理地址。

4. **速度太快被封？**  
   `core.py` 里已设 `REQUEST_INTERVAL=1.2~1.5s`，可自行调大。

---

## 七、卸载
```bash
pip uninstall mykb
```
然后删除源码目录即可。

---

## 八、后续计划
- 支持自定义多语言顺序  
- 支持输出为 CSV/MarkDown 格式  
- 支持增量更新（仅抓新增词条）  
欢迎提 Issue & PR！
