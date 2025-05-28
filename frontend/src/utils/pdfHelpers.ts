/**
 * PDF 查看器辅助函数
 * 用于处理 PDF 文件的 URL 和查看路径
 */

/**
 * 获取正确的 PDF 查看器 URL
 * @param pdfPathOrUrl PDF 文件的路径或 URL
 * @returns 包含正确端口的完整 PDF 查看器 URL
 */
export function getCorrectPdfViewerUrl(pdfPathOrUrl: string | undefined | null): string {
  if (!pdfPathOrUrl) {
    return ''; // 或者返回一个错误提示/占位符 URL
  }

  // 从环境变量中读取基础 URL，如果未定义，则回退到默认值
  const attachmentBaseUrl = import.meta.env.VITE_ATTACHMENT_BASE_URL || 'http://192.9.200.105:8088';
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