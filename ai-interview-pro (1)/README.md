<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# AI Interview Pro - 前端应用

AI 面试练习平台的前端项目，提供交互式面试练习、实时分析、AI 教练等功能。

## 🚀 技术栈

- **框架:** React 19.2.0 + TypeScript
- **构建工具:** Vite 6.4.1
- **样式:** Tailwind CSS 4.1.17（PostCSS）
- **UI 组件:** Lucide React（图标）
- **图表:** Recharts 2.12.2
- **动画:** 纯 CSS 3D 动画

## 📋 前置要求

- **Node.js:** v18 或更高版本
- **包管理器:** pnpm（推荐）或 npm

### 安装 pnpm（如果还没安装）

```bash
npm install -g pnpm
```bash

或使用 Volta（如果已安装）：

```bash
volta install pnpm
```

## 🛠️ 快速开始

### 1. 克隆或下载项目

```bash
git clone <repository-url>
cd ai-interview-pro
```bash

### 2. 安装依赖

使用 pnpm（推荐）：

```bash
pnpm install
```

或使用 npm（如果遇到依赖冲突）：

```bash
npm install --legacy-peer-deps
```bash

### 3. 启动开发服务器

```bash
pnpm dev
```

或使用 npm：

```bash
npm run dev
```text

### 4. 打开浏览器

