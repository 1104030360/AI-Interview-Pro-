# Phase 1 重構進度總結

**更新日期：** 2025年11月15日  
**當前狀態：** 基礎設施已完成，準備進行主程式重構

---

## ✅ 已完成的工作

### 1. 基礎設施建立（100%）

所有基礎設施已完成並通過測試：

- ✅ **環境變數管理** (`.env`, `.env.example`)
- ✅ **統一設定模組** (`config.py`)
- ✅ **自訂例外系統** (`exceptions.py`)
- ✅ **資料模型** (`models/camera_state.py`)
- ✅ **日誌系統** (`utils/logging_config.py`)
- ✅ **測試框架** (`tests/` - 6/6 通過)
- ✅ **Git 版本控制** (已提交)

### 2. 關鍵改善

| 問題 | 解決方案 | 狀態 |
|-----|---------|------|
| 硬編碼路徑 | 環境變數 + Config | ✅ |
| 18個全域變數 | CameraState 封裝 | ✅ |
| 魔術數字 | AnalysisConfig | ✅ |
| print() 日誌 | logging 系統 | ✅ |
| 無錯誤處理 | 自訂例外 | ✅ |
| 無測試 | pytest 框架 | ✅ |

---

## 📋 下一步工作計劃

### Phase 1 - 主程式重構

#### 任務 1: 建立輔助工具模組

**目標：** 將 project.py 中的獨立功能提取成可測試的模組

**需要建立的模組：**

1. `utils/classification.py`
   - `classify_frame()` - 影像分類
   - `preprocess_frame()` - 影像預處理

2. `utils/analysis.py`
   - `analyze_with_demographics()` - 完整分析
   - `analyze_emotions_only()` - 僅情緒分析
   - `analyze_frame_with_retry()` - 帶重試的分析

3. `utils/display.py`
   - `draw_analysis_results()` - 繪製分析結果
   - `put_text_chinese()` - 中文文字渲染

4. `utils/video.py`
   - `create_video_writer()` - 建立視訊寫入器
   - `convert_avi_to_mp4()` - 影片格式轉換

5. `utils/visualization.py`
   - `generate_emotion_wave_chart()` - 情緒波動圖
   - `generate_emotion_bar_chart()` - 情緒長條圖
   - `generate_combined_chart()` - 合併圖表

#### 任務 2: 重寫主程式

**策略：** 漸進式重構，保持功能完全一致

**步驟：**

1. **備份原始檔案**
   ```bash
   cp project.py project_original.py
   ```

2. **建立新版本架構**
   ```python
   def main():
       # 1. 初始化 (config, logging, model)
       # 2. 設定攝影機 (camera states, video writers)
       # 3. 主循環 (frame processing, analysis, display)
       # 4. 清理資源 (release cameras, close files)
       # 5. 後處理 (convert videos, generate charts)
   ```

3. **逐步替換功能**
   - 第1步：模型載入 → 使用 `load_keras_model()`
   - 第2步：攝影機開啟 → 使用 `open_camera_with_retry()`
   - 第3步：狀態管理 → 使用 `CameraState`
   - 第4步：分析邏輯 → 使用 utils 模組
   - 第5步：顯示邏輯 → 使用 display 模組
   - 第6步：圖表生成 → 使用 visualization 模組

4. **測試驗證**
   - 單元測試各個模組
   - 整合測試完整流程
   - 對比原始程式輸出

#### 任務 3: 重構 Auto_Switch.py

使用相同的模組化策略重構自動切換程式。

---

## 🎯 優先順序

### 高優先級 (本週完成)

1. ✅ 基礎設施 - **已完成**
2. ⏳ utils/classification.py - **進行中**
3. ⏳ utils/analysis.py - **進行中**
4. 📅 主程式重構 - **規劃中**

### 中優先級 (下週)

5. utils/display.py
6. utils/video.py
7. utils/visualization.py
8. Auto_Switch.py 重構
9. 完整測試套件

### 低優先級 (第三週)

10. 效能優化
11. 文件完善
12. CI/CD 設置

---

## 📝 使用新架構的範例

