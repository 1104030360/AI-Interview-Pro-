# 專題Python - 專案結構文件

**更新日期：** 2025年11月30日 **專案名稱：** AI Interview Pro - 面試練習平台 + 情緒分析系統 **狀態：** Phase 10 完成 (功能完善與 UX 優化)

______________________________________________________________________

## 📁 專案結構

```python
專題python/
├── .env                          # 環境變數設定檔（gitignore）
├── .env.example                  # 環境變數範例檔
├── .gitignore                    # Git 忽略檔案設定
├── README.md                     # 專案說明文件
├── requirements.txt              # Python 套件依賴清單
├── CLAUDE.md                     # 本文件
│
├── config.py                     # 設定管理模組 (情緒分析系統)
├── exceptions.py                 # 自訂例外類別
│
├── models/                       # 資料模型與狀態 (情緒分析系統)
│   ├── __init__.py
│   ├── camera_state.py          # 攝影機狀態管理
│   └── cascade/                 # OpenCV Haar Cascades
│
├── utils/                        # 工具函式庫 (情緒分析系統)
│   ├── __init__.py
│   ├── analysis.py              # DeepFace 分析邏輯
│   ├── async_analysis.py        # [Phase 5] 非同步分析核心
│   ├── camera.py                # 攝影機操作
│   ├── camera_processing.py     # 畫面處理
│   ├── classification.py        # 場景分類
│   ├── display.py               # 畫面顯示與繪圖
│   ├── logging_config.py        # 日誌設定
│   ├── model.py                 # 模型載入
│   ├── video.py                 # 影片錄製
│   └── visualization.py         # 圖表繪製
│
├── logs/                         # 系統日誌 (gitignore)
│
├── project_refactored.py         # 核心分析程式 (Entry Point)
├── Auto_Switch_refactored.py     # 自動觸發程式 (Entry Point)
├── report_main.py                # Flask Web Server (舊報表系統)
│
├── templates/                    # Flask Templates (舊報表系統)
│   └── index.html               # 報表頁面
│
├── static/                       # Static Assets (舊報表系統)
│   ├── css/                     # Styles
│   ├── js/                      # Scripts
│   ├── data/                    # JSON data exchange
│   └── *.jpg                    # Generated charts
│
├── backend/                      # 🆕 [Phase 6-9] RESTful API 後端
│   ├── __init__.py
│   ├── app.py                   # Flask App Factory (Port 5001)
│   ├── config_backend.py        # 後端配置 (JWT, CORS, Database)
│   ├── database.py              # SQLAlchemy 初始化
│   ├── requirements_backend.txt # 後端依賴清單
│   │
│   ├── api/                     # API Blueprint 模組
│   │   ├── __init__.py
│   │   ├── auth.py              # 認證 API (register, login, refresh, me)
│   │   ├── analytics.py         # [Phase 7] 分析 API (performance-trend, summary)
│   │   ├── uploads.py           # [Phase 8] 上傳 API (upload, download, list, delete)
│   │   ├── analysis.py          # [Phase 8] 分析報告 API (get, export)
│   │   ├── questions.py         # 🆕 [Phase 9] 題庫 API (CRUD, AI生成, 匯入匯出)
│   │   ├── coach.py             # 🆕 [Phase 9] AI教練 API (chat, SSE串流)
│   │   └── dev.py               # 🆕 [Phase 10] 開發工具 API (seed data)
│   │
│   ├── models/                  # 資料庫模型
│   │   ├── __init__.py
│   │   ├── user.py              # User 模型 (UUID, email, password_hash)
│   │   ├── user_settings.py     # UserSettings 模型 (profile, AI config, prompts)
│   │   ├── interview.py         # [Phase 7] Interview 模型 (面試記錄)
│   │   ├── analysis_report.py   # [Phase 7] AnalysisReport 模型 (分析報告)
│   │   └── question.py          # 🆕 [Phase 9] Question 模型 (題庫)
│   │
│   ├── services/                # 業務邏輯層
│   │   ├── __init__.py
│   │   ├── auth_service.py      # 認證服務 (bcrypt, user CRUD)
│   │   ├── analytics_service.py # [Phase 7] 分析服務 (trend, summary, level)
│   │   ├── storage_service.py   # [Phase 8] 儲存服務 (local file system)
│   │   ├── settings_service.py  # [Phase 9] 設定服務 (user settings CRUD)
│   │   ├── ai_service.py        # [Phase 9] AI服務 (Provider Registry 整合)
│   │   └── providers/           # 🆕 [Phase 10] AI Provider 模組
│   │       ├── __init__.py
│   │       ├── base.py          # AIProviderBase 抽象基類
│   │       ├── registry.py      # Provider 註冊表
│   │       ├── openai_provider.py  # OpenAI GPT
│   │       ├── ollama_provider.py  # Ollama 本地模型
│   │       ├── claude_provider.py  # Anthropic Claude
│   │       └── gemini_provider.py  # Google Gemini
│   │
│   ├── prompts/                 # 🆕 [Phase 10] Prompt 模板模組
│   │   ├── __init__.py
│   │   ├── base.py              # PromptTemplate 基類
│   │   ├── question.py          # 題目生成 Prompt
│   │   └── coach.py             # AI 教練 Prompt
│   │
│   ├── utils/                   # 🆕 [Phase 10] 後端工具模組
│   │   ├── __init__.py
│   │   ├── crypto.py            # Fernet 加密 (API Key)
│   │   ├── llm_parser.py        # 多層 LLM JSON 解析
│   │   └── ai_exceptions.py     # AI 自訂例外
│   │
│   └── tests/                   # 後端測試
│       ├── __init__.py
│       ├── test_auth_service.py       # 單元測試 (AuthService)
│       ├── test_auth_api.py           # 整合測試 (Auth API)
│       ├── test_analytics_service.py  # [Phase 7] 單元測試 (AnalyticsService)
│       ├── test_analytics_api.py      # [Phase 7] 整合測試 (Analytics API)
│       ├── test_storage_service.py    # [Phase 8] 單元測試 (StorageService)
│       ├── test_settings_service.py   # 🆕 [Phase 9] 單元測試 (SettingsService)
│       ├── test_questions_api.py      # 🆕 [Phase 9] 整合測試 (Questions API)
│       ├── test_coach_api.py          # 🆕 [Phase 9] 整合測試 (Coach API)
│       ├── test_crypto.py             # 🆕 [Phase 10] 單元測試 (Crypto - 13 tests)
│       ├── test_llm_parser.py         # 🆕 [Phase 10] 單元測試 (LLM Parser - 32 tests)
│       ├── test_api_manual.py         # 手動測試腳本 (需運行伺服器)
│       └── seed_analytics_data.py     # [Phase 7] 測試資料產生器
│
├── ai-interview-pro (1)/         # [Phase 6-10] React 前端應用
│   ├── components/              # React 元件
│   │   ├── ui/                 # 基礎 UI 元件
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Spinner.tsx      # 🆕 [Phase 10] 載入動畫
│   │   │   ├── Toast.tsx        # 🆕 [Phase 10] Toast 通知
│   │   │   └── UploadProgress.tsx # 🆕 [Phase 10] 上傳進度
│   │   ├── feedback/           # 🆕 [Phase 10] 回饋元件
│   │   │   ├── LoadingState.tsx
│   │   │   ├── ErrorState.tsx
│   │   │   └── EmptyState.tsx
│   │   ├── VideoPlayer.tsx      # 🆕 [Phase 10] 影片播放器
│   │   ├── Sidebar.tsx          # 側邊欄導航
│   │   ├── SystemCheckModal.tsx # 系統檢查
│   │   └── ThreeBackground.tsx  # 3D 背景動畫
│   │
│   ├── hooks/                   # 🆕 [Phase 10] 自訂 Hooks
│   │   └── useUploadTask.ts     # 上傳任務狀態管理
│   │
│   ├── pages/                   # 頁面元件
│   │   ├── Landing.tsx          # 歡迎頁
│   │   ├── Overview.tsx         # [Phase 7] 概覽頁 (整合 Analytics API)
│   │   ├── Record.tsx           # 🔄 [Phase 10] 錄製面試 (上傳進度)
│   │   ├── Analysis.tsx         # 🔄 [Phase 10] 分析結果 (影片回放)
│   │   ├── History.tsx          # 歷史記錄
│   │   ├── QuestionBank.tsx     # 🔄 [Phase 10] 題庫 (回饋元件)
│   │   ├── Coach.tsx            # 🔄 [Phase 10] AI 教練 (錯誤處理)
│   │   └── Settings.tsx         # 設定頁面
│   │
│   ├── services/                # API 服務層
│   │   └── api.ts               # API Client (auth, analytics, coach, questions, SSE)
│   │
│   ├── App.tsx                  # 主應用元件
│   ├── index.tsx                # 應用入口
│   ├── types.ts                 # TypeScript 類型
│   ├── package.json             # Node.js 依賴
│   ├── vite.config.ts           # Vite 配置 (Port 3000)
│   └── tailwind.config.js       # Tailwind CSS 配置
│
├── interview_pro.db              # 🆕 SQLite 資料庫 (gitignore)
│
├── docs/                         # 專案文件
│   ├── architecture/            # 架構文件
│   │   ├── backend-arch.md
│   │   └── frontend-arch.md
│   ├── dev-prompt/              # 開發提示
│   │   ├── phase1.md ... phase6.md
│   ├── newUI/                   # 新介面規劃
│   │   └── plan/
│   │       └── phase1-infrastructure.md
│   └── schedule/                # 進度追蹤
│       ├── plans/              # 詳細計畫
│       ├── todo/               # 每日待辦
│       └── reports/            # 階段報告
│
├── archive/                      # 歸檔區
│   └── legacy_v1/               # 舊版程式碼
│
└── tests/                        # 情緒分析系統測試
    ├── verify_phase4.py
    ├── test_camera_config.py
    └── benchmark_performance.py # [Phase 5] 效能測試
```

