# 程式碼品質審查與改進建議

**審查者視角：基於 Linus Torvalds 的工程哲學與技術標準**

---

## 【核心判斷】

🔴 **品味評分：垃圾**

這個專案雖然功能可以運作，但程式碼品質是一場徹頭徹尾的災難。整個 `project.py` 就是一個 450+ 行的巨型怪物，充滿了糟糕的設計決策、重複的程式碼，以及讓人看了眼睛流血的全域變數污染。

**這不是「能用就好」的問題，而是技術債已經堆積到隨時會崩潰的程度。**

---

## 【致命問題分析】

### 1. 硬編碼路徑災難 🔴

**問題位置：** `project.py:12-13`, `project.py:53`, `Auto_Switch.py:13-14`, `Auto_Switch.py:25`

```python
model = load_model("/Users/linjunting/Downloads/converted_keras-2/keras_model.h5", compile=False)
class_names = [line.strip() for line in open("/Users/linjunting/Downloads/converted_keras-2/labels.txt", "r").readlines()]
font_path = "/Users/linjunting/Downloads/Noto_Sans_TC/NotoSansTC-VariableFont_wght.ttf"
```

**Linus 會說什麼：**
> "What the f*ck is wrong with you? 你是認真覺得每個使用者的檔案都會放在 `/Users/linjunting/Downloads/` 嗎？這是什麼鬼業餘水準？"

**為什麼這是垃圾：**
- 程式碼完全不可移植，換一台電腦就炸掉
- 違反基本的軟體工程原則
- 沒有任何環境變數或設定檔機制
- 這根本不是「能用就好」，而是「只有你的電腦能用」

**正確做法：**
```python
import os
from pathlib import Path

# Use environment variables with sensible defaults
MODEL_DIR = os.getenv('MODEL_DIR', './models')
FONT_DIR = os.getenv('FONT_DIR', './fonts')

model_path = Path(MODEL_DIR) / 'keras_model.h5'
labels_path = Path(MODEL_DIR) / 'labels.txt'
font_path = Path(FONT_DIR) / 'NotoSansTC-VariableFont_wght.ttf'

# Check files exist before loading
if not model_path.exists():
    raise FileNotFoundError(f"Model not found: {model_path}")
```

---

### 2. 全域變數污染 - 18 個全域變數的噩夢 🔴

**問題位置：** `project.py:16-39`

```python
class_1_detected = False
class_2_detected = False
start_time_1 = None
start_time_2 = None
start_time_low_confidence = None
ages_over_time = []
genders_over_time = []
emotions_over_time = []

class_1_detected1 = False      # WTF？
class_2_detected1 = False
start_time_11 = None           # 什麼鬼命名？
start_time_21 = None
start_time_low_confidence1 = None
ages_over_time1 = []
genders_over_time1 = []
emotions_over_time1 = []
result_age = None
result1_age = None
# ... 還有更多
```

**Linus 會說什麼：**
> "Christ, people... 你看看這堆垃圾！18 個全域變數？而且還用 `1` 和 `11` 來區分兩個攝影機？這是我見過最腦殘的命名方式。Bad programmers worry about the code. Good programmers worry about data structures. 你的資料結構根本就是一場災難。"

**為什麼這是災難：**
- **完全沒有封裝**：所有狀態都暴露在全域
- **命名災難**：`class_1_detected1` vs `class_1_detected` 是什麼鬼？
- **無法擴充**：如果要支援 3 個攝影機呢？再加 18 個變數？
- **資料結構設計失敗**：兩個攝影機用完全相同的資料結構，為什麼不用物件或字典？

**正確做法：**
```python
from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass
class CameraState:
    """State for a single camera's emotion analysis"""
    class_1_detected: bool = False
    class_2_detected: bool = False
    start_time_1: Optional[float] = None
    start_time_2: Optional[float] = None
    start_time_low_confidence: Optional[float] = None
    ages_over_time: List[int] = None
    genders_over_time: List[Tuple[str, float]] = None
    emotions_over_time: List[str] = None
    result_age: Optional[int] = None
    result_gender: Optional[str] = None
    result_gender_confidence: Optional[float] = None

    def __post_init__(self):
        if self.ages_over_time is None:
            self.ages_over_time = []
        if self.genders_over_time is None:
            self.genders_over_time = []
        if self.emotions_over_time is None:
            self.emotions_over_time = []

# Now you have clean, scalable data structures
camera_states = {
    'customer': CameraState(),
    'server': CameraState()
}

# Want 3 cameras? Just add one line:
# camera_states['manager'] = CameraState()
```

