/**
 * 自动页面归档插件
 * 监听新标签页打开事件，保存页面内容后自动关闭
 */

// 存储归档状态
let isArchiving = false;
let archivedUrls = new Set();
let processingTabs = new Set();

/**
 * 初始化插件
 */
chrome.runtime.onInstalled.addListener(() => {
  console.log('[AutoPageArchiver] 插件已安装');
  // 初始化存储
  chrome.storage.local.set({ archivedUrls: [] });
});

/**
 * 监听来自popup的消息
 */
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('[AutoPageArchiver] 收到消息:', request);
  
  if (request.action === 'startArchiving') {
    isArchiving = true;
    archivedUrls.clear();
    processingTabs.clear();
    console.log('[AutoPageArchiver] 开始归档模式');
    sendResponse({ status: 'started' });
  } else if (request.action === 'stopArchiving') {
    isArchiving = false;
    console.log('[AutoPageArchiver] 停止归档模式');
    sendResponse({ status: 'stopped' });
  } else if (request.action === 'getStatus') {
    sendResponse({ isArchiving });
  }
});

/**
 * 处理页面归档
 */
async function processPage(tabId, url) {
  if (!isArchiving) {
    console.log('[AutoPageArchiver] 归档模式未启动，忽略');
    return;
  }
  
  if (processingTabs.has(tabId)) {
    console.log('[AutoPageArchiver] 标签页正在处理中:', tabId);
    return;
  }
  
  processingTabs.add(tabId);
  console.log('[AutoPageArchiver] 开始处理页面:', { tabId, url });
  
  try {
    // 等待页面加载完成
    console.log('[AutoPageArchiver] 等待页面加载...');
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // 检查标签页是否还存在
    const tab = await chrome.tabs.get(tabId);
    if (!tab) {
      console.log('[AutoPageArchiver] 标签页已关闭');
      return;
    }
    
    // 获取页面内容
    console.log('[AutoPageArchiver] 尝试获取页面内容...');
    const [result] = await chrome.scripting.executeScript({
      target: { tabId: tabId },
      function: () => {
        console.log('[AutoPageArchiver] 正在执行脚本...');
        return {
          html: document.documentElement.outerHTML,
          url: window.location.href,
          title: document.title
        };
      }
    });
    
    console.log('[AutoPageArchiver] 脚本执行结果:', result);
    
    if (result && result.result) {
      const { html, url, title } = result.result;
      
      // 检查URL是否已经归档过
      if (archivedUrls.has(url)) {
        console.log('[AutoPageArchiver] URL已归档过:', url);
        chrome.tabs.remove(tabId);
        return;
      }
      
      // 保存页面内容
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const filename = `archive_${timestamp}_${title.replace(/[^a-z0-9]/gi, '_')}.html`;
      
      console.log('[AutoPageArchiver] 准备保存文件:', filename);
      
      const blob = new Blob([html], { type: 'text/html' });
      const urlObject = URL.createObjectURL(blob);
      
      await chrome.downloads.download({
        url: urlObject,
        filename: filename,
        saveAs: false
      });
      
      console.log('[AutoPageArchiver] 文件保存成功');
      
      // 记录已归档的URL
      archivedUrls.add(url);
      chrome.storage.local.get(['archivedUrls'], (result) => {
        const urls = result.archivedUrls || [];
        urls.push({ url, timestamp, title });
        chrome.storage.local.set({ archivedUrls: urls });
      });
      
      // 关闭标签页
      console.log('[AutoPageArchiver] 准备关闭标签页');
      chrome.tabs.remove(tabId);
      
      console.log('[AutoPageArchiver] 页面归档完成:', { url, title });
    } else {
      console.log('[AutoPageArchiver] 未获取到页面内容');
    }
  } catch (error) {
    console.error('[AutoPageArchiver] 归档页面时出错:', error);
  } finally {
    processingTabs.delete(tabId);
  }
}

/**
 * 监听新标签页创建事件
 */
chrome.tabs.onCreated.addListener((tab) => {
  console.log('[AutoPageArchiver] 新标签页创建:', tab);
  if (isArchiving && tab.url) {
    processPage(tab.id, tab.url);
  }
});

/**
 * 监听标签页更新事件
 */
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  console.log('[AutoPageArchiver] 标签页更新:', { tabId, changeInfo, tab });
  
  // 检查是否是页面加载完成
  if (changeInfo.status === 'complete' && tab.url && !tab.url.startsWith('chrome://')) {
    console.log('[AutoPageArchiver] 页面加载完成:', tab.url);
    if (isArchiving) {
      processPage(tabId, tab.url);
    }
  }
}); 