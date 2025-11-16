# 🚀 快速開始指南

**更新日期：** 2025年11月16日  
**環境：** Conda `new_tf_env` (Python 3.8.18)

---

## ⚡ 3 步驟開始

### 1️⃣ 啟用環境

```bash
conda activate new_tf_env
```

### 2️⃣ 設定路徑

編輯 `.env` 檔案，設定正確的模型和字體路徑：

```properties
MODEL_DIR=/Users/你的使用者名稱/Downloads/converted_keras-2
KERAS_MODEL_PATH=/Users/你的使用者名稱/Downloads/converted_keras-2/keras_model.h5
LABELS_PATH=/Users/你的使用者名稱/Downloads/converted_keras-2/labels.txt
FONT_PATH=/Users/你的使用者名稱/Downloads/Noto_Sans_TC/NotoSansTC-VariableFont_wght.ttf
```

### 3️⃣ 執行程式

```bash
# 執行重構版主程式（推薦）
python project_refactored.py

# 或執行自動觸發版本
python Auto_Switch_refactored.py
```

---

## 📋 環境資訊

### Conda 環境：`new_tf_env`

- **Python:** 3.8.18
- **位置:** `/Users/linjunting/miniforge3/envs/new_tf_env`
- **特色:** ✨ 支援 Metal GPU 加速（M1/M2 Mac）

### 已安裝套件

| 套件 | 版本 | 用途 |
|-----|------|------|
| TensorFlow | 2.13.0 | 深度學習框架 + Metal 加速 |
| Keras | 2.13.1 | 高階神經網路 API |
| DeepFace | 0.0.85 | 臉部辨識與情緒分析 |
| OpenCV | 4.9.0 | 電腦視覺與攝影機處理 |
| Pytest | 8.3.5 | 測試框架 |
| python-dotenv | 1.0.1 | 環境變數管理 |

---

## 🎯 常用指令

### 環境管理

```bash
# 啟用環境
conda activate new_tf_env

# 檢查環境
conda env list

# 確認當前環境
echo $CONDA_DEFAULT_ENV

# 停用環境
conda deactivate
```

### 執行程式

```bash
# 啟用環境
conda activate new_tf_env

# 執行主程式（重構版）
python project_refactored.py

# 執行自動觸發系統（重構版）
python Auto_Switch_refactored.py

# 執行原始版本
python project.py

# 結束程式：按 Q 鍵
```

### 測試

```bash
# 執行所有測試
pytest tests/ -v

# 執行特定測試
pytest tests/test_camera_state.py -v

# 執行測試並產生覆蓋率報告
pytest --cov=. --cov-report=html

# 查看覆蓋率報告
open htmlcov/index.html
```

### Git 操作

```bash
# 檢查狀態
git status

# 拉取最新程式碼
git pull origin AI_FRIEND

# 提交變更
git add .
git commit -m "feat: 你的變更說明"
git push origin AI_FRIEND
```

---

## 🔧 驗證環境

```bash
# 快速驗證
conda activate new_tf_env
python -c "import tensorflow as tf; import keras; import cv2; print('✅ 環境正常')"

# 完整驗證
python -c "
import sys, tensorflow as tf, keras, deepface, cv2, pytest
from dotenv import load_dotenv

print('=' * 50)
print('🔍 環境驗證')
print('=' * 50)
print(f'Python: {sys.version.split()[0]}')
print(f'TensorFlow: {tf.__version__}')
print(f'Keras: {keras.__version__}')
print(f'OpenCV: {cv2.__version__}')
print('=' * 50)
print('✅ 所有核心套件正常！')
"
```

---

## 📁 專案結構

