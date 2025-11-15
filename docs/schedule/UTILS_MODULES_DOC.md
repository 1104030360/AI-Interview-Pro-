# 工具模組完整文件

**建立日期：** 2025年11月15日  
**狀態：** ✅ 完成

---

## 📦 模組架構

```
utils/
├── __init__.py           # 模組導出
├── logging_config.py     # 日誌系統
├── camera.py             # 攝影機管理
├── model.py              # 模型載入
├── classification.py     # 影像分類
├── analysis.py           # 情緒分析
├── display.py            # 顯示功能
├── video.py              # 視訊處理
├── visualization.py      # 圖表生成
└── camera_processing.py  # 攝影機處理邏輯
```

---

## 🔧 模組詳細說明

### 1. logging_config.py
**功能：** 設定和管理日誌系統

**主要函式：**
- `setup_logging()` - 設定日誌系統（檔案 + 控制台）
- `get_logger(name)` - 獲取指定名稱的 logger

**特色：**
- 自動日誌輪換（10MB，保留5個備份）
- 同時輸出到檔案和控制台
- 可設定日誌等級

---

### 2. camera.py
**功能：** 攝影機初始化、設定和資源管理

**主要函式：**
- `open_camera_with_retry(camera_id, max_retries=3)` - 開啟攝影機（帶重試）
- `configure_camera(cap, fps, width, height)` - 設定攝影機參數
- `read_frame(cap)` - 讀取影像幀
- `release_camera(*caps)` - 釋放攝影機資源
- `get_camera_info(cap)` - 獲取攝影機資訊

**特色：**
- 自動重試機制
- 完整錯誤處理
- 參數驗證

**使用範例：**
```python
from utils import open_camera_with_retry, configure_camera

# 開啟並設定攝影機
cap = open_camera_with_retry(0, max_retries=3)
configure_camera(cap, fps=5, width=320, height=240)
```

---

### 3. model.py
**功能：** Keras 模型載入和驗證

**主要函式：**
- `load_keras_model(max_retries=3)` - 載入模型和標籤
- `validate_model(model, expected_input_shape)` - 驗證模型

**特色：**
- 自動從 Config 讀取路徑
- 帶重試機制
- 檔案存在性檢查

**使用範例：**
```python
from utils import load_keras_model

model, class_names = load_keras_model()
print(f"Loaded model with {len(class_names)} classes")
```

---

### 4. classification.py
**功能：** 影像預處理和分類

**主要函式：**
- `preprocess_frame(frame, target_size=(224,224))` - 預處理影像
- `classify_frame(frame, model, class_names)` - 分類影像
- `is_person_detected(class_name, confidence_score)` - 判斷是否偵測到人
- `is_session_end(class_name)` - 判斷是否結束會話

**特色：**
- 標準化預處理流程
- 信心度檢查
- 清晰的返回值

**使用範例：**
```python
from utils import classify_frame, is_person_detected

class_name, confidence = classify_frame(frame, model, class_names)
if is_person_detected(class_name, confidence):
    print("Person detected!")
```

---

### 5. analysis.py
**功能：** 情緒、年齡、性別分析

**主要函式：**
- `analyze_with_demographics(frame, class_name, confidence)` - 完整分析
- `analyze_emotions_only(frame, class_name, confidence)` - 僅情緒分析
- `analyze_frame_with_retry(...)` - 帶重試的分析
- `categorize_emotion(emotion)` - 情緒分類（正/負/中）
- `map_emotion_to_score(emotion)` - 情緒映射為分數
- `calculate_emotion_statistics(emotions)` - 計算情緒統計
- `calculate_satisfaction_score(emotions, baseline=60)` - 計算滿意度分數

**特色：**
- 完整的 DeepFace 整合
- 重試機制
- 詳細的統計計算
- 滿意度分數演算法

**使用範例：**
```python
from utils import analyze_with_demographics, calculate_satisfaction_score

# 分析單一畫面
result = analyze_with_demographics(frame, 'Class 1', 0.95)
print(f"Emotion: {result['emotion']}, Age: {result['age']}")

# 計算滿意度
emotions = ['happy', 'neutral', 'sad', 'happy']
score = calculate_satisfaction_score(emotions)
print(f"Satisfaction: {score}/100")
```

---

### 6. display.py
**功能：** 影像顯示和文字繪製

**主要函式：**
- `put_text_chinese(img, text, x, y, font_size, color)` - 繪製中文文字
- `draw_analysis_results(img, results, show_demographics)` - 繪製分析結果
- `resize_and_flip_frame(frame, target_size, flip)` - 調整和翻轉
- `create_split_screen(frame1, frame2, orientation)` - 建立分割畫面

**特色：**
- 中文字體支援
- 統一的顯示格式
- 彈性的佈局選項

**使用範例：**
```python
from utils import draw_analysis_results, put_text_chinese

# 繪製完整分析結果
img = draw_analysis_results(img, result, show_demographics=True)

# 繪製自訂文字
img = put_text_chinese(img, "偵測中...", 10, 30, font_size=32)
```

---

### 7. video.py
**功能：** 視訊錄製和格式轉換

**主要函式：**
- `create_video_writer(output_path, fps, frame_size, fourcc)` - 建立錄影器
- `convert_avi_to_mp4(input_file, output_file, remove_source)` - 格式轉換
- `release_video_resources(*writers)` - 釋放資源
- `get_video_info(video_path)` - 獲取視訊資訊