---

### 3. 重複程式碼 - Copy-Paste 程式設計的完美範例 🔴

**問題位置：** `project.py:206-234`

**相同邏輯重複了兩次：**
```python
# Camera 0 processing
if check_time <= 8:
    result = analyze_frame_A(frame, class_name, confidence_score,
                            emotions_over_time, ages_over_time,
                            genders_over_time, check_time)
    result_age = result['age']
    result_gender = result['gender']
    result_gender_confidence = result['gender_confidence']
else:
    result = analyze_frame_B(frame, class_name, confidence_score,
                            emotions_over_time, check_time)

# Camera 1 processing - EXACTLY THE SAME LOGIC!
if check_time <= 8:
    result1 = analyze_frame_A(frame1, class_name1, confidence_score1,
                             emotions_over_time1, ages_over_time1,
                             genders_over_time1, check_time)
    result1_age = result1['age']
    result1_gender = result1['gender']
    result1_gender_confidence = result1['gender_confidence']
else:
    result1 = analyze_frame_B(frame1, class_name1, confidence_score1,
                             emotions_over_time1, check_time)
```

**Linus 會說什麼：**
> "這是什麼鬼 copy-paste 程式設計？你連最基本的 DRY (Don't Repeat Yourself) 原則都不懂嗎？這種程式碼是垃圾，純粹的垃圾。如果你要修一個 bug，現在得改兩個地方，然後你會忘記改第二個，然後你就有了更多 bug。這是惡性循環。"

**為什麼這是垃圾：**
- 完全相同的邏輯寫了兩遍
- 任何修改都需要改兩個地方
- 增加 bug 的機率
- 程式碼膨脹，難以維護

**正確做法：**
```python
def process_camera_frame(frame, class_name, confidence_score,
                         camera_state, check_time):
    """Process a single camera frame - works for ANY camera"""
    if check_time <= 8:
        result = analyze_frame_A(
            frame, class_name, confidence_score,
            camera_state.emotions_over_time,
            camera_state.ages_over_time,
            camera_state.genders_over_time,
            check_time
        )
        camera_state.result_age = result['age']
        camera_state.result_gender = result['gender']
        camera_state.result_gender_confidence = result['gender_confidence']
    else:
        result = analyze_frame_B(
            frame, class_name, confidence_score,
            camera_state.emotions_over_time,
            check_time
        )
    return result

# Now just call it for each camera
result0 = process_camera_frame(frame, class_name, confidence_score,
                                camera_states['customer'], check_time)
result1 = process_camera_frame(frame1, class_name1, confidence_score1,
                                camera_states['server'], check_time)
```

---

### 4. 巨型主循環 - 100+ 行的怪物 🔴

**問題位置：** `project.py:166-260`

**Linus 會說什麼：**
> "如果你需要超過 3 層縮排，你就已經完蛋了，應該修復你的程式。看看這個主循環，100 多行，嵌套 4-5 層深。這不是程式碼，這是垃圾堆。"

**為什麼這是災難：**
- 主循環做太多事情：讀取畫面、分類、情緒分析、顯示、錄影
- 嵌套過深，難以理解
- 無法測試
- 違反單一職責原則

**正確做法：**
```python
def main_loop(cameras, model, config):
    """Main processing loop - clean and testable"""
    while True:
        # 1. Capture frames
        frames = capture_frames(cameras)
        if not frames:
            break

        # 2. Process each camera
        results = {}
        for cam_id, frame in frames.items():
            results[cam_id] = process_single_camera(
                frame, model, camera_states[cam_id], config
            )

        # 3. Update display
        update_display(frames, results)

        # 4. Record if needed
        record_frames(cameras, frames)

        # 5. Check exit conditions
        if should_exit(camera_states, results):
            break

    # Clean and simple - each function does ONE thing
```

---

### 5. 錯誤處理缺失 🔴

**問題位置：** 整個專案

**目前的「錯誤處理」：**
```python
try:
    analyze = DeepFace.analyze(frame, actions=['emotion', 'age', 'gender'],
                              enforce_detection=False)
    # ... processing ...
except Exception as e:
    print(f"Error in emotion detection: {e}")
    return None  # 然後呢？程式會炸掉
```