```
專題python/
├── .env                      # 環境變數設定 ⚙️
├── config.py                 # 設定管理模組
├── exceptions.py             # 例外處理
│
├── models/                   # 資料模型
│   └── camera_state.py
│
├── utils/                    # 工具模組 🛠️
│   ├── camera.py            # 攝影機管理
│   ├── classification.py    # 影像分類
│   ├── analysis.py          # 情緒分析
│   ├── display.py           # 顯示功能
│   ├── video.py             # 視訊處理
│   └── ...
│
├── tests/                    # 測試檔案 ✅
│   └── test_*.py
│
├── project_refactored.py    # 主程式（重構版）⭐
├── Auto_Switch_refactored.py# 自動觸發（重構版）⭐
│
├── project.py               # 主程式（原始版）
├── Auto_Switch.py           # 自動觸發（原始版）
│
└── docs/                    # 文件 📚
    ├── ENVIRONMENT_SETUP.md # 完整環境設定指南
    └── ...
```

---

## 💡 使用技巧

### 1. 自動啟用環境

編輯 `~/.zshrc` 或 `~/.bashrc`：

```bash
# 進入專案目錄時自動啟用環境
cd_專題() {
    cd ~/Desktop/專題python
    conda activate new_tf_env
}
alias 專題=cd_專題
```

之後只需輸入 `專題` 即可進入專案並啟用環境。

### 2. 快速測試攝影機

```bash
python -c "
import cv2
cap0 = cv2.VideoCapture(0)
cap1 = cv2.VideoCapture(1)
print('攝影機 0:', '✅ 可用' if cap0.isOpened() else '❌ 無法開啟')
print('攝影機 1:', '✅ 可用' if cap1.isOpened() else '❌ 無法開啟')
cap0.release()
cap1.release()
"
```

### 3. 檢查模型檔案

```bash
# 檢查模型是否存在
ls -lh ~/Downloads/converted_keras-2/keras_model.h5

# 檢查字體是否存在
ls -lh ~/Downloads/Noto_Sans_TC/*.ttf
```

---

## ⚠️ 常見問題

### Q: 環境未啟用？

```bash
# 確認當前環境
echo $CONDA_DEFAULT_ENV

# 如果是空的，啟用環境
conda activate new_tf_env
```

### Q: 找不到模組？

```bash
# 確認使用正確的 Python
which python  # 應顯示 miniforge3/envs/new_tf_env/bin/python

# 如果不對，重新啟用環境
conda deactivate
conda activate new_tf_env
```

### Q: 攝影機權限問題？

**macOS:**
1. 開啟「系統偏好設定」
2. 點選「安全性與隱私」
3. 選擇「攝影機」標籤
4. 勾選「終端機」或你使用的 IDE

---

## 📚 更多資源

- **完整設定指南：** [docs/ENVIRONMENT_SETUP.md](docs/ENVIRONMENT_SETUP.md)
- **專案結構：** [CLAUDE.md](CLAUDE.md)
- **Phase 1 計畫：** [docs/schedule/plans/phase1.md](docs/schedule/plans/phase1.md)
- **工具模組文件：** [docs/schedule/UTILS_MODULES_DOC.md](docs/schedule/UTILS_MODULES_DOC.md)
- **重構對比報告：** [docs/schedule/reports/2025-11-16-重構對比-REP.md](docs/schedule/reports/2025-11-16-重構對比-REP.md)

---

## 🎓 操作流程

### 完整工作流程

```bash
# 1. 啟用環境
conda activate new_tf_env

# 2. 進入專案目錄
cd ~/Desktop/專題python

# 3. 拉取最新程式碼
git pull origin AI_FRIEND

# 4. 執行測試（可選）
pytest tests/ -v

# 5. 執行程式
python project_refactored.py

# 6. 程式操作：
#    - 偵測到 Class 1/2 後自動開始
#    - 偵測 3 秒後開始情緒分析
#    - 離開座位 3 秒後自動停止
#    - 按 Q 鍵結束並產生圖表

# 7. 查看產生的圖表
open *.jpg
```

---

**準備好了嗎？開始使用吧！** 🚀

```bash
conda activate new_tf_env
python project_refactored.py
```
