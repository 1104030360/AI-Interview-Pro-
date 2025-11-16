# 專題Python - 專案結構文件

**更新日期：** 2025年11月15日  
**專案名稱：** 服務業滿意度分析系統 - 多模態情緒辨識  
**狀態：** Phase 1 重構進行中

---

## 📁 專案結構

```
專題python/
├── .env                          # 環境變數設定檔（gitignore）
├── .env.example                  # 環境變數範例檔
├── .gitignore                    # Git 忽略檔案設定
├── README.md                     # 專案說明文件
├── requirements.txt              # Python 套件依賴清單
│
├── config.py                     # 設定管理模組（NEW）
├── exceptions.py                 # 自訂例外類別（NEW）
│
├── models/                       # 資料模型目錄（NEW）
│   ├── __init__.py
│   └── camera_state.py          # 攝影機狀態資料類別
│
├── utils/                        # 工具函式目錄（NEW）
│   ├── __init__.py
│   ├── logging_config.py        # 日誌設定
│   ├── camera_processing.py     # 攝影機處理邏輯
│   ├── classification.py        # 影像分類邏輯
│   ├── frame_capture.py         # 畫面擷取邏輯
│   ├── display.py               # 顯示處理邏輯
│   ├── recording.py             # 錄影處理邏輯
│   └── exit_conditions.py       # 退出條件判斷
│
├── tests/                        # 測試目錄（NEW）
│   ├── __init__.py
│   ├── conftest.py              # pytest 設定
│   ├── test_camera_state.py     # 狀態管理測試
│   ├── test_config.py           # 設定載入測試
│   ├── test_camera_processing.py# 處理邏輯測試
│   ├── test_classification.py   # 分類功能測試
│   └── test_emotion_scoring.py  # 評分計算測試
│
├── logs/                         # 日誌檔案目錄（NEW, gitignore）
│   └── emotion_analysis.log
│
├── project.py                    # 主程式（重構中）
├── Auto_Switch.py                # 自動切換程式（重構中）
├── report_main.py                # 報告生成主程式
│
├── docs/                         # 文件目錄
│   ├── SETUP.md                 # 詳細設定指南（NEW）
│   ├── ARCHITECTURE.md          # 架構說明（NEW）
│   ├── API.md                   # API 文件（NEW）
│   ├── CONTRIBUTING.md          # 貢獻指南（NEW）
│   ├── NAMING_CONVENTIONS.md    # 命名規範（NEW）
│   │
│   ├── architecture/            # 架構文件
│   │   ├── backend-arch.md     # 後端架構說明
│   │   └── frontend-arch.md    # 前端架構說明
│   │
│   ├── dev-prompt/              # 開發提示文件
│   │   └── phase1.md           # Phase 1 開發指示
│   │
│   ├── schedule/                # 進度管理
│   │   ├── plans/              # 計畫文件
│   │   │   └── phase1.md       # Phase 1 詳細計畫
│   │   ├── todo/               # 待辦事項
│   │   └── reports/            # 完成報告
│   │
│   └── specs/                   # 規格文件
│       ├── drafts/
│       ├── features/
│       └── prompts/
│
├── haarcascade_*.xml            # OpenCV 人臉辨識模型檔案
│
├── report.HTML/CSS/JS           # 報告前端檔案
├── report2.HTML/CSS/JS          # 報告前端檔案（版本2）
│
├── output_cam0.avi/mp4         # 攝影機0輸出影片
├── output_cam1.avi/mp4         # 攝影機1輸出影片
│
├── .venv/                       # Python 虛擬環境（Python 3.8.8）
└── opencv-4.x/                  # OpenCV 原始碼（開發用）
```

---

## 🎯 核心功能模組

### 1. 情緒辨識系統 (`project.py`)

**當前狀態：** 重構中  
**功能：**
- 雙攝影機即時情緒分析
- 人臉偵測與追蹤
- 年齡、性別、情緒辨識
- 影片錄製與儲存

**使用的技術：**
- Keras 模型進行場景分類（人員進入/離開）
- DeepFace 進行人臉分析
- OpenCV 進行影像處理和攝影機控制
- PIL 進行中文文字渲染

**重構計畫：**
- 🔴 消除硬編碼路徑 → 使用環境變數
- 🔴 重構資料結構 → 使用 CameraState 類別
- 🔴 消除重複程式碼 → 統一處理邏輯
- 🔴 加入錯誤處理 → 重試機制與清楚錯誤訊息

---

## 📦 依賴套件

### 核心依賴
```txt
keras
tensorflow
opencv-python
deepface
numpy
Pillow
matplotlib
python-dotenv  # NEW - 環境變數管理
```