### 載入模型
```python
# 舊方式（硬編碼）
model = load_model("/Users/.../keras_model.h5", compile=False)
class_names = [line.strip() for line in open("/Users/.../labels.txt", "r").readlines()]

# 新方式（模組化）
from config import Config
from utils.model import load_keras_model

model, class_names = load_keras_model()
```

### 攝影機管理
```python
# 舊方式（無錯誤處理）
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

# 新方式（有重試和例外）
from utils.camera import open_camera_with_retry
from exceptions import CameraOpenError

try:
    cap = open_camera_with_retry(0, max_retries=3)
except CameraOpenError as e:
    logger.error(f"Failed to open camera: {e}")
    sys.exit(1)
```

### 狀態管理
```python
# 舊方式（全域變數）
class_1_detected = False
class_1_detected1 = False
start_time_1 = None
start_time_11 = None
ages_over_time = []
ages_over_time1 = []

# 新方式（封裝）
from models import CameraState

camera_states = {
    'customer': CameraState(),
    'server': CameraState()
}

# 存取
if camera_states['customer'].person_detected:
    elapsed = camera_states['customer'].get_elapsed_time(time.time())
```

### 日誌輸出
```python
# 舊方式
print("Cannot receive frame")
print(f"Error in emotion detection: {e}")

# 新方式
logger.warning("Cannot receive frame")
logger.error(f"Error in emotion detection: {e}", exc_info=True)
```

---

## 🧪 測試策略

### 單元測試

每個模組都應有對應的測試檔案：

- `tests/test_config.py` - 設定驗證
- `tests/test_camera_state.py` - ✅ 已完成
- `tests/test_classification.py` - 分類功能
- `tests/test_analysis.py` - 分析功能
- `tests/test_camera_processing.py` - 處理邏輯

### 整合測試

```python
# tests/test_integration.py
def test_full_pipeline_with_mock_data():
    """使用模擬數據測試完整流程"""
    # 1. 載入模型
    # 2. 初始化狀態
    # 3. 處理模擬畫面
    # 4. 驗證輸出
```

### 回歸測試

確保重構後行為完全一致：

```python
def test_output_matches_original():
    """對比新舊版本的輸出"""
    # 使用相同輸入
    # 比較輸出結果
    # 允許浮點數誤差
```

---

## 📊 預期效果

### 重構後的改善

| 指標 | 重構前 | 重構後（目標） |
|-----|-------|--------------|
| 程式碼行數 | 450+ | 300 (主程式) + 400 (模組) |
| 函式平均長度 | 50+ 行 | < 30 行 |
| 巢狀深度 | 4-5 層 | <= 2 層 |
| 全域變數 | 18 個 | 0 個 |
| 測試覆蓋率 | 0% | > 60% |
| 重複程式碼 | 大量 | 最小化 |

### 可維護性提升

- ✅ 每個函式職責單一
- ✅ 易於理解和修改
- ✅ 容易新增功能（如第三個攝影機）
- ✅ 錯誤容易追蹤
- ✅ 可以獨立測試每個部分

---

## 💬 重要備註

### 保持向後相容

重構過程中**最重要**的原則：**功能完全不變**

- 所有偵測邏輯保持一致
- 計時參數保持一致（3秒、8秒等）
- 評分計算保持一致
- 輸出格式保持一致

### 逐步驗證

每完成一個模組就：

1. 寫測試
2. 執行測試
3. 提交 git
4. 繼續下一個

### 文件同步

隨著程式碼更新，同步更新：

- `README.md` - 使用說明
- `docs/architecture/backend-arch.md` - 架構說明
- `docs/API.md` - API 文件

---

## 🔗 相關文件

- [基礎設施報告](reports/2025-11-15-基礎設施-REP.md)
- [TODO 清單](todo/2025-11-15-基礎設施-TODO.md)
- [Phase 1 計畫](plans/phase1.md)
- [程式碼審查](../../CODE_REVIEW_IMPROVEMENTS.md)

---

**最後更新：** 2025年11月15日  
**狀態：** 基礎設施完成 ✅ | 主程式重構進行中 ⏳
