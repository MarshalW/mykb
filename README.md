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