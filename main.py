"""
主程序入口
"""

import os
import sys
from page_archiver import PageArchiver
from config import *

def main():
    """
    主函数
    """
    try:
        # 创建归档目录
        if not os.path.exists(ARCHIVE_DIR):
            os.makedirs(ARCHIVE_DIR)
            
        # 初始化归档器
        archiver = PageArchiver(
            archive_dir=ARCHIVE_DIR,
            urls_file=ARCHIVE_URLS_FILE,
            whitelist_domains=WHITELIST_DOMAINS,
            max_archive_size=MAX_ARCHIVE_SIZE,
            archive_interval=ARCHIVE_INTERVAL
        )
        
        # 启动归档
        print("开始归档...")
        archiver.start_archiving()
        
    except KeyboardInterrupt:
        print("\n程序已停止")
        sys.exit(0)
    except Exception as e:
        print(f"发生错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 