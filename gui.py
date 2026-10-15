"""
主界面程序
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import json
import os
import subprocess
import time
import win32gui
import win32process
import win32con
import base64
import re
from page_archiver import PageArchiver
from config import *

class ArchiveGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("网页归档工具")
        self.root.geometry("800x600")
        
        # 战斧浏览器配置
        self.zhanfu_browser_path = r"D:\Program Files (x86)\zhanfubrowser\4.2.0.8\Core\zhanfubrowser.exe"
        self.zhanfu_user_data = r"C:\Users\Administrator\AppData\Local\zhanfubrowser_v2_1\UserData\1685142"
        
        # 战斧浏览器特征
        self.zhanfu_identifiers = {
            "process_name": "zhanfubrowser.exe",
            "cmd_patterns": [
                "--browser_id=",
                "store_data_path=NQROxfI4aSnmSex7nYm7kEyQsDWbtnhuh5UPwxDcQ54whyy5vclEtxdez6BHmNgX7a0PRinp1I8"
            ]
        }
        
        # 窗口监听相关
        self.browser_process = None
        self.window_titles = set()
        self.is_monitoring = False
        
        # 加载配置
        self.config_file = "gui_config.json"
        self.config = self.load_config()
        
        # 初始化归档器
        self.archiver = PageArchiver(
            archive_dir=ARCHIVE_DIR,
            urls_file=ARCHIVE_URLS_FILE,
            whitelist_domains=WHITELIST_DOMAINS,
            max_archive_size=MAX_ARCHIVE_SIZE,
            archive_interval=ARCHIVE_INTERVAL
        )
        
        self.setup_ui()
        
    def decrypt_zhanfu_cmd(self, cmdline):
        """解密战斧浏览器命令行参数"""
        try:
            # 提取加密的存储路径
            encoded = cmdline.split('store_data_path=')[-1]
            # 特殊Base64解码（带自定义移位）
            decoded = bytes([(b - 8) % 256 for b in base64.b64decode(encoded)])
            data_path = decoded.decode('gbk').rstrip('\x00')
            return {"storage_path": data_path}
        except Exception as e:
            print(f"解密命令行失败: {e}")
            return None
            
    def find_zhanfu_windows(self):
        """查找战斧浏览器窗口"""
        hwnds = []
        def callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                try:
                    title = win32gui.GetWindowText(hwnd)
                    if title:  # 只处理有标题的窗口
                        print(f"发现窗口: {title}")  # 调试信息
                        if "TK-" in title:  # 放宽匹配条件
                            hwnds.append((hwnd, title))
                except:
                    pass
            return True
        win32gui.EnumWindows(callback, None)
        return hwnds
        
    def monitor_windows(self):
        """监听窗口变化"""
        print("开始监听窗口...")
        last_titles = set()
        
        while self.is_monitoring:
            try:
                # 获取所有窗口
                current_windows = self.find_zhanfu_windows()
                current_titles = {title for _, title in current_windows}
                
                # 检查新窗口
                new_titles = current_titles - last_titles
                for title in new_titles:
                    print(f"检测到新窗口: {title}")
                    self.root.after(0, lambda t=title: self.handle_new_window(t))
                
                # 更新窗口列表
                last_titles = current_titles
                
            except Exception as e:
                print(f"监听错误: {e}")
                import traceback
                traceback.print_exc()
                
            time.sleep(0.5)
            
    def handle_new_window(self, title):
        """处理新窗口"""
        print(f"\n处理窗口标题: {title}")
        
        # 尝试从URL中提取ID
        if " - " in title:
            url = title.split(" - ")[0]
            print(f"提取到URL: {url}")
            
            # 尝试从URL中提取ID
            if "user/" in url:
                try:
                    # 假设ID在URL的最后一个部分
                    user_id = url.split("user/")[1].split("/")[0]
                    print(f"提取到用户ID: {user_id}")
                    
                    # 更新界面
                    self.update_ui(f"用户ID: {user_id}")
                    # 保存到归档器
                    self.archiver.archived_urls.add(user_id)
                    self.archiver.save_urls_to_file()
                except Exception as e:
                    print(f"提取ID失败: {e}")
                    
    def load_config(self):
        """加载配置"""
        default_config = {
            "filter_text": "",
            "window_size": "800x600",
            "browser_path": r"D:\Program Files (x86)\zhanfubrowser\4.2.0.8\Core\zhanfubrowser.exe",
            "user_data": r"C:\Users\Administrator\AppData\Local\zhanfubrowser_v2_1\UserData\1685142"
        }
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
        return default_config
        
    def save_config(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")
            
    def setup_ui(self):
        """设置用户界面"""
        # 控制面板
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)
        
        # 开始/停止按钮
        self.start_button = ttk.Button(control_frame, text="开始归档", command=self.toggle_archiving)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        # 状态标签
        self.status_label = ttk.Label(control_frame, text="状态: 未开始")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # 筛选框
        filter_frame = ttk.Frame(control_frame)
        filter_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filter_frame, text="筛选:").pack(side=tk.LEFT)
        self.filter_entry = ttk.Entry(filter_frame, width=30)
        self.filter_entry.pack(side=tk.LEFT, padx=5)
        self.filter_entry.insert(0, self.config.get("filter_text", ""))
        self.filter_entry.bind("<KeyRelease>", self.apply_filter)
        
        # 统计信息
        stats_frame = ttk.Frame(control_frame)
        stats_frame.pack(side=tk.RIGHT)
        
        self.total_label = ttk.Label(stats_frame, text="总归档: 0")
        self.total_label.pack(side=tk.LEFT, padx=5)
        
        # 网址列表
        self.url_list = scrolledtext.ScrolledText(self.root, wrap=tk.WORD)
        self.url_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 设置字体
        self.url_list.configure(font=('Courier', 10))
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def apply_filter(self, event=None):
        """应用筛选"""
        filter_text = self.filter_entry.get().lower()
        self.config["filter_text"] = filter_text
        
        # 清空列表
        self.url_list.delete(1.0, tk.END)
        
        # 重新显示符合条件的URL
        for url in self.archiver.archived_urls:
            if filter_text in url.lower():
                self.url_list.insert(tk.END, f"{url}\n")
                
    def toggle_archiving(self):
        """切换归档状态"""
        if not self.archiver.is_archiving:
            self.start_archiving()
        else:
            self.stop_archiving()
            
    def start_archiving(self):
        """开始归档"""
        self.archiver.start_archiving()
        self.start_button.configure(text="停止归档")
        self.status_label.configure(text="状态: 正在启动浏览器...")
        
        # 启动浏览器
        self.run_browser()
        
    def stop_archiving(self):
        """停止归档"""
        self.archiver.stop_archiving()
        self.is_monitoring = False
        self.start_button.configure(text="开始归档")
        self.status_label.configure(text="状态: 已停止")
        
        # 关闭浏览器进程
        if self.browser_process:
            self.browser_process.terminate()
            self.browser_process = None
        
    def run_browser(self):
        """运行战斧浏览器"""
        try:
            print("正在启动浏览器...")
            # 启动战斧浏览器
            cmd = [
                self.config.get("browser_path", self.zhanfu_browser_path),
                f"--user-data-dir={self.config.get('user_data', self.zhanfu_user_data)}",
                "--disable-gpu",
                "--silent-debugger-extension-api",
                "--enable-features=QuietNotificationPrompts",
                "--disable-features=CalculateNativeWinOcclusion",
                "--remote-debugging-port=9222",  # 启用调试模式
                "--enable-logging=stderr"  # 启用日志
            ]
            
            print(f"启动命令: {' '.join(cmd)}")
            
            # 启动浏览器并保存进程
            self.browser_process = subprocess.Popen(cmd)
            print("浏览器进程已启动")
            
            # 等待浏览器启动
            time.sleep(3)
            print("等待浏览器启动完成")
            
            # 启动窗口监听
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self.monitor_windows)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            
            # 更新状态
            self.status_label.configure(text="状态: 浏览器已启动")
            print("浏览器已启动，开始监听窗口变化")
            
        except Exception as e:
            print(f"启动浏览器失败: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("错误", f"启动浏览器失败: {str(e)}")
                
    def update_ui(self, content):
        """更新界面"""
        # 在主线程中更新UI
        self.root.after(0, lambda: self._update_ui_internal(content))
        
    def _update_ui_internal(self, content):
        """内部UI更新方法"""
        # 更新网址列表
        self.url_list.insert(tk.END, f"{content}\n")
        self.url_list.see(tk.END)
        
        # 更新统计信息
        total = len(self.archiver.archived_urls)
        self.total_label.configure(text=f"总归档: {total}")
        
    def on_closing(self):
        """窗口关闭事件处理"""
        # 保存配置
        self.config["window_size"] = self.root.geometry()
        self.save_config()
        
        # 停止归档
        if self.archiver.is_archiving:
            self.stop_archiving()
            
        # 关闭窗口
        self.root.destroy()
        
    def run(self):
        """运行程序"""
        # 设置窗口大小
        if "window_size" in self.config:
            self.root.geometry(self.config["window_size"])
            
        self.root.mainloop()

if __name__ == "__main__":
    app = ArchiveGUI()
    app.run() 