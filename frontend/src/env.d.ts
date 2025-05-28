/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_ATTACHMENT_BASE_URL: string;
  // 在这里定义其他你使用的环境变量...
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
} 