______________________________________________________________________

## 🎯 核心功能模組

### 1. 情緒辨識系統 (`project_refactored.py`)

- **職責**：雙鏡頭影像擷取、情緒/年齡/性別分析、圖表生成。
- **Phase 5 改進**：
  - 導入 `AsyncDeepFaceAnalyzer` 實現非同步分析。
  - 採用 Producer-Consumer 架構，解決 UI 卡頓問題。
  - 預期效能提升 10-30 倍 (FPS)。

### 2. 自動觸發系統 (`Auto_Switch_refactored.py`)

- **職責**：待機偵測人臉，自動喚醒主分析程式。

### 3. 舊報表展示系統 (`report_main.py`)

- **職責**：提供 Web 介面顯示分析結果。
- **資料來源**：讀取 `static/data/analysis_result.json`。
- **狀態**：保留作為情緒分析獨立報表。

### 4. 🆕 RESTful API 後端 (`backend/app.py`) - Phase 6-7

- **職責**：提供 AI Interview Pro 前端所需的 RESTful API 服務。
- **技術棧**：Flask 3.0 + SQLAlchemy 2.0 + JWT + bcrypt
- **Port**：5001
- **主要功能**：
  - **使用者認證** \[Phase 6\]：JWT-based 無狀態認證 (access token + refresh token)
  - **使用者註冊/登入** \[Phase 6\]：bcrypt 密碼雜湊、email 唯一性驗證
  - **使用者設定管理** \[Phase 6\]：Profile、AI 配置、Prompt 客製化
  - **績效分析** \[Phase 7\]：時間序列趨勢、統計摘要、等級評估
  - **CORS 支援**：允許前端 (localhost:3000) 跨域請求
