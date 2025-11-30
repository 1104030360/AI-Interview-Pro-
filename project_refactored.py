"""
情緒分析主程式（重構版）

使用模組化架構重構，消除硬編碼和全域變數，提供完整的錯誤處理。

主要改進：
- 使用 Config 管理所有設定
- 使用 CameraState 封裝狀態
- 使用工具模組函式
- 完整的錯誤處理和日誌
- 消除重複程式碼
"""
import cv2
import sys
import time
import json
import datetime
from pathlib import Path

from config import Config
from models import CameraState
from utils import (
    setup_logging,
    get_logger,
    load_keras_model,
    classify_frame,
    analyze_with_demographics,
    analyze_emotions_only,
    draw_analysis_results,
    resize_and_flip_frame,
    create_video_writer,
    convert_avi_to_mp4,
    release_video_resources,
    generate_all_charts,
    generate_combined_wave_chart,
    calculate_satisfaction_score,
    AsyncDeepFaceAnalyzer,
    ThreadedCamera,
    AsyncCameraInitializer
)
from exceptions import CameraOpenError, ModelLoadError


class EmotionAnalysisSystem:
    """情緒分析系統主類別"""
    
    def __init__(self):
        """初始化系統"""
        self.config = Config()
        self.logger = None
        self.model = None
        self.class_names = None
        self.cameras = {}
        self.camera_states = {}
        self.video_writers = {}
        self.analyzers = {}  # Async DeepFace analyzers
        self.frame_count = 0
        self.exit_by_user = False
        self.previous_results = {
            'customer': None,
            'server': None
        }
        
    def initialize(self):
        """初始化所有組件（使用並行初始化以最大化性能）"""
        try:
            # 設定日誌
            setup_logging()
            self.logger = get_logger(__name__)
            self.logger.info("=== 情緒分析系統啟動（ThreadedCamera 優化版）===")

            # 【並行 Phase 1】啟動攝影機異步初始化（背景執行，非阻塞）
            self.logger.info("【並行初始化】啟動攝影機背景初始化...")
            camera_initializers = self._start_async_camera_init()

            # 【並行執行】載入 Keras 模型（與攝影機初始化同時進行）
            self.logger.info("【並行執行】載入 Keras 模型...")
            self.model, self.class_names = load_keras_model()
            self.logger.info(f"模型載入成功，類別數：{len(self.class_names)}")

            # 【並行 Phase 2】等待攝影機初始化完成
            self._wait_for_cameras(camera_initializers)

            # 初始化狀態
            self.camera_states = {}
            for cam_conf in self.config.camera.get_active_cameras():
                self.camera_states[cam_conf['name']] = CameraState()

            # 初始化視訊錄製
            self._initialize_video_writers()

            # 初始化 Async DeepFace 分析器
            self._initialize_async_analyzers()

            self.logger.info("系統初始化完成（ThreadedCamera + AsyncDeepFace）")
            return True
            
        except ModelLoadError as e:
            if self.logger:
                self.logger.error(f"模型載入失敗：{e}")
            else:
                print(f"模型載入失敗：{e}")
            return False
        except CameraOpenError as e:
            if self.logger:
                self.logger.error(f"攝影機開啟失敗：{e}")
            else:
                print(f"攝影機開啟失敗：{e}")
            return False
        except Exception as e:
            if self.logger:
                self.logger.error(f"初始化失敗：{e}", exc_info=True)
            else:
                print(f"初始化失敗：{e}")
            return False
    
    def _start_async_camera_init(self):
        """
        啟動攝影機異步初始化（Phase 1：非阻塞）

        Returns:
            Dict[str, Tuple]: {camera_name: (initializer, cam_conf)}
        """
        active_cameras = self.config.camera.get_active_cameras()
        camera_initializers = {}

        self.logger.info(f"開始異步初始化 {len(active_cameras)} 個鏡頭...")

        for cam_conf in active_cameras:
            name = cam_conf['name']
            cam_id = cam_conf['id']

            self.logger.info(f"啟動 {name} (ID:{cam_id}) 背景初始化...")

            # 創建異步初始化器
            initializer = AsyncCameraInitializer()
            initializer.start_opening(
                camera_id=cam_id,
                width=self.config.camera.CAMERA_WIDTH,
                height=self.config.camera.CAMERA_HEIGHT,
                fps=self.config.camera.TARGET_FPS,
                buffer_size=2,
                warmup_frames=5
            )

            camera_initializers[name] = (initializer, cam_conf)

        self.logger.info("所有鏡頭正在背景初始化（與模型載入並行）...")
        return camera_initializers

    def _wait_for_cameras(self, camera_initializers):
        """
        等待所有攝影機準備好（Phase 2：阻塞等待）

        Args:
            camera_initializers: Dict from _start_async_camera_init()
        """
        self.logger.info("等待鏡頭初始化完成...")

        for name, (initializer, cam_conf) in camera_initializers.items():
            self.logger.info(f"等待 {name} 準備...")

            camera = initializer.wait_for_camera(timeout=10.0)

            if camera:
                self.cameras[name] = camera
                self.logger.info(f"✓ {name} 準備完成 (ThreadedCamera)")
            else:
                self.logger.error(f"✗ {name} 初始化失敗")
                # 如果是主要鏡頭失敗，則視為嚴重錯誤
                if cam_conf['role'] == 'primary':
                    raise CameraOpenError(f"主要鏡頭 {name} 無法開啟")

        self.logger.info(f"成功初始化 {len(self.cameras)} 個鏡頭 (ThreadedCamera)")

    def _initialize_cameras(self):
        """
        初始化攝影機（已棄用 - 保留僅為兼容性）

        注意：現在使用 _start_async_camera_init() 和 _wait_for_cameras()
        來實現並行初始化
        """
        # 這個方法已經被 initialize() 中的並行初始化取代
        # 保留僅為文檔目的
        pass
    
    def _initialize_video_writers(self):
        """初始化視訊寫入器（支援 ThreadedCamera）"""
        # 建立視訊寫入器
        for name, cam in self.cameras.items():
            # ThreadedCamera 使用屬性，cv2.VideoCapture 使用 get()
            if hasattr(cam, 'width'):
                # ThreadedCamera
                width = cam.width
                height = cam.height
            else:
                # 傳統 cv2.VideoCapture
                width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # 根據鏡頭名稱決定檔名
            filename = 'output_cam0.avi' if name == 'customer' else 'output_cam1.avi'

            self.video_writers[name] = create_video_writer(
                filename,
                self.config.camera.TARGET_FPS,
                (width, height)
            )
        
        self.logger.info("視訊錄製初始化完成")

    def _initialize_async_analyzers(self):
        """初始化 Async DeepFace 分析器"""
        self.logger.info("初始化 Async DeepFace 分析器...")

        # 為每個鏡頭建立 async analyzer
        for name in self.cameras.keys():
            analyzer = AsyncDeepFaceAnalyzer(
                name=name,
                detector_backend='opencv',  # 最快的 detector
                frame_skip=5,  # 每 5 幀分析一次
                input_width=320,  # 降採樣以提升速度
                input_height=240,
                analyze_actions=['emotion', 'age', 'gender']
            )

            # 啟動分析器
            analyzer.start()

            self.analyzers[name] = analyzer
            self.logger.info(f"Async analyzer '{name}' 已啟動")

        self.logger.info(f"成功啟動 {len(self.analyzers)} 個 async analyzers")

    def process_frame(self, camera_name, frame):
        """
        處理單一攝影機的畫面（使用 Async DeepFace 分析器）

        Args:
            camera_name: 攝影機名稱 ('customer' 或 'server')
            frame: 影像幀

        Returns:
            處理後的分析結果字典，如果無需分析則返回 None
            特殊返回值 'stop' 表示應該停止分析
        """
        state = self.camera_states[camera_name]
        analyzer = self.analyzers[camera_name]

        # 進行快速分類（Keras，非阻塞）
        class_name, confidence = classify_frame(
            frame,
            self.model,
            self.class_names
        )

        # 檢查是否偵測到人（Class 1）
        if class_name == 'Class 1':
            # 檢查信心度
            if confidence < 1.0:
                if state.low_confidence_start is None:
                    state.low_confidence_start = time.time()
                elif (time.time() - state.low_confidence_start) > 3:
                    self.logger.warning(
                        f"{camera_name}: 信心度低於 100% 超過 3 秒，停止分析"
                    )
                    return 'stop'
            else:
                state.low_confidence_start = None

            # 標記偵測到人
            if not state.person_detected:
                state.person_detected = True
                state.detection_start_time = time.time()
                self.logger.info(f"{camera_name}: 偵測到人物")

            state.session_end_detected = False

        elif class_name == 'Class 2':
            # 偵測到會話結束標記
            if not state.session_end_detected:
                state.session_end_detected = True
                state.session_end_start_time = time.time()
                self.logger.info(f"{camera_name}: 偵測到會話結束標記")

            state.person_detected = False

        else:
            # 未偵測到特定類別，重置狀態
            state.person_detected = False
            state.session_end_detected = False

        # 如果偵測到人且超過延遲時間，提交到 async analyzer
        if state.person_detected and state.detection_start_time:
            elapsed = time.time() - state.detection_start_time

            if elapsed > self.config.analysis.PRESENCE_DETECTION_DELAY_SEC:
                # 提交影格到 async analyzer（非阻塞）
                analyzer.submit_frame(frame, class_name, confidence)

        # 從 async analyzer 獲取最新結果（非阻塞）
        result = analyzer.get_result(timeout=0.001)

        if result:
            # 處理結果中的人口統計資訊
            if result.get('age') and result.get('gender'):
                # 判斷是否需要快取人口統計資訊
                include_demographics = state.should_analyze_demographics(time.time())

                if include_demographics:
                    # 快取人口統計資訊（前 8 秒）
                    state.cache_demographics(
                        result.get('age'),
                        result.get('gender'),
                        result.get('gender_confidence')
                    )

            # 如果結果沒有人口統計資訊但我們有快取，則添加快取資訊
            if not result.get('age') and state.cached_age:
                result['age'] = state.cached_age
                result['gender'] = state.cached_gender
                result['gender_confidence'] = state.cached_gender_confidence

            return result

        return None
    
    def should_exit(self):
        """判斷是否應該退出主循環"""
        # 檢查兩個攝影機的會話結束狀態
        for name, state in self.camera_states.items():
            if state.session_end_detected and state.session_end_start_time:
                if (time.time() - state.session_end_start_time) > 3:
                    self.logger.info(f"{name}: Class 2 持續超過 3 秒，結束分析")
                    return True
        
        return False
    
    def run(self):
        """執行主循環"""
        if not self.initialize():
            self.logger.error("初始化失敗，無法啟動系統") if self.logger else print("初始化失敗")
            return False
        
        self.logger.info("開始主循環...")
        
        try:
            while True:
                frames = {}
                
                # 動態讀取所有已開啟的鏡頭
                for name, cam in self.cameras.items():
                    ret, frame = cam.read()
                    if ret:
                        frames[name] = frame
                    else:
                        self.logger.warning(f"無法讀取鏡頭 {name} 的畫面")
                
                # 如果沒有任何畫面，則退出
                if not frames:
                    self.logger.error("所有鏡頭皆無法讀取畫面")
                    break
                
                # 調整大小和翻轉
                processed_imgs = {}
                for name, frame in frames.items():
                    processed_imgs[name] = resize_and_flip_frame(frame)

                # 每 3 幀進行一次 Keras 分類分析（降低 CPU 負載）
                # AsyncDeepFaceAnalyzer 會自動處理 frame skipping (每 5 幀)
                if self.frame_count % 3 == 0:
                    for name, frame in frames.items():
                        result = self.process_frame(name, frame)
                        if result == 'stop':
                            # 如果任一鏡頭要求停止，則整個系統停止 (可根據需求調整)
                            self.exit_by_user = True # 標記為正常退出
                            break
                        elif result:
                            self.previous_results[name] = result

                    if self.exit_by_user:
                        break
                
                # 繪製結果與寫入視訊
                for name, img in processed_imgs.items():
                    # 繪製結果
                    if self.previous_results.get(name):
                        img = draw_analysis_results(
                            img,
                            self.previous_results[name],
                            show_demographics=True
                        )
                    
                    # 寫入視訊
                    if self.video_writers.get(name):
                        # 注意：寫入的是原始 frame 還是處理過的 img？
                        # 原程式碼是寫入 frame_customer (原始)，但這裡是 processed_imgs (resize & flip)
                        # 為了保持一致性，我們應該寫入原始 frame，但這裡為了簡化邏輯，
                        # 假設 video writer 的尺寸是基於原始 frame 的。
                        # 原程式碼：self.video_writers['customer'].write(frame_customer)
                        # 這裡 frames[name] 是原始 frame
                        self.video_writers[name].write(frames[name])
                    
                    # 顯示畫面
                    # 使用鏡頭名稱作為視窗標題
                    cv2.imshow(f'Camera: {name}', img)
                
                # 檢查使用者輸入
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    self.logger.info("使用者按下 'q'，結束程式")
                    self.exit_by_user = True
                    break
                
                # 檢查是否應該退出
                if self.should_exit():
                    break
                
                self.frame_count += 1
            
            self.logger.info("主循環結束")
            return True
            
        except KeyboardInterrupt:
            self.logger.info("使用者中斷程式")
            self.exit_by_user = True
            return True
        except Exception as e:
            self.logger.error(f"執行時發生錯誤：{e}", exc_info=True)
            return False
    
    def cleanup(self):
        """清理資源"""
        if self.logger:
            self.logger.info("清理資源...")

        # 停止所有 async analyzers
        if self.analyzers:
            self.logger.info("停止 async analyzers...")
            for name, analyzer in self.analyzers.items():
                analyzer.stop(timeout=5.0)
                self.logger.info(f"Async analyzer '{name}' 已停止")

        # 停止所有 ThreadedCamera
        if self.cameras:
            self.logger.info("停止 ThreadedCamera...")
            for name, camera in self.cameras.items():
                camera.stop()  # ThreadedCamera.stop()
                self.logger.info(f"ThreadedCamera '{name}' 已停止")

        # 釋放視訊寫入器
        if self.video_writers:
            release_video_resources(*self.video_writers.values())

        # 關閉所有視窗
        cv2.destroyAllWindows()

        if self.logger:
            self.logger.info("資源清理完成")
    
    def post_process(self):
        """後處理：轉換視訊和生成圖表"""
        self.logger.info("開始後處理...")
        
        # 轉換視訊格式
        self.logger.info("轉換視訊格式...")
        convert_avi_to_mp4('output_cam0.avi', 'output_cam0.mp4')
        convert_avi_to_mp4('output_cam1.avi', 'output_cam1.mp4')
        
        # 生成圖表
        self.logger.info("生成分析圖表...")
        
        # 處理每個鏡頭的圖表
        for name, state in self.camera_states.items():
            if state.emotions:
                camera_display_name = 'Customer' if name == 'customer' else 'Server'
                generate_all_charts(
                    state.emotions,
                    state.ages,
                    state.genders,
                    camera_name=camera_display_name,
                    output_dir=str(Path.cwd())
                )
                
                # 計算分數並顯示
                score = calculate_satisfaction_score(state.emotions)
                self.logger.info(f"Here is the Emotion Grade {score} of {camera_display_name}")
                print(f"Here is the Emotion Grade {score} of {camera_display_name}")

        # 生成合併圖表 (僅在雙鏡頭模式且都有數據時)
        customer_state = self.camera_states.get('customer')
        server_state = self.camera_states.get('server')
        
        if (customer_state and server_state and 
            customer_state.emotions and server_state.emotions):
            generate_combined_wave_chart(
                customer_state.emotions,
                server_state.emotions,
                str(Path.cwd() / 'Customer_Emotion_Wave & Server_Emotion_Wave.jpg'),
                label1='Customer_Emotion_Wave',
                label2='Server_Emotion_Wave',
                title='Combined Emotion Analysis'
            )
        
        # [Phase 3] Export Analysis Result to JSON
        # 計算分數 (若無數據則為 0)
        customer_score = calculate_satisfaction_score(customer_state.emotions) if customer_state and customer_state.emotions else 0
        server_score = calculate_satisfaction_score(server_state.emotions) if server_state and server_state.emotions else 0
        
        self.export_json_result(customer_score, server_score)

        self.logger.info("後處理完成")

    def export_json_result(self, customer_score, server_score):
        """匯出分析結果為 JSON"""
        try:
            self.logger.info("匯出 JSON 結果...")
            
            # Ensure data directory exists
            data_dir = self.config.paths.WEB_STATIC_DIR / 'data'
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Construct data
            # Note: This structure matches report_main.py's data_store
            data = {
                "title": "ADAM",
                "name": "Service_Session_" + datetime.datetime.now().strftime("%Y%m%d_%H%M"),
                "time": datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
                "person_name": "Guest", # Could be detected from face recognition if implemented
                "organization": "Service Industry",
                "total_score": round((customer_score + server_score) / 2, 1),
                "audio_score": 0.0, # Placeholder
                "text_score": 0.0,  # Placeholder
                "facial_score": round((customer_score + server_score) / 2, 1),
                "ai_text1": "分析完成。顧客與服務員情緒評分已生成。",
                "ai_text2": f"顧客情緒評分: {customer_score}",
                "ai_text3": f"服務員情緒評分: {server_score}",
                "charts": [
                    "Customer_Emotion_Wave.jpg",
                    "Customer_Emotion_Bar1.jpg"
                ]
            }
            
            # 根據模式添加額外資訊
            if self.config.camera.MODE == 'DUAL':
                data["ai_text3"] = f"服務員情緒評分: {server_score}"
                data["charts"].extend([
                    "Customer_Emotion_Wave & Server_Emotion_Wave.jpg",
                    "Server_Emotion_Wave.jpg",
                    "Server_Emotion_Bar.jpg"
                ])
            else:
                # 單鏡頭模式
                data["ai_text3"] = "（單鏡頭模式：無服務員數據）"
                # 總分僅基於顧客
                data["total_score"] = customer_score
                data["facial_score"] = customer_score
            
            # Write to file
            json_path = data_dir / 'analysis_result.json'
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                
            self.logger.info(f"JSON 結果已儲存至: {json_path}")
            
        except Exception as e:
            self.logger.error(f"匯出 JSON 失敗: {e}")


def main():
    """主函式"""
    system = EmotionAnalysisSystem()
    
    try:
        # 執行系統
        success = system.run()
        
        # 清理資源
        system.cleanup()
        
        # 後處理
        if success and not system.exit_by_user:
            system.post_process()
        
        # 返回適當的退出碼
        if system.exit_by_user:
            sys.exit('q')
        else:
            sys.exit(0 if success else 1)
            
    except Exception as e:
        if system.logger:
            system.logger.error(f"程式異常終止：{e}", exc_info=True)
        else:
            print(f"程式異常終止：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
