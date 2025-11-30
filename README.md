# AI Interview Pro + 情緒分析系統

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8.18-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)
![React](https://img.shields.io/badge/React-18.2-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5.8-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.13-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-6.2-646CFF?style=for-the-badge&logo=vite&logoColor=white)

![DeepFace](https://img.shields.io/badge/DeepFace-0.0.85-4285F4?style=flat-square)
![OpenCV](https://img.shields.io/badge/OpenCV-4.9-5C3EE8?style=flat-square&logo=opencv&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat-square)
![JWT](https://img.shields.io/badge/JWT-Auth-000000?style=flat-square&logo=jsonwebtokens&logoColor=white)

**一個整合 AI 面試練習與即時情緒分析的智慧平台**

*支援多種 AI 模型（OpenAI GPT、Gemini、Ollama）| 即時雙鏡頭情緒分析 | Producer-Consumer 非同步高效能處理*

[快速開始](#快速開始) | [功能特色](#功能特色) | [系統架構](#系統架構) | [API 文檔](#api-端點) | [常見問題](#常見問題)

</div>

---

## 目錄

- [專案概覽](#專案概覽)
- [功能特色](#功能特色)
- [系統架構](#系統架構)
- [系統需求](#系統需求)
- [安裝指南](#安裝指南)
- [快速開始](#快速開始)
- [專案結構](#專案結構)
- [使用說明](#使用說明)
- [API 端點](#api-端點)
- [資料庫模型](#資料庫模型)
- [AI Provider 整合](#ai-provider-整合)
- [效能優化](#效能優化)
- [開發指南](#開發指南)
- [常見問題](#常見問題)
- [授權資訊](#授權資訊)

---

## 專案概覽

本專案整合兩大核心系統，打造完整的 AI 輔助面試訓練解決方案：

### 1. AI Interview Pro - AI 面試練習平台

一個現代化的 AI 驅動面試練習平台，幫助使用者提升面試技巧：

- **AI 教練**: 整合多種 LLM (OpenAI GPT-4、Claude、Gemini、Ollama) 提供即時回饋與建議
- **題庫管理**: 分類管理面試題目，支援 AI 自動生成與批量匯入/匯出
- **績效追蹤**: 視覺化呈現練習歷程與進步趨勢，提供個人化學習建議
- **影片錄製**: 錄製面試練習並進行回放分析，支援斷點續傳

### 2. 情緒分析系統 - 即時情緒辨識

基於深度學習的即時情緒分析系統，採用 **Producer-Consumer 非同步架構**：

- **即時分析**: 使用 DeepFace + TensorFlow 進行情緒、年齡、性別辨識
- **雙鏡頭模式**: 同時分析顧客與服務員的情緒狀態（適用服務業場景）
- **效能優化**: ThreadedCamera + AsyncDeepFaceAnalyzer 架構，FPS 提升 10-30 倍
- **報表生成**: 自動生成情緒趨勢圖表、滿意度評分與 JSON 結果

---

## 功能特色

### AI Interview Pro

| 功能 | 說明 |
|------|------|
| **使用者認證** | JWT 無狀態認證，支援 Token 刷新機制 |
| **AI 教練** | 支援 OpenAI GPT-4、Anthropic Claude 3、Google Gemini、本地 Ollama |
| **題庫管理** | CRUD 操作、AI 生成題目、JSON 匯入/匯出功能 |
| **績效分析** | Recharts 時間序列趨勢圖、多維度統計摘要 |
| **影片上傳** | 支援進度顯示、分塊上傳、錯誤重試 |
| **安全性** | API Key 加密儲存 (Fernet AES-128-CBC)、bcrypt 密碼雜湊 |

### 情緒分析系統

| 功能 | 說明 |
|------|------|
| **情緒辨識** | 辨識 7 種情緒 (happy, sad, angry, fear, surprise, disgust, neutral) |
| **人口統計** | 自動估算年齡 (±4.65 MAE) 與性別 (97.44% 準確率) |
| **雙鏡頭** | 支援 SINGLE/DUAL 模式，可同時分析多個對象 |
| **非同步處理** | Producer-Consumer 架構，UI 執行緒不阻塞 |
| **圖表生成** | Matplotlib 情緒波形圖、長條圖、合併圖表 |
| **影片錄製** | AVI 錄製 + FFmpeg 自動轉檔 MP4 |

---

## 系統架構

```text
┌─────────────────────────────────────────────────────────────────────┐
│                         Frontend (React + Vite)                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │   Landing   │ │   Coach     │ │   Record    │ │  Settings   │   │
│  │    Page     │ │   Chat      │ │   Page      │ │    Page     │   │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │
│                              │                                       │
│                              ▼                                       │
│                    ┌─────────────────────┐                          │
│                    │   API Service Layer │                          │
│                    └─────────────────────┘                          │
└─────────────────────────────│────────────────────────────────────────┘
                              │ HTTP/REST
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Backend (Flask 3.0)                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │   Auth      │ │   Coach     │ │  Questions  │ │  Analytics  │   │
│  │  Blueprint  │ │  Blueprint  │ │  Blueprint  │ │  Blueprint  │   │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘   │
│         │               │               │               │           │
│         ▼               ▼               ▼               ▼           │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Service Layer                             │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐    │   │
│  │  │   Auth      │ │    AI       │ │     Provider        │    │   │
│  │  │  Service    │ │  Service    │ │     Registry        │    │   │
│  │  └─────────────┘ └──────┬──────┘ └──────────┬──────────┘    │   │
│  └─────────────────────────│───────────────────│────────────────┘   │
│                            │                   │                     │
│                            ▼                   ▼                     │
│                   ┌─────────────────────────────────────┐           │
│                   │        AI Providers                  │           │
│                   │  ┌────────┐ ┌────────┐ ┌────────┐   │           │
│                   │  │ OpenAI │ │ Claude │ │ Gemini │   │           │
│                   │  └────────┘ └────────┘ └────────┘   │           │
│                   │  ┌────────┐                         │           │
│                   │  │ Ollama │ (Local)                 │           │
│                   │  └────────┘                         │           │
│                   └─────────────────────────────────────┘           │
│                            │                                         │
│                            ▼                                         │
│                   ┌─────────────────┐                               │
│                   │  SQLite + ORM   │                               │
│                   │  (SQLAlchemy)   │                               │
│                   └─────────────────┘                               │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                 Emotion Analysis System (Python)                     │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Main Process (UI Thread)                  │   │
│  │  ┌─────────────────┐     ┌─────────────────┐                │   │
│  │  │ ThreadedCamera  │────▶│  Frame Display  │                │   │
│  │  │  (Non-blocking) │     │   (OpenCV)      │                │   │
│  │  └────────┬────────┘     └─────────────────┘                │   │
│  └───────────│──────────────────────────────────────────────────┘   │
│              │                                                       │
│              ▼ Frame Queue (Producer)                                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              AsyncDeepFaceAnalyzer (Consumer)                │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐    │   │
│  │  │   Frame     │ │  DeepFace   │ │   Result Queue      │    │   │
│  │  │   Queue     │─▶│  Analysis   │─▶│   (Non-blocking)    │    │   │
│  │  └─────────────┘ └─────────────┘ └─────────────────────┘    │   │
│  │                                                              │   │
│  │  Features:                                                   │   │
│  │  • Frame skipping (每 5 幀分析一次)                          │   │
│  │  • Image downsampling (320x240)                             │   │
│  │  • Metal/CUDA GPU acceleration                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│              │                                                       │
│              ▼                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Output Generation                         │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐    │   │
│  │  │   Charts    │ │   Video     │ │   JSON Results      │    │   │
│  │  │ (Matplotlib)│ │   (MP4)     │ │   (analysis.json)   │    │   │
│  │  └─────────────┘ └─────────────┘ └─────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 系統需求

### 硬體需求

| 組件 | 最低需求 | 建議配置 |
|------|---------|---------|
| **CPU** | Intel Core i5 / Apple M1 | Intel Core i7 / Apple M2 以上 |
| **RAM** | 8GB | 16GB 以上 |
| **GPU** | 內建顯示 | 支援 Metal (macOS) 或 CUDA (Windows/Linux) |
| **儲存空間** | 10GB | 20GB SSD |
| **攝影機** | 1 個 USB 網路攝影機 | 2 個 USB 網路攝影機 (雙鏡頭模式) |

### 軟體需求

| 軟體 | 版本 | 說明 |
|------|------|------|
| **作業系統** | macOS 12+ / Windows 10+ / Ubuntu 20.04+ | 跨平台支援 |
| **Python** | 3.8.18 | 建議使用 Conda 管理環境 |
| **Node.js** | 18.x+ | 前端開發環境 |
| **pnpm** | 8.x+ | 前端套件管理 (建議) |
| **FFmpeg** | 4.x+ | 影片轉檔 (可選) |

### 瀏覽器支援

| 瀏覽器 | 版本 |
|--------|------|
| Chrome | 90+ |
| Firefox | 88+ |
| Safari | 14+ |
| Edge | 90+ |

---

## 安裝指南

### 步驟 1: 複製專案

```bash
git clone https://github.com/1104030360/AI-Interview-Pro-.git
cd AI-Interview-Pro-
```

### 步驟 2: 設定 Conda 環境

```bash
# 建立 Conda 環境 (建議使用 Miniforge/Miniconda)
conda create -n new_tf_env python=3.8.18
conda activate new_tf_env

# 安裝情緒分析系統依賴 (TensorFlow, DeepFace, OpenCV 等)
pip install -r requirements.txt

# 安裝後端 API 依賴 (Flask, SQLAlchemy, JWT 等)
pip install -r backend/requirements_backend.txt
```

> **提示**: 如果在 macOS M1/M2 上遇到 TensorFlow 問題，可使用：
> ```bash
> conda install -c apple tensorflow-deps
> pip install tensorflow-macos tensorflow-metal
> ```

### 步驟 3: 設定前端環境

```bash
cd "ai-interview-pro (1)"

# 使用 pnpm (建議，更快且節省磁碟空間)
pnpm install

# 或使用 npm (如遇依賴衝突)
npm install --legacy-peer-deps
```

### 步驟 4: 環境變數設定

複製範例檔案並修改：

```bash
cp .env.example .env
```

編輯 `.env` 檔案：

```properties
# === 模型路徑 (情緒分析系統) ===
MODEL_DIR=/path/to/your/converted_keras-2
KERAS_MODEL_PATH=${MODEL_DIR}/keras_model.h5
LABELS_PATH=${MODEL_DIR}/labels.txt

# === 字體路徑 (中文顯示) ===
FONT_PATH=/path/to/NotoSansTC-VariableFont_wght.ttf

# === 攝影機設定 ===
CAMERA_0_ID=0                    # 顧客攝影機 ID
CAMERA_1_ID=1                    # 服務員攝影機 ID
CAMERA_MODE=DUAL                 # SINGLE 或 DUAL

# === DeepFace 設定 ===
DEEPFACE_DETECTOR=opencv         # 偵測器 (opencv/ssd/mtcnn/retinaface)
DEEPFACE_FRAME_SKIP=5            # 每 N 幀分析一次

# === 後端 API 設定 ===
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# === AI 設定加密金鑰 (生產環境必填) ===
# 使用以下命令生成:
# python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
AI_SETTINGS_ENCRYPTION_KEY=
```

### 步驟 5: 初始化資料庫

```bash
cd backend
python -c "from database import db, init_db; from app import create_app; app = create_app(); init_db(app)"
```

---

## 快速開始

### 啟動後端 API (Port 5001)

```bash
conda activate new_tf_env
cd backend
python app.py
```

看到以下訊息表示啟動成功：

```text
============================================================
AI Interview Pro Backend API Server
============================================================
Running on: http://0.0.0.0:5001
Debug mode: True
Database: sqlite:///...interview_pro.db
============================================================
```

### 啟動前端 (Port 3000)

開啟新終端機：

```bash
cd "ai-interview-pro (1)"
pnpm dev
```

前端將在 `http://localhost:3000` 啟動。

### 啟動情緒分析系統

開啟新終端機：

```bash
conda activate new_tf_env
python project_refactored.py
```

操作方式：

- 程式啟動後會開啟攝影機視窗
- 偵測到人臉後 3 秒開始分析
- 按 `Q` 鍵結束分析並生成報表

---

## 專案結構

```text
專題python/
├── backend/                      # Flask 後端 API
│   ├── api/                     # API 端點 (auth, analytics, coach, questions...)
│   ├── models/                  # SQLAlchemy 資料模型
│   ├── services/                # 業務邏輯層
│   │   └── providers/          # AI Provider (OpenAI, Claude, Gemini, Ollama)
│   ├── prompts/                 # Prompt 模板
│   ├── utils/                   # 工具模組 (crypto, llm_parser)
│   └── tests/                   # 測試套件
│
├── ai-interview-pro (1)/         # React 前端
│   ├── src/
│   │   ├── components/         # React 元件
│   │   ├── pages/              # 頁面元件
│   │   ├── services/           # API 服務層
│   │   └── hooks/              # 自訂 Hooks
│   └── package.json
│
├── utils/                        # 情緒分析工具模組
│   ├── analysis.py              # DeepFace 分析邏輯
│   ├── async_analysis.py        # 非同步分析核心
│   ├── camera.py                # 攝影機操作
│   ├── display.py               # 畫面顯示
│   └── visualization.py         # 圖表生成
│
├── models/                       # 資料模型
│   └── camera_state.py          # 攝影機狀態管理
│
├── config.py                     # 設定管理
├── project_refactored.py         # 情緒分析主程式
├── Auto_Switch_refactored.py     # 自動觸發程式
├── requirements.txt              # Python 依賴
└── .env.example                  # 環境變數範例
```

---

## 使用說明

### AI Interview Pro 使用流程

1. **註冊/登入**: 在首頁點擊「開始使用」進行註冊或登入
2. **系統檢查**: 允許攝影機和麥克風權限
3. **概覽頁**: 查看績效趨勢和統計摘要
4. **練習面試**:
   - 進入「錄製」頁面
   - 選擇面試類型
   - 開始錄製練習
5. **AI 教練**: 與 AI 教練對話，獲取個人化建議
6. **題庫**: 瀏覽、新增或 AI 生成面試題目
7. **分析**: 查看歷史記錄和詳細分析報告

### 情緒分析系統使用流程

1. **環境準備**:

   ```bash
   conda activate new_tf_env
   ```

2. **執行分析**:

   ```bash
   python project_refactored.py
   ```

3. **操作說明**:
   - 系統啟動後會開啟攝影機視窗
   - 偵測到 `Class 1` (人物) 後，等待 3 秒開始情緒分析
   - 偵測到 `Class 2` (無人) 超過 3 秒，自動結束
   - 隨時按 `Q` 鍵手動結束

4. **查看結果**:
   - 圖表檔案會存放在專案根目錄
   - JSON 結果存於 `static/data/analysis_result.json`

### 自動觸發模式

```bash
python Auto_Switch_refactored.py
```

此模式會在偵測到人物時自動啟動主分析程式。

### 輸出檔案說明

| 檔案名稱 | 說明 |
|---------|------|
| `Customer_Emotion_Wave.jpg` | 顧客情緒波形圖 |
| `Customer_Emotion_Bar1.jpg` | 顧客情緒分布長條圖 |
| `Server_Emotion_Wave.jpg` | 服務員情緒波形圖 (雙鏡頭) |
| `Customer_Emotion_Wave & Server_Emotion_Wave.jpg` | 合併情緒分析圖 |
| `output_cam0.mp4` | 顧客攝影機錄影 |
| `output_cam1.mp4` | 服務員攝影機錄影 |
| `static/data/analysis_result.json` | JSON 格式分析結果 |

---

## API 端點

### 認證 API (`/api/auth`)

| 方法 | 端點 | 說明 | 認證 |
|------|------|------|------|
| POST | `/register` | 使用者註冊 | 無 |
| POST | `/login` | 使用者登入，回傳 JWT Token | 無 |
| POST | `/refresh` | 刷新 Access Token | Refresh Token |
| GET | `/me` | 取得當前使用者資訊 | Access Token |

### 分析 API (`/api/analytics`)

| 方法 | 端點 | 說明 | 參數 |
|------|------|------|------|
| GET | `/performance-trend` | 績效趨勢 (時間序列) | `timeRange`, `metric` |
| GET | `/summary` | 統計摘要 | - |

### 上傳 API (`/api/uploads`)

| 方法 | 端點 | 說明 |
|------|------|------|
| POST | `/upload` | 上傳檔案 |
| GET | `/list` | 列出檔案 |
| GET | `/download/<id>` | 下載檔案 |
| DELETE | `/<id>` | 刪除檔案 |

### 題庫 API (`/api/questions`)

| 方法 | 端點 | 說明 |
|------|------|------|
| GET | `/` | 取得題目列表 |
| POST | `/` | 新增題目 |
| PUT | `/<id>` | 更新題目 |
| DELETE | `/<id>` | 刪除題目 |
| POST | `/generate` | AI 生成題目 |
| POST | `/import` | 匯入題目 (JSON) |
| GET | `/export` | 匯出題目 (JSON) |

### AI 教練 API (`/api/coach`)

| 方法 | 端點 | 說明 |
|------|------|------|
| POST | `/chat` | 發送訊息，取得 AI 回覆 |
| GET | `/stream` | SSE 串流回應 |
| GET | `/suggestions` | 取得對話建議 |

### 設定 API (`/api/settings`)

| 方法 | 端點 | 說明 |
|------|------|------|
| GET | `/` | 取得使用者設定 |
| PUT | `/` | 更新使用者設定 |
| PUT | `/ai` | 更新 AI Provider 設定 |

### 系統 API

| 方法 | 端點 | 說明 |
|------|------|------|
| GET | `/api/health` | 健康檢查 |

---

## 資料庫模型

### User（使用者）

```sql
users
├── id: UUID (PK)
├── email: VARCHAR(255) UNIQUE
├── password_hash: VARCHAR(255)
├── name: VARCHAR(100)
├── role: VARCHAR(50) [default: 'user']
├── created_at: DATETIME
└── updated_at: DATETIME
```

### UserSettings（使用者設定）

```sql
user_settings
├── id: INTEGER (PK)
├── user_id: UUID (FK → users.id)
├── display_name: VARCHAR(100)
├── job_role: VARCHAR(100)
├── language: VARCHAR(10) [default: 'en']
├── ai_provider: VARCHAR(50) [default: 'ollama']
├── ai_api_key_encrypted: TEXT  -- Fernet 加密
├── ai_model: VARCHAR(100)
├── prompt_global: TEXT
├── prompt_interview: TEXT
└── prompt_coach: TEXT
```

### Interview（面試記錄）

```sql
interviews
├── id: UUID (PK)
├── user_id: UUID (FK → users.id)
├── title: VARCHAR(255)
├── status: VARCHAR(50) [pending/in_progress/completed/failed]
├── created_at: DATETIME
├── completed_at: DATETIME
├── actual_duration: INTEGER (秒)
├── video_url_cam0: VARCHAR(500)
└── video_url_cam1: VARCHAR(500)
```

### AnalysisReport（分析報告）

```sql
analysis_reports
├── id: UUID (PK)
├── interview_id: UUID (FK → interviews.id)
├── status: VARCHAR(50) [pending/processing/completed/failed]
├── overall_score: FLOAT [0-100]
├── empathy_score: FLOAT
├── confidence_score: FLOAT
├── technical_score: FLOAT
├── clarity_score: FLOAT
├── emotion_data: JSON  -- 情緒時間線數據
├── suggestions: JSON   -- AI 建議
└── created_at: DATETIME
```

### Question（題庫）

```sql
questions
├── id: UUID (PK)
├── text: TEXT
├── type: VARCHAR(50) [Behavioral/Technical/System Design]
├── difficulty: VARCHAR(20) [Junior/Mid/Senior]
├── role: VARCHAR(50) [Frontend/Backend/PM/...]
├── tags: JSON
├── example_answer: TEXT
├── created_by: VARCHAR(50) [system/user_id]
└── created_at: DATETIME
```

---

## AI Provider 整合

本專案支援多種 AI Provider，透過統一的抽象介面進行整合：

### 支援的 Provider

| Provider | 模型 | 特色 | 串流支援 |
|----------|------|------|----------|
| **OpenAI** | GPT-4o, GPT-4o-mini | 最強推理能力 | ✅ |
| **Anthropic** | Claude 3 Sonnet/Opus | 長文理解優秀 | ✅ |
| **Google** | Gemini 1.5 Flash/Pro | 多模態支援 | ✅ |
| **Ollama** | Llama 3, Mistral, etc. | **本地運行，免費** | ✅ |

### Provider 架構

```text
backend/services/providers/
├── __init__.py
├── base.py          # AIProviderBase 抽象基類
├── registry.py      # Provider 工廠註冊器
├── openai_provider.py
├── anthropic_provider.py
├── google_provider.py
└── ollama_provider.py
```

### 使用範例

```python
from backend.services.providers import get_provider

# 取得 Provider 實例
provider = get_provider('openai', api_key='sk-xxx')

# 同步對話
response = provider.chat(messages=[{'role': 'user', 'content': 'Hello'}])

# 串流對話
for chunk in provider.stream(messages):
    print(chunk, end='', flush=True)
```

### 新增自訂 Provider

1. 在 `backend/services/providers/` 建立新檔案
2. 繼承 `AIProviderBase` 並實作 `chat()` 和 `stream()` 方法
3. 在 `registry.py` 中註冊

---

## 效能優化

### 情緒分析系統優化

本專案採用 **Producer-Consumer 非同步架構**，大幅提升分析效能：

#### ThreadedCamera（執行緒化攝影機）

```python
# 傳統方式：阻塞式讀取
ret, frame = cap.read()  # 每次 ~33ms 阻塞

# 優化方式：背景執行緒持續讀取
class ThreadedCamera:
    def __init__(self):
        self.thread = threading.Thread(target=self._update)
        self.frame_buffer = deque(maxlen=2)
    
    def read(self):  # 非阻塞，直接從 buffer 讀取
        return self.frame_buffer[-1]
```

**效能提升：2-3x FPS 提升**

#### AsyncDeepFaceAnalyzer（非同步分析器）

```python
class AsyncDeepFaceAnalyzer:
    def __init__(self):
        self.frame_queue = Queue(maxsize=2)
        self.result_queue = Queue(maxsize=10)
        self.worker_thread = threading.Thread(target=self._analyze_worker)
    
    # Producer: 主執行緒放入 frame
    def submit_frame(self, frame):
        if not self.frame_queue.full():
            self.frame_queue.put(frame)
    
    # Consumer: 背景執行緒分析
    def _analyze_worker(self):
        while self.running:
            frame = self.frame_queue.get()
            result = DeepFace.analyze(frame, ...)
            self.result_queue.put(result)
```

**效能提升：10-30x 分析吞吐量**

#### 優化策略

| 策略 | 說明 | 效果 |
|------|------|------|
| **Frame Skipping** | 每 5 幀分析一次 | 減少 80% 運算量 |
| **Image Downsampling** | 縮放至 320x240 分析 | 減少 75% 運算量 |
| **Result Caching** | 人口統計資料快取 | 8 秒後停止重複分析 |
| **Metal/CUDA GPU** | 自動偵測並使用 GPU | 2-5x 加速 |

### 前端效能優化

- **React.memo**: 避免不必要的重新渲染
- **useMemo/useCallback**: 快取計算結果和函數
- **Vite 代碼分割**: 按需載入頁面元件
- **Tailwind CSS JIT**: 只產生使用到的樣式

---

## 開發指南

### 執行測試

```bash
# 執行所有後端測試
cd backend
pytest tests/ -v

# 執行特定測試
pytest tests/test_auth_service.py -v

# 產生覆蓋率報告
pytest --cov=. --cov-report=html

# 執行前端/核心測試
cd ..
pytest tests/ -v
```

### 程式碼風格

- **Python**: 遵循 PEP 8，4 空格縮排，snake_case 命名
- **TypeScript**: 使用 ESLint + Prettier
- **提交訊息**: 使用 Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`)

### 資料庫遷移

```bash
cd backend
flask db migrate -m "描述變更"
flask db upgrade
```

### 新增 AI Provider

1. 在 `backend/services/providers/` 建立新的 provider 類別
2. 繼承 `AIProviderBase` 抽象基類
3. 在 `registry.py` 中註冊新的 provider

```python
# backend/services/providers/my_provider.py
from .base import AIProviderBase

class MyProvider(AIProviderBase):
    def __init__(self, api_key: str, model: str = None):
        super().__init__(api_key, model or "default-model")

    def chat(self, messages: list, **kwargs) -> str:
        # 實作聊天邏輯
        pass

    def stream(self, messages: list, **kwargs):
        # 實作串流邏輯
        yield from ...
```

---

## 常見問題

### Q: 環境未啟用？

```bash
# 確認當前環境
echo $CONDA_DEFAULT_ENV

# 啟用環境
conda activate new_tf_env
```

### Q: 找不到模組？

```bash
# 確認使用正確的 Python
which python
# 應顯示: /path/to/miniforge3/envs/new_tf_env/bin/python

# 重新啟用環境
conda deactivate && conda activate new_tf_env
```

### Q: 攝影機無法開啟？

**macOS:**

1. 開啟「系統設定」→「隱私權與安全性」→「攝影機」
2. 允許終端機或 IDE 存取攝影機

**測試攝影機:**

```bash
python -c "
import cv2
cap0 = cv2.VideoCapture(0)
cap1 = cv2.VideoCapture(1)
print('攝影機 0:', '可用' if cap0.isOpened() else '無法開啟')
print('攝影機 1:', '可用' if cap1.isOpened() else '無法開啟')
cap0.release(); cap1.release()
"
```

### Q: 前端依賴安裝失敗？

```bash
# 清除快取並重新安裝
rm -rf node_modules pnpm-lock.yaml
pnpm install

# 或使用 npm with legacy peer deps
npm install --legacy-peer-deps
```

### Q: 後端啟動時出現 JWT 錯誤？

確保 `.env` 檔案中設定了 `SECRET_KEY` 和 `JWT_SECRET_KEY`。

### Q: AI 功能無法使用？

1. 確認 AI Provider 設定正確 (Settings 頁面)
2. 確認 API Key 已正確輸入
3. 檢查網路連線

### Q: DeepFace 分析速度很慢？

1. 確認使用 `opencv` 作為 detector_backend (最快)
2. 檢查 `.env` 中的 `DEEPFACE_FRAME_SKIP` 設定
3. 降低攝影機解析度 (`CAMERA_WIDTH`, `CAMERA_HEIGHT`)

---

## 技術棧

### 後端

- **框架**: Flask 3.0 + Flask-CORS + Flask-JWT-Extended
- **資料庫**: SQLAlchemy 2.0 + Flask-Migrate + SQLite
- **認證**: JWT (Access + Refresh Token) + bcrypt 密碼雜湊
- **加密**: Cryptography (Fernet AES-128-CBC)
- **AI 整合**: OpenAI SDK, Anthropic SDK, Google GenerativeAI, Ollama

### 前端

- **框架**: React 18.2 + TypeScript 5.8
- **打包工具**: Vite 6.2
- **樣式**: Tailwind CSS 4.1 + PostCSS
- **圖表**: Recharts 2.12
- **圖示**: Lucide React 0.358

### 情緒分析

- **深度學習**: TensorFlow 2.13 + Keras 2.13
- **臉部分析**: DeepFace 0.0.85 (支援 VGG-Face, FaceNet, ArcFace 等 11+ 模型)
- **影像處理**: OpenCV 4.9 + NumPy 1.24 + Pillow 10.2
- **圖表**: Matplotlib + Pandas 2.0

### DeepFace 支援的功能

| 功能 | 說明 |
|------|------|
| **情緒辨識** | angry, disgust, fear, happy, sad, surprise, neutral |
| **年齡估算** | ± 4.65 MAE (Mean Absolute Error) |
| **性別辨識** | 97.44% 準確率 |
| **人臉偵測** | OpenCV, SSD, MTCNN, RetinaFace, MediaPipe, YOLOv8 等 |

---

## 授權資訊

本專案採用 MIT 授權條款。詳見 [LICENSE](LICENSE) 檔案。

### 第三方授權

- **DeepFace**: MIT License - [serengil/deepface](https://github.com/serengil/deepface)
- **TensorFlow**: Apache 2.0 License
- **Flask**: BSD-3-Clause License
- **React**: MIT License

---

## 聯絡與貢獻

如有問題或建議，歡迎透過以下方式聯繫：

- **Issue**: [GitHub Issues](https://github.com/1104030360/AI-Interview-Pro-/issues)
- **Pull Request**: 歡迎提交 PR，請遵循 [Conventional Commits](https://www.conventionalcommits.org/) 規範

### 貢獻指南

1. Fork 本專案
2. 建立功能分支 (`git checkout -b feat/amazing-feature`)
3. 提交變更 (`git commit -m 'feat: add amazing feature'`)
4. 推送分支 (`git push origin feat/amazing-feature`)
5. 開啟 Pull Request

---

<div align="center">

**Made for better interview preparation**

*如果這個專案對你有幫助，歡迎給個 Star！*

</div>