- **API 端點**：
  - **Auth API** \[Phase 6\]:
    - `POST /api/auth/register` - 使用者註冊
    - `POST /api/auth/login` - 使用者登入
    - `POST /api/auth/refresh` - 刷新 access token
    - `GET /api/auth/me` - 取得當前使用者資訊
  - **Analytics API** \[Phase 7\]:
    - `GET /api/analytics/performance-trend` - 績效趨勢 (時間序列)
    - `GET /api/analytics/summary` - 統計摘要 (sessions, score, hours, level)
  - `GET /api/health` - 健康檢查
- **測試覆蓋率**：40 個測試用例 (19 Phase 6 + 21 Phase 7)

### 5. 🆕 React 前端應用 (`ai-interview-pro (1)/`) - Phase 6-7

- **職責**：AI 面試練習平台的使用者介面。
- **技術棧**：React 19 + TypeScript + Vite + Tailwind CSS + Recharts
- **Port**：3000
- **主要功能**：
  - **Landing 頁面** \[Phase 6\]：3D CSS 動畫歡迎頁
  - **Overview 概覽** \[Phase 7\]：即時績效趨勢圖表、統計儀表板 (連接 Analytics API)
  - **Record 錄製**：進行模擬面試並錄製
  - **Analysis 分析**：查看面試表現分析
  - **History 歷史**：瀏覽歷史面試記錄
  - **Settings 設定**：個人資料、AI 配置、Prompt 客製化