访问 [http://localhost:3000](http://localhost:3000)

## 📁 项目结构

```
ai-interview-pro/
├── components/          # 公共组件
│   ├── ui/             # 基础 UI 组件（Button, Card 等）
│   ├── Sidebar.tsx     # 侧边栏导航
│   ├── SystemCheckModal.tsx  # 系统检查弹窗
│   └── ThreeBackground.tsx   # CSS 3D 动画背景
├── pages/              # 页面组件
│   ├── Landing.tsx     # 欢迎页
│   ├── Overview.tsx    # 概览页
│   ├── Record.tsx      # 录制面试
│   ├── Analysis.tsx    # 分析结果
│   ├── History.tsx     # 历史记录
│   └── Settings.tsx    # 设置页面
├── App.tsx             # 主应用组件
├── index.tsx           # 应用入口
├── types.ts            # TypeScript 类型定义
├── index.css           # Tailwind CSS 入口
├── tailwind.config.js  # Tailwind 配置
├── postcss.config.js   # PostCSS 配置
└── vite.config.ts      # Vite 配置
```text

## 🎯 主要功能

- **Landing 欢迎页** - 带有 3D 动画背景的启动页
- **Overview 概览** - 查看面试统计和快速操作
- **Record 录制** - 进行模拟面试并录制
- **Analysis 分析** - 查看面试表现分析
- **History 历史** - 浏览历史面试记录
- **Coach AI 教练** - AI 驱动的面试辅导
- **Question Bank 题库** - 面试问题库
- **Settings 设置** - 个人资料和 AI 配置

## 🐛 常见问题

### 问题 1：依赖冲突错误

**错误信息：** `ERESOLVE unable to resolve dependency tree`

**解决方案：**

```bash
# 使用 pnpm
pnpm install

# 或使用 npm with legacy peer deps
npm install --legacy-peer-deps
```

### 问题 2：504 Outdated Optimize Dep

**错误信息：** `504 (Outdated Optimize Dep)`

**解决方案：** 清理 Vite 缓存

```bash
# 删除缓存
rm -rf node_modules/.vite dist

# 重新启动
pnpm dev
```bash

### 问题 3：Tailwind 样式不生效

**解决方案：** 确保已安装 Tailwind 依赖并配置正确

```bash
pnpm add -D tailwindcss @tailwindcss/postcss autoprefixer
```

## 📦 构建生产版本

```bash
pnpm build
```bash

构建产物将输出到 `dist/` 目录。

### 预览生产版本

```bash
pnpm preview
```

## 🔧 可用的脚本

- `pnpm dev` - 启动开发服务器
- `pnpm build` - 构建生产版本
- `pnpm preview` - 预览生产版本

## 🎨 自定义配置

### 修改主题颜色

编辑 `tailwind.config.js`：

```js
colors: {
  background: '#09090b',
  surface: '#18181b',
  primary: '#06b6d4',
  // ... 更多颜色
}
```json

### 修改端口

编辑 `vite.config.ts`：

```ts
export default defineConfig({
  server: {
    port: 3000, // 修改为你想要的端口
  },
})
```

## 📝 环境变量

如果项目需要 API keys，创建 `.env.local` 文件：

```env
VITE_API_KEY=your_api_key_here
VITE_API_BASE_URL=http://localhost:8000
VITE_BACKEND_URL=http://localhost:8000/api
GEMINI_API_KEY=your_gemini_api_key
```text

---

## 🔌 后端集成指南

### 概述

本项目是纯前端应用，需要配合后端 API 使用。以下是完整的集成指南。

### 1. 环境变量配置

在项目根目录创建 `.env.local` 文件：

```env
# 后端 API 基础 URL
VITE_API_BASE_URL=http://localhost:8000
VITE_BACKEND_URL=http://localhost:8000/api

# AI 服务配置（如果直接调用 AI API）
VITE_GEMINI_API_KEY=your_gemini_api_key_here
VITE_OPENAI_API_KEY=your_openai_api_key_here
```

### 2. 必需的后端 API 接口

#### 2.1 用户设置相关

**保存用户设置**

```json
POST /api/settings
Content-Type: application/json

Request Body:
{
  "profile": {
    "name": "string",
    "role": "string",
    "language": "en" | "zh-TW" | "zh-CN" | "jp",
    "avatarUrl": "string (optional)"
  },
  "ai": {
    "provider": "ollama" | "openai" | "anthropic",
    "apiKey": "string",
    "model": "string"
  },
  "prompts": {
    "global": "string",
    "interviewSuggestions": "string",
    "coachChat": "string"
  }
}

Response:
{
  "success": true,
  "message": "Settings saved successfully"
}
```

**获取用户设置**

```json
GET /api/settings

Response:
{
  "profile": { ... },
  "ai": { ... },
  "prompts": { ... }
}
```

#### 2.2 面试录制相关

**开始面试录制**

```json
POST /api/interview/start
Content-Type: application/json

Request Body:
{
  "scenario": "string",
  "mode": "Single" | "Dual",
  "questionIds": ["string"]
}

Response:
{
  "sessionId": "string",
  "startTime": "ISO 8601 datetime"
}
```

**上传面试录音/视频**

```json
POST /api/interview/upload
Content-Type: multipart/form-data

Form Data:
- sessionId: string
- file: File (audio/video)
- timestamp: number

Response:
{
  "success": true,
  "fileUrl": "string"
}
```

**结束面试并请求分析**

```json
POST /api/interview/complete
Content-Type: application/json

Request Body:
{
  "sessionId": "string",
  "duration": "string",
  "answers": [
    {
      "questionId": "string",
      "transcription": "string",
      "audioUrl": "string"
    }
  ]
}

Response:
{
  "recordId": "string",
  "analysisId": "string"
}
```

#### 2.3 面试分析相关

**获取面试分析结果**

```json
GET /api/analysis/:analysisId

Response:
{
  "overallScore": number (0-100),
  "clarity": number (0-100),
  "confidence": number (0-100),
  "knowledge": number (0-100),
  "structure": number (0-100),
  "empathy": number (0-100),
  "feedback": "string",
  "suggestions": ["string"],
  "transcript": "string"
}
```

#### 2.4 历史记录相关

**获取面试历史列表**

```json
GET /api/history?page=1&limit=10

Response:
{
  "records": [
    {
      "id": "string",
      "date": "ISO 8601 datetime",
      "scenario": "string",
      "mode": "Single" | "Dual",
      "score": number,
      "duration": "string",
      "tags": ["string"]
    }
  ],
  "total": number,
  "page": number,
  "limit": number
}
```

**获取单条历史记录详情**

```json
GET /api/history/:recordId

Response:
{
  "id": "string",
  "date": "string",
  "scenario": "string",
  "mode": "Single" | "Dual",
  "score": number,
  "duration": "string",
  "tags": ["string"],
  "questions": [...],
  "answers": [...],
  "analysis": { ... }
}
```

#### 2.5 题库相关

**获取题目列表**

```json
GET /api/questions?type=Behavioral&difficulty=Mid&limit=20

Response:
{
  "questions": [
    {
      "id": "string",
      "text": "string",
      "type": "Behavioral" | "Technical" | "Situational",
      "difficulty": "Junior" | "Mid" | "Senior",
      "role": "string",
      "tags": ["string"]
    }
  ],
  "total": number
}
```

**AI 生成新题目**

```json
POST /api/questions/generate
Content-Type: application/json

Request Body:
{
  "type": "Behavioral" | "Technical" | "Situational",
  "difficulty": "Junior" | "Mid" | "Senior",
  "role": "string",
  "count": number
}

Response:
{
  "questions": [...]
}
```

#### 2.6 AI 教练相关

**发送教练聊天消息**

```json
POST /api/coach/chat
Content-Type: application/json

Request Body:
{
  "message": "string",
  "context": {
    "sessionId": "string (optional)",
    "questionId": "string (optional)"
  }
}

Response:
{
  "reply": "string",
  "suggestions": ["string"]
}
```

#### 2.7 系统检查相关

**检查后端健康状态**

```json
GET /api/health

Response:
{
  "status": "ok",
  "timestamp": "ISO 8601 datetime",
  "services": {
    "database": "ok",
    "ai": "ok",
    "storage": "ok"
  }
}
```

### 3. 前端集成步骤

#### 步骤 1：创建 API 客户端

创建 `src/services/api.ts`：

```typescript
const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000/api';

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const config: RequestInit = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Settings API
  async saveSettings(settings: AppSettings) {
    return this.request('/settings', {
      method: 'POST',
      body: JSON.stringify(settings),
    });
  }

  async getSettings() {
    return this.request<AppSettings>('/settings');
  }

  // Interview API
  async startInterview(data: { scenario: string; mode: string; questionIds: string[] }) {
    return this.request('/interview/start', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async uploadRecording(sessionId: string, file: File) {
    const formData = new FormData();
    formData.append('sessionId', sessionId);
    formData.append('file', file);
    formData.append('timestamp', Date.now().toString());

    return fetch(`${this.baseUrl}/interview/upload`, {
      method: 'POST',
      body: formData,
    }).then(res => res.json());
  }

  // Analysis API
  async getAnalysis(analysisId: string) {
    return this.request(`/analysis/${analysisId}`);
  }

  // History API
  async getHistory(page: number = 1, limit: number = 10) {
    return this.request(`/history?page=${page}&limit=${limit}`);
  }

  // Questions API
  async getQuestions(filters: { type?: string; difficulty?: string; limit?: number }) {
    const params = new URLSearchParams(filters as any);
    return this.request(`/questions?${params}`);
  }

  // Coach API
  async sendCoachMessage(message: string, context?: any) {
    return this.request('/coach/chat', {
      method: 'POST',
      body: JSON.stringify({ message, context }),
    });
  }

  // Health check
  async healthCheck() {
    return this.request('/health');
  }
}

export const apiClient = new ApiClient();
```python

#### 步骤 2：在组件中使用 API

在 `Settings.tsx` 中保存设置：

```typescript
import { apiClient } from '../services/api';

const handleSave = async () => {
  try {
    await apiClient.saveSettings(settings);
    // 显示成功消息
  } catch (error) {
    console.error('Failed to save settings:', error);
    // 显示错误消息
  }
};
```

在 `History.tsx` 中获取历史记录：

```typescript
import { useState, useEffect } from 'react';
import { apiClient } from '../services/api';

export const History = () => {
  const [records, setRecords] = useState([]);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const data = await apiClient.getHistory(1, 10);
        setRecords(data.records);
      } catch (error) {
        console.error('Failed to fetch history:', error);
      }
    };

    fetchHistory();
  }, []);

  // ... 渲染逻辑
};
```javascript

#### 步骤 3：系统检查集成

更新 `SystemCheckModal.tsx` 中的后端检查：

```typescript
const checkBackend = async () => {
  try {
    const response = await apiClient.healthCheck();
    return response.status === 'ok';
  } catch (error) {
    console.error('Backend health check failed:', error);
    return false;
  }
};
```

### 4. CORS 配置

后端需要配置 CORS 以允许前端访问。

**Express.js 示例：**

```javascript
const cors = require('cors');

app.use(cors({
  origin: 'http://localhost:3000', // 前端地址
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));
```python

**FastAPI 示例：**

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 5. 认证机制（可选）

如果需要用户认证，可以使用 JWT Token：

**前端存储 Token：**

```typescript
// 登录后存储
localStorage.setItem('auth_token', token);

// 在 API 请求中添加 Token
headers: {
  'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
  'Content-Type': 'application/json',
}
```javascript

**后端验证 Token：**

```javascript
// Express middleware 示例
const authenticateToken = (req, res, next) => {
  const token = req.headers['authorization']?.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }

  jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
    if (err) {
      return res.status(403).json({ error: 'Invalid token' });
    }
    req.user = user;
    next();
  });
};
```

### 6. WebSocket 集成（实时功能）

如果需要实时分析或教练对话，可以使用 WebSocket：

**前端 WebSocket 客户端：**

```typescript
// src/services/websocket.ts
export class WebSocketClient {
  private ws: WebSocket | null = null;

  connect(sessionId: string) {
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';
    this.ws = new WebSocket(`${wsUrl}?sessionId=${sessionId}`);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
    };

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      // 处理实时消息
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  send(message: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }

  disconnect() {
    this.ws?.close();
  }
}
```bash

### 7. 测试后端连接

运行以下命令测试后端连接：

```bash
# 测试健康检查
curl http://localhost:8000/api/health

# 测试获取题目
curl http://localhost:8000/api/questions?type=Behavioral&limit=5
```

### 8. 部署注意事项

**前端部署：**

1. 构建生产版本：

```bash
pnpm build
```text

2. 更新 `.env.production` 环境变量：

```env
VITE_BACKEND_URL=https://your-backend-api.com/api
```

3. 部署 `dist/` 目录到静态托管服务（Vercel、Netlify、AWS S3 等）

**后端配置：**

- 确保生产环境的 CORS 配置正确
- 使用 HTTPS 协议
- 配置环境变量和 API keys
- 设置适当的速率限制

### 9. 开发环境代理配置（可选）

如果遇到 CORS 问题，可以在 `vite.config.ts` 中配置代理：

```typescript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
```text

然后使用 `/api` 作为请求前缀，无需配置 `VITE_BACKEND_URL`。

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 License

[MIT License](LICENSE)