**Linus 會說什麼：**
> "吞掉所有例外然後印一行訊息？這是什麼垃圾錯誤處理？你的程式遇到錯誤就默默死掉，使用者根本不知道發生什麼事。這不是錯誤處理，這是掩蓋錯誤。"

**為什麼這是垃圾：**
- `except Exception` 捕捉所有例外，包括你不該捕捉的
- 印出訊息後就忽略錯誤
- 沒有重試機制
- 沒有降級策略
- 攝影機開啟失敗沒有檢查

**正確做法：**
```python
class CameraError(Exception):
    """Custom exception for camera-related errors"""
    pass

def open_camera(camera_id, max_retries=3):
    """Open camera with proper error handling"""
    for attempt in range(max_retries):
        cap = cv2.VideoCapture(camera_id)
        if cap.isOpened():
            logger.info(f"Camera {camera_id} opened successfully")
            return cap

        logger.warning(f"Camera {camera_id} open attempt {attempt + 1} failed")
        time.sleep(1)

    raise CameraError(
        f"Failed to open camera {camera_id} after {max_retries} attempts. "
        f"Check if camera is connected and not in use."
    )

def analyze_frame_with_retry(frame, actions, max_retries=2):
    """Analyze frame with retry logic for transient failures"""
    last_error = None

    for attempt in range(max_retries):
        try:
            return DeepFace.analyze(frame, actions=actions,
                                   enforce_detection=False)
        except ValueError as e:
            # No face detected - this is expected, not an error
            logger.debug(f"No face detected in frame")
            return None
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                logger.warning(f"Analysis failed (attempt {attempt + 1}): {e}")
                time.sleep(0.1)

    # All retries failed
    logger.error(f"Analysis failed after {max_retries} attempts: {last_error}")
    raise
```

---

### 6. 魔術數字到處都是 🔴

**問題位置：** 整個 `project.py`

```python
if (time.time() - start_time_low_confidence) > 3:  # 為什麼是 3？
if check_time <= 8:  # 為什麼是 8？
basicpoint = 60  # 為什麼是 60？
remain = 100 - basicpoint  # 這什麼計算？
negativeweight = -1
neutralweight = 0
positiveweight = 1
```

**Linus 會說什麼：**
> "這些魔術數字是從哪來的？你的屁股嗎？給這些數字一個該死的名字，讓人知道它們代表什麼意思。"

**正確做法：**
```python
# Configuration constants with clear names and documentation
class Config:
    # Detection thresholds
    PRESENCE_DETECTION_DELAY_SEC = 3  # Wait 3s before starting analysis
    ABSENCE_DETECTION_DELAY_SEC = 3   # Wait 3s before stopping
    LOW_CONFIDENCE_TIMEOUT_SEC = 3    # Stop if confidence low for 3s

    # Age/Gender caching
    DEMOGRAPHIC_ANALYSIS_DURATION_SEC = 8  # Analyze demographics for first 8s

    # Scoring weights
    BASELINE_SCORE = 60  # Neutral baseline score
    EMOTION_WEIGHT_RANGE = 40  # Score varies ±40 from baseline

    EMOTION_WEIGHTS = {
        'positive': 1,
        'neutral': 0,
        'negative': -1
    }

    # Camera settings
    TARGET_FPS = 5
    CAMERA_WIDTH = 320
    CAMERA_HEIGHT = 240
```

---

## 【次要但仍需修復的問題】

### 7. 變數命名混亂

```python
class_1_detected1  # 什麼鬼？
start_time_11      # 這是 11 還是 1 的第二個？
cam0scr           # 沒有底線，不一致
```

**改進：**
```python
customer_camera_state.presence_detected
server_camera_state.presence_start_time
customer_emotion_score
```

### 8. 註解品質低劣

```python
# 超過分析超過五秒年齡性別得出結論->直接使用第五秒最後一次判斷的性別年齡結果
```
這註解根本看不懂，而且說的是 5 秒，程式碼寫的是 8 秒。

**改進：**
```python
# Cache demographics after initial analysis period to reduce DeepFace calls
# Demographics are stable, so we only need to analyze them once
if check_time <= Config.DEMOGRAPHIC_ANALYSIS_DURATION_SEC:
    # Still analyzing - update demographics
    analyze_with_demographics(frame, state)
else:
    # Use cached demographics, only update emotions
    analyze_emotions_only(frame, state)
```