- **API 整合** \[Phase 7\]：
  - API Client (`services/api.ts`) 處理認證與資料請求
  - 自動 token 刷新機制
  - Fallback to mock data when unauthenticated

______________________________________________________________________

## 🔧 設定管理

所有設定透過 `.env` 檔案與 `config.py` 管理：

```env
MODEL_DIR=./models
KERAS_MODEL_PATH=${MODEL_DIR}/keras_model.h5
LABELS_PATH=${MODEL_DIR}/labels.txt
FONT_PATH=./fonts/NotoSansTC-VariableFont_wght.ttf
OUTPUT_DIR=./output
LOG_DIR=./logs
WEB_STATIC_DIR=./static
CAMERA_MODE=DUAL  # SINGLE or DUAL
DEEPFACE_DETECTOR=opencv # [Phase 5] Detector backend
DEEPFACE_FRAME_SKIP=5    # [Phase 5] Analysis interval
```text

______________________________________________________________________

## 📊 開發狀態

### 情緒分析系統

- **Phase 1 (Refactoring)**: ✅ 完成 (核心邏輯模組化)
- **Phase 2 (Frontend)**: ✅ 完成 (新介面整合)
- **Phase 3 (Integration)**: ✅ 完成 (系統穩定化)
- **Phase 4 (Flexibility)**: ✅ 完成 (鏡頭彈性化)
- **Phase 5 (Performance)**: ✅ 完成 (非同步分析、效能優化)

### AI Interview Pro 平台

- **Phase 6 (Backend Infrastructure)**: ✅ 完成 (使用者認證 API)

  - User/UserSettings 資料模型
  - Auth API (register, login, refresh, me)
  - JWT + bcrypt 安全機制

- **Phase 7 (Analytics & Aggregation)**: ✅ 完成 (資料聚合與分析)

  - Interview/AnalysisReport 資料模型
  - AnalyticsService (trend, summary, level)
  - Analytics API (performance-trend, summary)
  - 前端 Overview 頁面整合

- **Phase 8 (Storage & Integration)**: ✅ 完成 (檔案儲存與整合)

  - StorageService (本地檔案系統)
  - Uploads API (上傳、下載、列表、刪除)
  - Analysis API (報告取得、匯出)

- **Phase 9 (Advanced Features)**: ✅ 完成 (AI Coach & 題庫)

  - Question 資料模型與 CRUD API
  - AI Coach API (chat, suggestions)
  - AIService 與 LLM 整合

- **Phase 10 (功能完善與 UX 優化)**: ✅ 完成

  - **Plan 01**: API Key 加密儲存 (Fernet AES-128-CBC)
  - **Plan 02**: AI 建議產出與錯誤處理 (LLM Parser, 自訂例外)
  - **Plan 03**: 錄影上傳回饋與重試 (useUploadTask hook, UploadProgress)
  - **Plan 04**: Analysis 頁影片回放 (VideoPlayer 元件)
  - **Plan 05**: Analytics 測試資料 (seed_analytics_data.py 重構)
  - **Plan 06**: Prompt 標準化 (prompts 模組) + QuestionBank UX
  - **Plan 07**: 功能擴展 (AI Provider Registry, SSE 串流, 題目匯入匯出)
  - **Plan 08**: 前端 UI 元件庫 (Spinner, Toast, LoadingState, ErrorState, EmptyState)
  - 測試覆蓋率: 126 tests passed

______________________________________________________________________

**維護者**：AI Assistant (Agentic Mode)
