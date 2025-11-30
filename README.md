# AI Interview Pro + 情緒分析系統

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8.18-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask&logoColor=white)
![React](https://img.shields.io/badge/React-18.2-61DAFB?logo=react&logoColor=black)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.13-FF6F00?logo=tensorflow&logoColor=white)


**一個整合 AI 面試練習與即時情緒分析的智慧平台**

[快速開始](#-快速開始) | [功能特色](#-功能特色) | [安裝指南](#-安裝指南) | [API 文檔](#-api-端點) | [常見問題](#-常見問題)

</div>

---

## 目錄

- [專案概覽](#-專案概覽)
- [功能特色](#-功能特色)
- [系統需求](#-系統需求)
- [安裝指南](#-安裝指南)
- [快速開始](#-快速開始)
- [專案結構](#-專案結構)
- [使用說明](#-使用說明)
- [API 端點](#-api-端點)
- [開發指南](#-開發指南)
- [常見問題](#-常見問題)
- [授權資訊](#-授權資訊)

---

## 專案概覽

本專案整合兩大核心系統：

### 1. AI Interview Pro - AI 面試練習平台

一個現代化的 AI 驅動面試練習平台，幫助使用者提升面試技巧：

- **AI 教練**: 透過多種 LLM 提供即時回饋與建議
- **題庫管理**: 分類管理面試題目，支援 AI 自動生成
- **績效追蹤**: 視覺化呈現練習歷程與進步趨勢
- **影片錄製**: 錄製面試練習並進行回放分析

### 2. 情緒分析系統 - 即時情緒辨識

基於深度學習的即時情緒分析系統：

- **即時分析**: 使用 DeepFace 進行情緒、年齡、性別辨識
- **雙鏡頭模式**: 同時分析顧客與服務員的情緒狀態
- **效能優化**: 非同步分析架構，確保流暢的即時處理
- **報表生成**: 自動生成情緒趨勢圖表與滿意度評分

---

## 功能特色

### AI Interview Pro

| 功能 | 說明 |
|------|------|
| **使用者認證** | JWT 無狀態認證，安全的登入/註冊機制 |
| **AI 教練** | 支援 OpenAI GPT、Anthropic Claude、Google Gemini、Ollama |
| **題庫管理** | CRUD 操作、AI 生成題目、匯入/匯出功能 |
| **績效分析** | 時間序列趨勢圖、統計摘要、等級評估 |
| **影片上傳** | 支援進度顯示、斷點續傳、錯誤重試 |
| **安全性** | API Key 加密儲存 (Fernet AES-128-CBC) |

### 情緒分析系統

| 功能 | 說明 |
|------|------|
| **情緒辨識** | 辨識 7 種情緒 (happy, sad, angry, fear, surprise, disgust, neutral) |
| **人口統計** | 自動估算年齡與性別 |
| **雙鏡頭** | 支援單鏡頭 (顧客) 或雙鏡頭 (顧客 + 服務員) 模式 |
| **非同步處理** | Producer-Consumer 架構，FPS 提升 10-30 倍 |
| **圖表生成** | 自動生成情緒波形圖、長條圖、合併圖表 |
| **影片錄製** | 自動錄製分析過程並轉檔為 MP4 |

---

## 系統需求

### 硬體需求

- **CPU**: Intel Core i5 / Apple M1 或以上
- **RAM**: 8GB 以上 (建議 16GB)
- **GPU**: 支援 Metal (macOS) 或 CUDA (Windows/Linux)
- **攝影機**: 1-2 個 USB 網路攝影機

### 軟體需求

- **作業系統**: macOS 12+、Windows 10+、Ubuntu 20.04+
- **Python**: 3.8.18 (建議使用 Conda 環境)
- **Node.js**: 18.x 或以上
- **瀏覽器**: Chrome、Firefox、Safari (最新版本)

---

## 安裝指南

### 步驟 1: 複製專案

```bash
git clone https://github.com/1104030360/AI-Interview-Pro-.git
cd AI-Interview-Pro-
```

### 步驟 2: 設定 Conda 環境

```bash
# 建立 Conda 環境 (建議)
conda create -n new_tf_env python=3.8.18
conda activate new_tf_env

# 安裝情緒分析系統依賴
pip install -r requirements.txt

# 安裝後端 API 依賴
pip install -r backend/requirements_backend.txt

# (可選) 如需使用 OpenCV 原始碼功能
# OpenCV 已透過 pip 安裝，若需原始碼可自行下載：
# git clone https://github.com/opencv/opencv.git opencv-4.x
```

### 步驟 3: 設定前端環境

```bash
cd "ai-interview-pro (1)"

# 使用 pnpm (建議)
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

# === 字體路徑 ===
FONT_PATH=/path/to/NotoSansTC-VariableFont_wght.ttf

# === 攝影機設定 ===
CAMERA_0_ID=0
CAMERA_1_ID=1
CAMERA_MODE=DUAL  # 或 SINGLE

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

```
============================================================
🚀 AI Interview Pro Backend API Server
============================================================
📍 Running on: http://0.0.0.0:5001
🔧 Debug mode: True
💾 Database: sqlite:///...interview_pro.db
============================================================
```

### 啟動前端 (Port 3000)

開啟新終端機：

```bash
cd "ai-interview-pro (1)"
pnpm dev
```

前端將在 http://localhost:3000 啟動。

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

```
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

---

## API 端點

### 認證 API

| 方法 | 端點 | 說明 |
|------|------|------|
| POST | `/api/auth/register` | 使用者註冊 |
| POST | `/api/auth/login` | 使用者登入 |
| POST | `/api/auth/refresh` | 刷新 Access Token |
| GET | `/api/auth/me` | 取得當前使用者資訊 |

### 分析 API

| 方法 | 端點 | 說明 |
|------|------|------|
| GET | `/api/analytics/performance-trend` | 績效趨勢 (時間序列) |
| GET | `/api/analytics/summary` | 統計摘要 |

### 上傳 API

| 方法 | 端點 | 說明 |
|------|------|------|
| POST | `/api/uploads/upload` | 上傳檔案 |
| GET | `/api/uploads/list` | 列出檔案 |
| GET | `/api/uploads/download/<id>` | 下載檔案 |
| DELETE | `/api/uploads/<id>` | 刪除檔案 |

### 題庫 API

| 方法 | 端點 | 說明 |
|------|------|------|
| GET | `/api/questions` | 取得題目列表 |
| POST | `/api/questions` | 新增題目 |
| PUT | `/api/questions/<id>` | 更新題目 |
| DELETE | `/api/questions/<id>` | 刪除題目 |
| POST | `/api/questions/generate` | AI 生成題目 |
| POST | `/api/questions/import` | 匯入題目 |
| GET | `/api/questions/export` | 匯出題目 |

### AI 教練 API

| 方法 | 端點 | 說明 |
|------|------|------|
| POST | `/api/coach/chat` | 發送訊息 |
| GET | `/api/coach/stream` | SSE 串流回應 |
| POST | `/api/coach/suggestions` | 取得建議 |

### 系統 API

| 方法 | 端點 | 說明 |
|------|------|------|
| GET | `/api/health` | 健康檢查 |

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
```

### 程式碼風格

- Python: 遵循 PEP 8
- TypeScript: 使用 ESLint + Prettier
- 提交訊息: 使用 Conventional Commits

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

---

## 技術棧

### 後端
- **框架**: Flask 3.0
- **資料庫**: SQLAlchemy 2.0 + SQLite
- **認證**: Flask-JWT-Extended + bcrypt
- **AI 整合**: OpenAI, Anthropic, Google AI, Ollama

### 前端
- **框架**: React 18 + TypeScript
- **打包工具**: Vite 6
- **樣式**: Tailwind CSS 4
- **圖表**: Recharts

### 情緒分析
- **深度學習**: TensorFlow 2.13 + Keras
- **臉部分析**: DeepFace 0.0.85
- **影像處理**: OpenCV 4.9

---

## 授權資訊

本專案採用 MIT 授權條款。詳見 [LICENSE](LICENSE) 檔案。

---

## 聯絡與貢獻

如有問題或建議，歡迎透過以下方式聯繫：

- **Issue**: [GitHub Issues](https://github.com/1104030360/AI-Interview-Pro-/issues)
- **Pull Request**: 歡迎提交 PR

---

<div align="center">

**Made with ❤️ for better interview preparation**

</div>
