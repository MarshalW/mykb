import argparse
import sys
from .core import analyze_mode, normal_mode, patch_mode
import os

os.environ['HTTP_PROXY']  = 'http://myproxy:7890'
os.environ['HTTPS_PROXY'] = 'http://myproxy:7890'

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Wikipedia术语词库生成工具',
        epilog="使用示例:\n"
              "  1. 完整生成词库:\n"
              "     mykb 深度学习\n"
              "  2. 分析模式（仅统计和列出术语）:\n"
              "     mykb 深度学习 --count\n"
              "     mykb 深度学习 --list\n"
              "     mykb 深度学习 --count --list\n"
              "  3. 补丁模式（处理失败的词条）:\n"
              "     mykb --patch",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('topic', nargs='?', help='要处理的主题词')
    parser.add_argument('-p', '--patch', action='store_true', help='补丁模式：处理失败的词条')
    parser.add_argument('-c', '--count', action='store_true', help='仅统计相关术语数量')
    parser.add_argument('-l', '--list', action='store_true', help='仅列出相关术语')
    
    args = parser.parse_args()
    
    if args.patch:
        # 补丁模式
        patch_mode()
    elif args.topic:
        # 检查是否有分析模式参数
        if args.count or args.list:
            # 分析模式：只统计和列出术语，不获取内容
            analyze_mode(args.topic, args.count, args.list)
        else:
            # 正常模式：完整获取内容并生成词库
            normal_mode(args.topic)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()