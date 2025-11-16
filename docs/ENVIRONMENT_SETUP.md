# 環境設定指南

**更新日期：** 2025年11月16日  
**Python 版本：** 3.8.8  
**虛擬環境：** `.venv`

---

## 📋 系統需求

### 作業系統
- macOS (推薦)
- Linux
- Windows

### Python 版本
- Python 3.8.8 (必須)
  - 使用 Anaconda 或 pyenv 安裝

### 硬體需求
- 雙攝影機（內建 + USB 外接）
- 記憶體：至少 8GB RAM
- 硬碟：至少 5GB 可用空間

---

## 🚀 快速開始

### 1. 複製專案

```bash
git clone https://github.com/1104030360/Multimodal-Data-Applied-to-Service-Industry-Satisfaction-Analysis-.git
cd 專題python
```

### 2. 建立並啟用虛擬環境

**使用現有的 .venv（推薦）：**

```bash
# 啟用虛擬環境
source .venv/bin/activate  # macOS/Linux
# 或
.venv\Scripts\activate  # Windows

# 確認 Python 版本
python --version  # 應該顯示 Python 3.8.8
```

**或重新建立虛擬環境：**

```bash
# 確保使用 Python 3.8.8
python3.8 -m venv .venv

# 啟用虛擬環境
source .venv/bin/activate

# 升級 pip
pip install --upgrade pip
```

### 3. 安裝依賴套件

```bash
# 安裝所有必要套件
pip install -r requirements.txt

# 這將安裝：
# - tensorflow==2.13.1
# - keras==2.13.1
# - deepface==0.0.85
# - opencv-python==4.9.0.80
# - python-dotenv==1.0.1
# - pytest==8.3.5
# - pytest-cov==5.0.0
# - 以及其他依賴套件
```

### 4. 設定環境變數

```bash
# 複製環境變數範例檔
cp .env.example .env

# 編輯 .env 檔案，設定正確的路徑
nano .env  # 或使用其他編輯器
```

**必須設定的環境變數：**

```properties
# 模型檔案路徑
MODEL_DIR=/Users/你的使用者名稱/Downloads/converted_keras-2
KERAS_MODEL_PATH=/Users/你的使用者名稱/Downloads/converted_keras-2/keras_model.h5
LABELS_PATH=/Users/你的使用者名稱/Downloads/converted_keras-2/labels.txt

# 字體檔案路徑（用於顯示中文）
FONT_DIR=/Users/你的使用者名稱/Downloads/Noto_Sans_TC
FONT_PATH=/Users/你的使用者名稱/Downloads/Noto_Sans_TC/NotoSansTC-VariableFont_wght.ttf
```

### 5. 驗證安裝

```bash
# 測試所有核心套件
python -c "
import tensorflow as tf
import keras
import deepface
import cv2
import pytest
print('✅ TensorFlow:', tf.__version__)
print('✅ Keras:', keras.__version__)
print('✅ DeepFace installed')
print('✅ OpenCV:', cv2.__version__)
print('✅ Pytest installed')
print('\n🎉 環境設定成功！')
"
```

### 6. 執行測試

```bash
# 執行所有測試
pytest tests/ -v

# 執行特定測試
pytest tests/test_camera_state.py -v

# 執行測試並產生覆蓋率報告
pytest --cov=. --cov-report=html
```

---

## 📦 核心套件說明

### TensorFlow & Keras (2.13.1)
- **用途：** 載入和執行 Keras 模型進行影像分類
- **限制：** 必須使用 2.13.1 版本以相容現有模型

### DeepFace (0.0.85)
- **用途：** 臉部偵測、情緒分析、年齡/性別辨識
- **功能：** 
  - 情緒分類（7 種情緒）
  - 年齡估計
  - 性別判斷

### OpenCV (4.9.0.80)
- **用途：** 攝影機存取、影像處理、視訊錄製
- **功能：**
  - 雙攝影機管理
  - 即時影像處理
  - 人臉偵測（Haar Cascade）

### Python-dotenv (1.0.1)
- **用途：** 載入 .env 環境變數
- **重要性：** 管理敏感設定和路徑

### Pytest (8.3.5)
- **用途：** 單元測試框架
- **覆蓋率：** pytest-cov 套件提供測試覆蓋率報告

---

## 🔧 常見問題排解

### 問題 1：ImportError: No module named 'tensorflow'

**原因：** 虛擬環境未啟用或套件未安裝

**解決方法：**
```bash
# 確認虛擬環境已啟用
which python  # 應該顯示 .venv/bin/python

# 如果沒有，啟用虛擬環境
source .venv/bin/activate

# 重新安裝套件
pip install -r requirements.txt
```

### 問題 2：無法開啟攝影機

**原因：** 攝影機權限未授予或攝影機被佔用

**解決方法：**
```bash
# macOS: 檢查系統偏好設定 > 安全性與隱私 > 攝影機
# 確保終端機或 Python 有攝影機存取權限

# 測試攝影機
python -c "
import cv2
cap = cv2.VideoCapture(0)
if cap.isOpened():
    print('✅ 攝影機 0 可用')
    cap.release()
else:
    print('❌ 攝影機 0 無法開啟')
"
```

### 問題 3：FileNotFoundError: Model file not found

**原因：** .env 中的路徑設定錯誤

