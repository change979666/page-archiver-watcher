from playwright.sync_api import sync_playwright
import time
import json
from datetime import datetime
import os

class PageArchiver:
    def __init__(self, archive_dir="archived_pages", urls_file="archived_urls.json", 
                 whitelist_domains=None, max_archive_size=1000, archive_interval=1):
        """
        初始化页面归档器
        
        Args:
            archive_dir (str): 归档文件保存目录
            urls_file (str): 已归档URL记录文件
            whitelist_domains (list): 白名单域名列表
            max_archive_size (int): 最大归档数量
            archive_interval (int): 归档间隔（秒）
        """
        self.archived_urls = set()
        self.is_archiving = False
        self.archive_dir = archive_dir
        self.urls_file = urls_file
        self.whitelist_domains = whitelist_domains or []
        self.max_archive_size = max_archive_size
        self.archive_interval = archive_interval
        
        # 创建归档目录
        if not os.path.exists(self.archive_dir):
            os.makedirs(self.archive_dir)
            
        # 加载已归档的URL
        self.load_urls_from_file()
        
    def start_archiving(self):
        self.is_archiving = True
        print("开始归档模式")
        
    def stop_archiving(self):
        self.is_archiving = False
        print("停止归档模式")
        
    def save_page(self, page, url):
        if not self.is_archiving:
            return
            
        if url in self.archived_urls:
            print(f"URL已归档过: {url}")
            return
            
        try:
            # 等待页面加载完成
            page.wait_for_load_state("networkidle")
            
            # 获取页面内容
            content = page.content()
            title = page.title()
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"archive_{timestamp}_{title.replace('/', '_')}.html"
            filepath = os.path.join(self.archive_dir, filename)
            
            # 保存页面内容
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
                
            # 记录URL
            self.archived_urls.add(url)
            self.save_urls_to_file()
            
            print(f"页面已归档: {url}")
            print(f"保存位置: {filepath}")
            
        except Exception as e:
            print(f"归档页面时出错: {e}")
            
    def save_urls_to_file(self):
        with open(self.urls_file, "w", encoding="utf-8") as f:
            json.dump(list(self.archived_urls), f, ensure_ascii=False, indent=2)
            
    def load_urls_from_file(self):
        try:
            with open(self.urls_file, "r", encoding="utf-8") as f:
                self.archived_urls = set(json.load(f))
        except FileNotFoundError:
            self.archived_urls = set()

def main():
    print("=" * 50)
    print("页面自动归档工具")
    print("=" * 50)
    print("说明：")
    print("1. 程序会自动打开浏览器")
    print("2. 在浏览器中正常浏览网页")
    print("3. 当点击链接打开新页面时，程序会自动保存并关闭新页面")
    print("4. 按 Ctrl+C 停止程序")
    print("=" * 50)
    
    archiver = PageArchiver()
    
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # 监听新页面打开事件
        context.on("page", lambda new_page: archiver.save_page(new_page, new_page.url))
        
        # 启动归档
        archiver.start_archiving()
        
        try:
            # 保持程序运行
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n停止归档")
            archiver.stop_archiving()
            browser.close()

if __name__ == "__main__":
    main() 