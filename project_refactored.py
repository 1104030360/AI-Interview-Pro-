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
from pathlib import Path

from config import Config
from models import CameraState
from utils import (
    setup_logging,
    get_logger,
    load_keras_model,
    open_camera_with_retry,
    configure_camera,
    release_camera,
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
    calculate_satisfaction_score
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
        self.frame_count = 0
        self.exit_by_user = False
        self.previous_results = {
            'customer': None,
            'server': None
        }
        
    def initialize(self):
        """初始化所有組件"""
        try:
            # 設定日誌
            setup_logging()
            self.logger = get_logger(__name__)
            self.logger.info("=== 情緒分析系統啟動 ===")
            
            # 載入模型
            self.logger.info("載入 Keras 模型...")
            self.model, self.class_names = load_keras_model()
            self.logger.info(f"模型載入成功，類別數：{len(self.class_names)}")
            
            # 初始化攝影機
            self._initialize_cameras()
            
            # 初始化狀態
            self.camera_states = {
                'customer': CameraState(),
                'server': CameraState()
            }
            
            # 初始化視訊錄製
            self._initialize_video_writers()
            
            self.logger.info("系統初始化完成")
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
    
    def _initialize_cameras(self):
        """初始化雙攝影機"""
        self.logger.info("開啟攝影機...")
        
        # 開啟攝影機 0（顧客）
        self.cameras['customer'] = open_camera_with_retry(0, max_retries=3)
        configure_camera(self.cameras['customer'])
        
        # 開啟攝影機 1（服務員）
        self.cameras['server'] = open_camera_with_retry(1, max_retries=3)
        configure_camera(self.cameras['server'])
        
        self.logger.info("攝影機開啟成功")
    
    def _initialize_video_writers(self):
        """初始化視訊寫入器"""
        # 獲取攝影機解析度
        width = int(self.cameras['customer'].get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cameras['customer'].get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = self.config.camera.fps
        
        # 建立視訊寫入器
        self.video_writers['customer'] = create_video_writer(
            'output_cam0.avi',
            fps,
            (width, height)
        )
        
        self.video_writers['server'] = create_video_writer(
            'output_cam1.avi',
            fps,
            (width, height)
        )
        
        self.logger.info("視訊錄製初始化完成")
    
    def process_frame(self, camera_name, frame):
        """
        處理單一攝影機的畫面
        
        Args:
            camera_name: 攝影機名稱 ('customer' 或 'server')
            frame: 影像幀
            
        Returns:
            處理後的分析結果字典，如果無需分析則返回 None
        """
        state = self.camera_states[camera_name]
        
        # 進行分類
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
        
        # 如果偵測到人且超過延遲時間，進行分析
        if state.person_detected and state.detection_start_time:
            elapsed = time.time() - state.detection_start_time
            
            if elapsed > self.config.analysis.person_detection_delay:
                # 判斷是否需要人口統計分析
                include_demographics = state.should_analyze_demographics(time.time())
                
                # 進行分析
                if include_demographics:
                    result = analyze_with_demographics(frame, class_name, confidence)
                    if result:
                        # 快取人口統計資訊
                        state.cache_demographics(
                            result.get('age'),
                            result.get('gender'),
                            result.get('gender_confidence')
                        )
                        return result
                else:
                    result = analyze_emotions_only(frame, class_name, confidence)
                    if result:
                        # 加入快取的人口統計資訊
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
                # 讀取兩個攝影機的畫面
                ret_customer, frame_customer = self.cameras['customer'].read()
                ret_server, frame_server = self.cameras['server'].read()
                
                if not ret_customer or not ret_server:
                    self.logger.error("無法讀取攝影機畫面")
                    break
                
                # 調整大小和翻轉
                img_customer = resize_and_flip_frame(frame_customer)
                img_server = resize_and_flip_frame(frame_server)
                
                # 每幀都進行分析
                if self.frame_count % 1 == 0:
                    # 處理顧客攝影機
                    result_customer = self.process_frame('customer', frame_customer)
                    if result_customer == 'stop':
                        break
                    elif result_customer:
                        self.previous_results['customer'] = result_customer
                    
                    # 處理服務員攝影機
                    result_server = self.process_frame('server', frame_server)
                    if result_server == 'stop':
                        break
                    elif result_server:
                        self.previous_results['server'] = result_server
                
                # 繪製結果（使用最新的結果或快取）
                if self.previous_results['customer']:
                    img_customer = draw_analysis_results(
                        img_customer,
                        self.previous_results['customer'],
                        show_demographics=True
                    )
                
                if self.previous_results['server']:
                    img_server = draw_analysis_results(
                        img_server,
                        self.previous_results['server'],
                        show_demographics=True
                    )
                
                # 寫入視訊
                if self.video_writers['customer']:
                    self.video_writers['customer'].write(frame_customer)
                if self.video_writers['server']:
                    self.video_writers['server'].write(frame_server)
                
                # 顯示畫面
                cv2.imshow('camera0', img_customer)
                cv2.imshow('camera1', img_server)
                
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
        
        # 釋放攝影機
        if self.cameras:
            release_camera(*self.cameras.values())
        
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
        
        customer_state = self.camera_states['customer']
        server_state = self.camera_states['server']
        
        # 計算滿意度分數
        if customer_state.emotions:
            customer_score = calculate_satisfaction_score(customer_state.emotions)
            self.logger.info(f"Here is the Emotion Grade {customer_score} of Customer")
            print(f"Here is the Emotion Grade {customer_score} of Customer")
        
        if server_state.emotions:
            server_score = calculate_satisfaction_score(server_state.emotions)
            self.logger.info(f"Here is the Emotion Grade {server_score} of Server")
            print(f"Here is the Emotion Grade {server_score} of Server")
        
        # 生成顧客圖表
        if customer_state.emotions:
            generate_all_charts(
                customer_state.emotions,
                customer_state.ages,
                customer_state.genders,
                camera_name='Customer',
                output_dir=str(Path.cwd())
            )
        
        # 生成服務員圖表
        if server_state.emotions:
            generate_all_charts(
                server_state.emotions,
                server_state.ages,
                server_state.genders,
                camera_name='Server',
                output_dir=str(Path.cwd())
            )
        
        # 生成合併圖表
        if customer_state.emotions and server_state.emotions:
            generate_combined_wave_chart(
                customer_state.emotions,
                server_state.emotions,
                str(Path.cwd() / 'Customer_Emotion_Wave & Server_Emotion_Wave.jpg'),
                label1='Customer_Emotion_Wave',
                label2='Server_Emotion_Wave',
                title='Combined Emotion Analysis'
            )
        
        self.logger.info("後處理完成")


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