### 9. 沒有日誌系統

所有的「錯誤處理」都是 `print()`，這在生產環境是垃圾。

**改進：**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('emotion_analysis.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### 10. 沒有測試

整個專案零測試。怎麼確保程式碼正確？靠運氣嗎？

**需要加入：**
```python
# tests/test_camera_state.py
def test_camera_state_initialization():
    state = CameraState()
    assert state.class_1_detected == False
    assert state.emotions_over_time == []

# tests/test_emotion_scoring.py
def test_emotion_score_calculation():
    emotions = ['happy', 'happy', 'sad']
    score = calculate_emotion_score(emotions)
    assert 60 < score < 80  # More positive than negative
```

---

## 【改進優先順序】

### 🔴 立即修復（否則專案會崩潰）

1. **消除硬編碼路徑** - 使用環境變數和設定檔
2. **重構資料結構** - 用 CameraState 類別取代 18 個全域變數
3. **消除重複程式碼** - 統一雙攝影機處理邏輯
4. **加入適當錯誤處理** - 不要吞掉所有例外

### 🟡 近期改進（技術債）

5. **拆分巨型主循環** - 每個函式只做一件事
6. **消除魔術數字** - 使用具名常數
7. **改善變數命名** - 使用清晰、一致的命名
8. **加入日誌系統** - 取代所有 print()

### 🟢 長期改善（品質提升）

9. **撰寫單元測試** - 至少 60% 覆蓋率
10. **加入型別提示** - 使用 typing 模組
11. **效能優化** - 避免重複計算
12. **文件化** - 為所有公開函式加入 docstring

---

## 【重構範例：完整的 CameraProcessor 類別】

這是「好品味」程式碼應該長什麼樣子：

```python
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class EmotionAnalysisConfig:
    """Configuration for emotion analysis system"""
    model_dir: Path
    font_path: Path
    presence_detection_delay: float = 3.0
    absence_detection_delay: float = 3.0
    demographic_analysis_duration: float = 8.0
    target_fps: int = 5
    camera_width: int = 320
    camera_height: int = 240
    baseline_score: int = 60
    emotion_weight_range: int = 40


class CameraProcessor:
    """Processes emotion analysis for a single camera"""

    def __init__(self, camera_id: int, name: str, config: EmotionAnalysisConfig):
        self.camera_id = camera_id
        self.name = name
        self.config = config
        self.state = CameraState()
        self.cap = None
        self.video_writer = None

    def open(self) -> bool:
        """Open camera and initialize video writer"""
        self.cap = self._open_camera_with_retry()
        if not self.cap:
            return False

        self.video_writer = self._create_video_writer()
        return True

    def _open_camera_with_retry(self, max_retries: int = 3):
        """Open camera with retry logic"""
        for attempt in range(max_retries):
            cap = cv2.VideoCapture(self.camera_id)
            if cap.isOpened():
                self._configure_camera(cap)
                logger.info(f"Camera {self.name} opened successfully")
                return cap

            logger.warning(
                f"Camera {self.name} open attempt {attempt + 1} failed"
            )
            time.sleep(1)

        logger.error(f"Failed to open camera {self.name}")
        return None

    def _configure_camera(self, cap):
        """Configure camera settings"""
        cap.set(cv2.CAP_PROP_FPS, self.config.target_fps)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.camera_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.camera_height)

    def process_frame(self, model) -> Optional[Dict]:
        """Process a single frame and return analysis results"""
        ret, frame = self.cap.read()
        if not ret:
            logger.warning(f"Failed to read frame from {self.name}")
            return None

        # Classify presence
        class_name, confidence = self._classify_frame(frame, model)

        # Update detection state
        self._update_detection_state(class_name, confidence)

        # Perform emotion analysis if person present
        if self._should_analyze():
            return self._analyze_emotions(frame, class_name, confidence)

        return None

    def _classify_frame(self, frame, model) -> Tuple[str, float]:
        """Classify frame using Keras model"""
        # Preprocessing
        resized = cv2.resize(frame, (224, 224), interpolation=cv2.INTER_AREA)
        normalized = (np.asarray(resized, dtype=np.float32) / 127.5) - 1
        batched = normalized.reshape(1, 224, 224, 3)

        # Prediction
        prediction = model.predict(batched, verbose=0)
        index = np.argmax(prediction)

        return self.class_names[index], prediction[0][index]

    def _should_analyze(self) -> bool:
        """Determine if we should perform emotion analysis"""
        if not self.state.class_1_detected:
            return False

        if not self.state.start_time_1:
            return False

        elapsed = time.time() - self.state.start_time_1
        return elapsed > self.config.presence_detection_delay

    def calculate_emotion_score(self) -> float:
        """Calculate final emotion score based on collected data"""
        if not self.state.emotions_over_time:
            return self.config.baseline_score

        # Count emotion categories
        counts = {'positive': 0, 'neutral': 0, 'negative': 0}
        for emotion in self.state.emotions_over_time:
            category = self._categorize_emotion(emotion)
            counts[category] += 1

        total = sum(counts.values())
        if total == 0:
            return self.config.baseline_score

        # Calculate weighted score
        pos_ratio = counts['positive'] / total
        neg_ratio = counts['negative'] / total

        score = (
            self.config.baseline_score +
            self.config.emotion_weight_range * (pos_ratio - neg_ratio)
        )

        return round(score, 2)

    def close(self):
        """Release camera and video writer resources"""
        if self.cap:
            self.cap.release()
        if self.video_writer:
            self.video_writer.release()
        logger.info(f"Camera {self.name} closed")


# Usage is now clean and simple:
def main():
    config = EmotionAnalysisConfig(
        model_dir=Path(os.getenv('MODEL_DIR', './models')),
        font_path=Path(os.getenv('FONT_DIR', './fonts')) / 'NotoSansTC.ttf'
    )

    # Initialize cameras
    cameras = {
        'customer': CameraProcessor(0, 'customer', config),
        'server': CameraProcessor(1, 'server', config)
    }

    # Open all cameras
    for cam in cameras.values():
        if not cam.open():
            logger.error(f"Failed to open camera {cam.name}")
            return

    try:
        # Main loop is now trivial
        while True:
            results = {}
            for name, cam in cameras.items():
                results[name] = cam.process_frame(model)

            if should_exit(cameras):
                break

    finally:
        # Clean up
        for cam in cameras.values():
            cam.close()
```

---

## 【總結：Linus 式的最終判決】

> "Listen, I get it. This is a student project, and it works. But 'it works' is not good enough if you want to be a real engineer. This code is a mess of global variables, copy-paste programming, and hardcoded paths that make it impossible for anyone else to use or maintain.
>
> The fundamental problem is that you never stopped to think about your data structures. You just started coding and kept adding variables until it worked. That's not engineering - that's hacking shit together until it accidentally works.
>
> Good taste in programming means seeing that you have two cameras doing exactly the same thing, and realizing 'hey, maybe I should write ONE function that works for any camera, instead of copying everything twice.' It means understanding that 18 global variables is a flashing red sign that your design is broken.
>
> Fix the data structures first. Everything else will follow. And for f*ck's sake, stop hardcoding paths."

**翻譯成人話：**

這個專案的核心問題不是功能，而是**程式碼組織方式**。你從來沒有好好設計資料結構，只是不斷堆疊全域變數直到功能能用。這不是工程，這是碰運氣。

**真正的解決方案很簡單：**

1. **設計清晰的資料結構** - 用 `CameraState` 類別封裝每個攝影機的狀態
2. **消除重複** - 兩個攝影機用同一個處理函式
3. **提取設定** - 把所有硬編碼的值移到設定檔
4. **一次只做一件事** - 每個函式專注在單一職責

這不是「重寫整個專案」，而是**重新組織現有的程式碼**，讓它變成可維護、可擴充、可測試的系統。

**現在就開始修復，否則當你需要加新功能時，你會發現自己被這堆技術債壓垮。**

---

## 【附錄：快速修復檢查清單】

- [ ] 移除所有硬編碼路徑，使用環境變數
- [ ] 建立 `CameraState` 類別，消除全域變數
- [ ] 建立 `CameraProcessor` 類別，統一處理邏輯
- [ ] 建立 `Config` 類別，集中所有設定
- [ ] 加入適當的例外處理和日誌
- [ ] 拆分主循環，每個函式 < 20 行
- [ ] 所有魔術數字改用具名常數
- [ ] 加入型別提示
- [ ] 撰寫基本單元測試
- [ ] 加入 README 說明如何設定環境變數

**完成這些後，你才有一個真正可以拿出來展示的專案。**