**解決方法：**
```bash
# 檢查模型檔案是否存在
ls -l /Users/你的使用者名稱/Downloads/converted_keras-2/keras_model.h5

# 如果不存在，更新 .env 中的 KERAS_MODEL_PATH
nano .env
```

### 問題 4：中文字無法顯示

**原因：** 字體檔案路徑錯誤或字體未安裝

**解決方法：**
```bash
# 下載 Noto Sans TC 字體
# https://fonts.google.com/noto/specimen/Noto+Sans+TC

# 解壓縮到指定位置
# 更新 .env 中的 FONT_PATH
```

### 問題 5：Python 版本不符

**原因：** 系統 Python 版本不是 3.8.8

**解決方法：**
```bash
# 使用 pyenv 安裝 Python 3.8.8
pyenv install 3.8.8
pyenv local 3.8.8

# 或使用 Anaconda
conda create -n emotion-analysis python=3.8.8
conda activate emotion-analysis

# 重新建立虛擬環境
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 🎯 執行程式

### 執行重構版本（推薦）

```bash
# 啟用虛擬環境
source .venv/bin/activate

# 執行主程式
python project_refactored.py

# 或執行自動觸發系統
python Auto_Switch_refactored.py
```

### 執行原始版本

```bash
# 啟用虛擬環境
source .venv/bin/activate

# 執行原始主程式
python project.py

# 或執行原始自動觸發系統
python Auto_Switch.py
```

### 操作說明

1. **啟動程式**：執行上述指令
2. **開始偵測**：當 Class 1 或 Class 2 被偵測到時自動開始
3. **情緒分析**：偵測滿 3 秒後開始情緒分析
4. **停止分析**：離開座位 3 秒後自動停止
5. **結束程式**：按下 `Q` 鍵
6. **產生報告**：程式結束時自動產生圖表

---

## 📊 專案結構

```
專題python/
├── .venv/                    # 虛擬環境 ⭐ 使用此環境
├── .env                      # 環境變數（需手動設定）
├── .env.example              # 環境變數範例
├── config.py                 # 設定管理
├── exceptions.py             # 例外處理
├── models/                   # 資料模型
│   └── camera_state.py
├── utils/                    # 工具模組
│   ├── camera.py            # 攝影機管理
│   ├── classification.py    # 影像分類
│   ├── analysis.py          # 情緒分析
│   ├── display.py           # 顯示功能
│   ├── video.py             # 視訊處理
│   └── ...
├── tests/                    # 測試檔案
├── project_refactored.py    # 主程式（重構版）⭐
├── Auto_Switch_refactored.py# 自動觸發（重構版）⭐
└── requirements.txt          # 依賴清單
```

---

## 🔄 虛擬環境管理

### 切換到 .venv

```bash
# 停用當前環境（如果已啟用）
deactivate

# 啟用 .venv
source .venv/bin/activate

# 確認環境
which python  # 應顯示：.../專題python/.venv/bin/python
python --version  # 應顯示：Python 3.8.8
```

### 更新套件

```bash
# 啟用虛擬環境
source .venv/bin/activate

# 更新單一套件
pip install --upgrade <套件名稱>

# 更新所有套件（不建議，可能破壞相容性）
pip list --outdated

# 重新安裝所有套件
pip install -r requirements.txt --force-reinstall
```

### 匯出套件清單

```bash
# 匯出當前環境的所有套件
pip freeze > requirements_new.txt

# 比較差異
diff requirements.txt requirements_new.txt
```

---

## 📝 開發工作流程

### 1. 開始開發

```bash
# 進入專案目錄
cd /Users/你的使用者名稱/Desktop/專題python

# 啟用虛擬環境
source .venv/bin/activate

# 拉取最新程式碼
git pull origin AI_FRIEND

# 建立新分支（如果需要）
git checkout -b feature/your-feature-name
```

### 2. 開發過程

```bash
# 執行測試（確保現有功能正常）
pytest tests/ -v

# 進行開發...

# 再次執行測試
pytest tests/ -v

# 檢查程式碼品質
flake8 .  # （如果已安裝）
```

### 3. 提交變更

```bash
# 檢查變更
git status
git diff

# 加入變更
git add .

# 提交
git commit -m "feat: 你的功能描述"

# 推送
git push origin feature/your-feature-name
```

---

## 🎓 學習資源

### 官方文件
- [TensorFlow 文件](https://www.tensorflow.org/api_docs/python/tf)
- [Keras 文件](https://keras.io/)
- [DeepFace GitHub](https://github.com/serengil/deepface)
- [OpenCV 文件](https://docs.opencv.org/)

### 專案相關
- [Phase 1 計畫](docs/schedule/plans/phase1.md)
- [工具模組文件](docs/schedule/UTILS_MODULES_DOC.md)
- [重構對比報告](docs/schedule/reports/2025-11-16-重構對比-REP.md)

---

## ✅ 檢查清單

完成環境設定後，確認以下項目：

- [ ] Python 3.8.8 已安裝
- [ ] `.venv` 虛擬環境已建立並啟用
- [ ] 所有依賴套件已安裝（requirements.txt）
- [ ] `.env` 檔案已設定正確路徑
- [ ] 模型檔案存在且可讀取
- [ ] 字體檔案存在且可讀取
- [ ] 攝影機可以正常存取
- [ ] 測試可以成功執行（pytest）
- [ ] 可以成功執行 `project_refactored.py`

---

**設定完成！開始享受情緒分析系統吧！** 🎉
