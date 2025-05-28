export function getCorrectPdfViewerUrl(pdfPathOrUrl: string | undefined | null): string {
  if (!pdfPathOrUrl) {
    return ''; // 或者返回一个错误提示/占位符 URL
  }

  // 从环境变量中读取基础 URL，如果未定义，则回退到默认值或抛出错误
  const attachmentBaseUrl = import.meta.env.VITE_ATTACHMENT_BASE_URL || 'http://localhost:8088'; // 提供一个回退值或进行错误处理
  // 注意：在生产环境中，确保 VITE_ATTACHMENT_BASE_URL 已正确设置。
  // 你也可以在这里添加更严格的检查，例如：
  // if (!import.meta.env.VITE_ATTACHMENT_BASE_URL) {
  //   console.error("错误：环境变量 VITE_ATTACHMENT_BASE_URL 未设置！");
  //   return '#error-env-not-set'; // 或其他错误指示
  // }
  // const attachmentBaseUrl = import.meta.env.VITE_ATTACHMENT_BASE_URL;

  const viewerRoute = '/native-pdf-viewer?url=';
  let fullPdfUrl = '';

  try {
    // 检查是否已经是包含协议的完整URL
    if (pdfPathOrUrl.startsWith('http://') || pdfPathOrUrl.startsWith('https://')) {
      const urlObj = new URL(pdfPathOrUrl);
      // 如果主机名是我们期望的服务器（从 attachmentBaseUrl 解析），并且端口不正确，则修正端口
      const baseHostname = new URL(attachmentBaseUrl).hostname;
      const basePort = new URL(attachmentBaseUrl).port;

      if (urlObj.hostname === baseHostname && urlObj.port !== basePort) {
        urlObj.port = basePort;
      }
      fullPdfUrl = urlObj.toString();
    } 
    // 检查是否是期望的相对路径 /attachment/
    else if (pdfPathOrUrl.startsWith('/attachment/')) {
      fullPdfUrl = attachmentBaseUrl + pdfPathOrUrl;
    } 
    // 其他情况
    else {
      if (pdfPathOrUrl.includes('://')) {
         fullPdfUrl = pdfPathOrUrl; // 其他协议，保持原样
      } else {
        fullPdfUrl = attachmentBaseUrl.endsWith('/') || pdfPathOrUrl.startsWith('/')
                   ? attachmentBaseUrl + pdfPathOrUrl
                   : attachmentBaseUrl + '/' + pdfPathOrUrl;
        console.warn(`PDF path format '${pdfPathOrUrl}' was not absolute or /attachment/. Prefixed with base URL: ${fullPdfUrl}`);
      }
    }
  } catch (e) {
    console.error(`Error processing PDF URL '${pdfPathOrUrl}' with base '${attachmentBaseUrl}':`, e);
    return `${viewerRoute}${encodeURIComponent(pdfPathOrUrl)}`; 
  }
  
  return `${viewerRoute}${encodeURIComponent(fullPdfUrl)}`;
} 