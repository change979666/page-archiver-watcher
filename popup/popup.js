/**
 * 自动页面归档插件的弹出界面逻辑
 */

// 获取DOM元素
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const statusText = document.getElementById('statusText');
const archivedCount = document.getElementById('archivedCount');
const urlList = document.getElementById('urlList');

// 更新状态显示
function updateStatus(isArchiving) {
  statusText.textContent = isArchiving ? '正在归档...' : '未启动';
  startBtn.disabled = isArchiving;
  stopBtn.disabled = !isArchiving;
}

// 更新归档统计
function updateStats() {
  chrome.storage.local.get(['archivedUrls'], (result) => {
    const urls = result.archivedUrls || [];
    archivedCount.textContent = urls.length;
    
    // 更新URL列表
    urlList.innerHTML = '';
    urls.forEach(item => {
      const div = document.createElement('div');
      div.className = 'url-item';
      div.textContent = `${item.timestamp} - ${item.url}`;
      urlList.appendChild(div);
    });
  });
}

// 开始归档
startBtn.addEventListener('click', () => {
  chrome.runtime.sendMessage({ action: 'startArchiving' }, (response) => {
    if (response.status === 'started') {
      updateStatus(true);
    }
  });
});

// 停止归档
stopBtn.addEventListener('click', () => {
  chrome.runtime.sendMessage({ action: 'stopArchiving' }, (response) => {
    if (response.status === 'stopped') {
      updateStatus(false);
    }
  });
});

// 初始化
chrome.runtime.sendMessage({ action: 'getStatus' }, (response) => {
  updateStatus(response.isArchiving);
  updateStats();
});

// 监听存储变化
chrome.storage.onChanged.addListener((changes) => {
  if (changes.archivedUrls) {
    updateStats();
  }
}); 