**特色：**
- FFmpeg 整合
- 自動格式轉換
- 完整的錯誤處理

**使用範例：**
```python
from utils import create_video_writer, convert_avi_to_mp4

# 建立錄影器
writer = create_video_writer('output.avi', fps=5, frame_size=(320, 240))

# 錄製後轉換
convert_avi_to_mp4('output.avi', 'output.mp4', remove_source=True)
```

---

### 8. visualization.py
**功能：** 生成情緒分析圖表

**主要函式：**
- `generate_emotion_wave_chart(emotions, output_path, ...)` - 波動圖
- `generate_emotion_bar_chart(emotions, output_path, ...)` - 長條圖
- `generate_combined_wave_chart(emotions1, emotions2, ...)` - 雙攝影機對比圖
- `generate_demographics_title(ages, genders)` - 生成標題
- `generate_all_charts(emotions, ages, genders, ...)` - 生成所有圖表

**特色：**
- Matplotlib 整合
- 美觀的圖表設計
- 自動計算統計
- 支援雙攝影機對比

**使用範例：**
```python
from utils import generate_all_charts

# 生成所有圖表
emotions = ['happy', 'neutral', 'sad']
ages = [25, 26, 25]
genders = [('Male', 0.92), ('Male', 0.91), ('Male', 0.93)]

generate_all_charts(emotions, ages, genders, camera_name='Customer')
```

---

### 9. camera_processing.py
**功能：** 統一的攝影機處理邏輯

**主要函式：**
- `process_camera_frame(...)` - 處理單一攝影機幀
- `should_exit(camera_states, frame_count)` - 判斷是否退出

**特色：**
- 消除雙攝影機重複程式碼
- 統一的邏輯流程
- CameraState 整合

**使用範例：**
```python
from utils import process_camera_frame
from models import CameraState

state = CameraState()
result = process_camera_frame(
    frame, model, class_names, state, 
    camera_name='customer'
)
```

---

## 📊 程式碼統計

| 模組 | 行數 | 函式數 | 用途 |
|-----|------|--------|------|
| logging_config.py | 60 | 2 | 日誌系統 |
| camera.py | 170 | 6 | 攝影機管理 |
| model.py | 90 | 2 | 模型載入 |
| classification.py | 120 | 4 | 影像分類 |
| analysis.py | 280 | 8 | 情緒分析 |
| display.py | 140 | 4 | 顯示功能 |
| video.py | 140 | 4 | 視訊處理 |
| visualization.py | 250 | 5 | 圖表生成 |
| camera_processing.py | 160 | 2 | 處理邏輯 |
| **總計** | **~1,410** | **37** | **完整工具集** |

---

## 🎯 使用方式

### 簡化導入

所有函式都可以從 `utils` 直接導入：

```python
from utils import (
    setup_logging,
    load_keras_model,
    open_camera_with_retry,
    classify_frame,
    analyze_with_demographics,
    draw_analysis_results,
    generate_all_charts
)
```

### 完整範例

```python
from config import Config
from models import CameraState
from utils import (
    setup_logging, get_logger,
    load_keras_model,
    open_camera_with_retry,
    configure_camera,
    classify_frame,
    analyze_with_demographics,
    draw_analysis_results,
    generate_all_charts
)

# 1. 初始化
config = Config()
setup_logging()
logger = get_logger(__name__)

# 2. 載入模型
model, class_names = load_keras_model()

# 3. 開啟攝影機
cap = open_camera_with_retry(0)
configure_camera(cap)

# 4. 初始化狀態
state = CameraState()

# 5. 處理畫面
ret, frame = cap.read()
class_name, confidence = classify_frame(frame, model, class_names)
result = analyze_with_demographics(frame, class_name, confidence)

# 6. 顯示結果
img = draw_analysis_results(frame, result)

# 7. 生成圖表
generate_all_charts(
    state.emotions,
    state.ages,
    state.genders,
    camera_name='Camera0'
)
```

---

## ✅ 驗證清單

- [x] 所有模組已建立
- [x] 所有函式都有 docstring
- [x] 所有函式都有型別提示
- [x] 所有模組都有錯誤處理
- [x] 所有模組都有日誌整合
- [x] __init__.py 已更新
- [x] Git 已提交

---

## 🔄 與原始程式碼的對應

| 原始功能 | 對應模組 | 對應函式 |
|---------|---------|---------|
| `load_model()` | model.py | `load_keras_model()` |
| `process_frame()` | classification.py | `classify_frame()` |
| `putText()` | display.py | `put_text_chinese()` |
| `analyze_frame_A()` | analysis.py | `analyze_with_demographics()` |
| `analyze_frame_B()` | analysis.py | `analyze_emotions_only()` |
| `convert_avi_to_mp4()` | video.py | `convert_avi_to_mp4()` |
| 情緒波動圖 | visualization.py | `generate_emotion_wave_chart()` |
| 情緒長條圖 | visualization.py | `generate_emotion_bar_chart()` |
| 攝影機初始化 | camera.py | `open_camera_with_retry()` + `configure_camera()` |
| 滿意度計算 | analysis.py | `calculate_satisfaction_score()` |

---

## 📝 下一步

現在所有工具模組都已完成，可以開始：

1. **重寫 project.py** - 使用新模組
2. **撰寫測試** - 為新模組建立測試
3. **整合測試** - 確保功能一致

---

**最後更新：** 2025年11月15日  
**狀態：** 所有工具模組完成 ✅