### 開發依賴
```txt
pytest         # NEW - 測試框架
pytest-cov     # NEW - 測試覆蓋率
mypy           # NEW - 型別檢查
```

---

## 🔧 設定管理

### 環境變數（`.env`）

```env
# 模型檔案路徑
MODEL_DIR=./models
KERAS_MODEL_PATH=${MODEL_DIR}/keras_model.h5
LABELS_PATH=${MODEL_DIR}/labels.txt

# 字體路徑
FONT_DIR=./fonts
FONT_PATH=${FONT_DIR}/NotoSansTC-VariableFont_wght.ttf

# 輸出路徑
OUTPUT_DIR=./output
LOG_DIR=./logs

# 日誌設定
LOG_LEVEL=INFO

# 攝影機設定
CAMERA_0_ID=0
CAMERA_1_ID=1
```

---

## 📝 開發工作流程

### 1. 環境設定
```bash
# 啟動虛擬環境
```bash
source .venv/bin/activate
```

# 安裝依賴
pip install -r requirements.txt

# 設定環境變數
cp .env.example .env
# 編輯 .env 檔案，設定正確的路徑
```

### 2. 開發
- 遵循命名規範
- 為新功能撰寫測試
- 使用型別提示
- 撰寫清楚的 docstring

### 3. 測試
```bash
# 執行測試
pytest

# 型別檢查
mypy project.py utils/ models/
```

### 4. 提交
```bash
# 遵循 Conventional Commits
git commit -m "feat: add camera state management"
git commit -m "refactor: extract camera processing logic"
```

---

## 📊 重構進度

### Phase 1: 基礎重構（進行中）

- [ ] 任務 1: 消除硬編碼路徑
- [ ] 任務 2: 重構資料結構
- [ ] 任務 3: 消除重複程式碼
- [ ] 任務 4: 加入錯誤處理

---

**最後更新：** 2025年11月15日

## Running the System

### Prerequisites
```bash
pip install keras opencv-python numpy deepface pillow matplotlib flask ffmpeg-python
```

### Required External Files
- Keras model: `/Users/linjunting/Downloads/converted_keras-2/keras_model.h5`
- Labels file: `/Users/linjunting/Downloads/converted_keras-2/labels.txt`
- Font file: `/Users/linjunting/Downloads/Noto_Sans_TC/NotoSansTC-VariableFont_wght.ttf`
- Haar Cascade XMLs: `haarcascade_*.xml` (already in repo)

### Execution

**Manual mode:**
```bash
python project.py
```
- Press 'q' to manually stop analysis

**Auto-trigger mode:**
```bash
python Auto_Switch.py
```
- Automatically starts when face detected
- Press 'q' to exit monitoring

**View reports:**
```bash
python report_main.py
```
- Open browser to http://localhost:5000

## Key Implementation Details

### Camera Configuration
- Uses cameras at indices 0 and 1 (must have two USB/external cameras)
- Resolution: 320x240 (low-res for performance)
- Frame rate: 5 FPS target
- Analysis interval: Every 1 frame

### Performance Optimization
- Emotion analysis runs every frame_interval (default: 1 frame)
- Age/gender cached after 8 seconds to reduce DeepFace calls
- Previous results reused for skipped frames
- Low resolution preprocessing for classification model (224x224)

### Text Rendering
- Uses PIL ImageFont for Chinese character support (NotoSansTC)
- Custom `putText()` function overlays text on OpenCV frames

### Video Output
- Primary format: AVI (XVID codec)
- Automatic conversion to MP4 via ffmpeg after recording
- Separate files for each camera

## File Organization

**Core Scripts:**
- `project.py` - Main analysis (752 lines)
- `Auto_Switch.py` - Auto-trigger wrapper
- `report_main.py` - Flask web server

**Test/Development:**
- `test.py`, `test2.py` - Development/testing scripts
- `practice.py`, `Helloworld.py` - Learning examples
- `tempCodeRunnerFile.py` - VS Code runner temp file

**Assets:**
- `haarcascade_*.xml` - Face detection cascades
- `*.jpg`, `*.jpeg` - Test images and generated charts
- `output_cam*.mp4/avi` - Recorded sessions

**Web Interface:**
- `report2.HTML` - Main report template
- `report2.CSS` - Styling
- `report2.JS` - Client-side logic

## Branch Information

Current working branch: **AI_FRIEND**
(No main/master branch configured)

## Common Issues

1. **Camera not found**: Ensure two cameras connected at indices 0 and 1
2. **Model file missing**: Update hardcoded paths in scripts to your local model location
3. **Font rendering fails**: Verify NotoSansTC font path exists
4. **ffmpeg errors**: Ensure ffmpeg-python package installed (not system ffmpeg)
