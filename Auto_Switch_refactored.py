"""
自動觸發系統（重構版）

使用人臉偵測自動啟動情緒分析系統。
當偵測到人臉超過設定時間後，自動執行主程式。

主要改進：
- 使用 Config 管理設定
- 消除硬編碼路徑
- 完整的錯誤處理和日誌
- 模組化設計
"""
import cv2
import sys
import time
import subprocess

from config import Config
from utils import (
    setup_logging,
    get_logger,
    open_camera_with_retry,
    configure_camera,
    resize_and_flip_frame
)
from exceptions import CameraOpenError


class AutoTriggerSystem:
    """人臉偵測自動觸發系統"""
    
    def __init__(self):
        """初始化系統"""
        self.config = Config()
        self.logger = None
        self.camera = None
        self.face_cascade = None
        self.face_detected = False
        self.detection_start_time = None
        self.frame_count = 0
        
    def initialize(self):
        """初始化組件"""
        try:
            # 設定日誌
            setup_logging()
            self.logger = get_logger(__name__)
            self.logger.info("=== 自動觸發系統啟動 ===")
            
            # 載入人臉偵測模型
            cascade_path = "models/cascade/haarcascade_frontalface_default.xml"
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            
            if self.face_cascade.empty():
                raise FileNotFoundError(
                    f"無法載入人臉偵測模型：{cascade_path}"
                )
            
            self.logger.info("人臉偵測模型載入成功")
            
            # 開啟攝影機
            self.logger.info("開啟攝影機...")
            self.camera = open_camera_with_retry(0, max_retries=3)
            configure_camera(self.camera)
            
            # 等待攝影機暖機
            self.logger.info("等待攝影機暖機 (5秒)...")
            time.sleep(5.0)
            
            self.logger.info("系統初始化完成")
            return True
            
        except FileNotFoundError as e:
            if self.logger:
                self.logger.error(f"檔案未找到：{e}")
            else:
                print(f"檔案未找到：{e}")
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
    
    def detect_faces(self, frame):
        """
        偵測畫面中的人臉
        
        Args:
            frame: 輸入影像幀
            
        Returns:
            人臉區域列表 [(x, y, w, h), ...]
        """
        # 轉換為灰階
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 偵測人臉
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        return faces
    
    def draw_faces(self, frame, faces):
        """
        在影像上標記人臉
        
        Args:
            frame: 輸入影像
            faces: 人臉區域列表
            
        Returns:
            標記後的影像
        """
        for (x, y, w, h) in faces:
            # 綠色矩形標記人臉
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        return frame
    
    def launch_main_program(self):
        """
        啟動主程式（project_refactored.py）
        
        Returns:
            主程式的退出碼
        """
        self.logger.info("啟動主程式...")
        
        try:
            # 執行重構後的主程式
            # 使用 sys.executable 確保使用當前虛擬環境的 Python
            result = subprocess.run(
                [sys.executable, 'project_refactored.py'],
                capture_output=True,
                text=True,
                timeout=600  # 10 分鐘超時
            )
            
            # 記錄輸出
            if result.stdout:
                self.logger.info(f"主程式輸出：\n{result.stdout}")
            if result.stderr:
                self.logger.warning(f"主程式錯誤：\n{result.stderr}")
            
            self.logger.info(f"主程式結束，退出碼：{result.returncode}")
            
            return result.returncode
            
        except subprocess.TimeoutExpired:
            self.logger.error("主程式執行超時")
            return -1
        except Exception as e:
            self.logger.error(f"啟動主程式時發生錯誤：{e}", exc_info=True)
            return -1
    
    def run(self):
        """執行主循環"""
        if not self.initialize():
            self.logger.error("初始化失敗，無法啟動系統") if self.logger else print("初始化失敗")
            return False
        
        self.logger.info("開始監控人臉...")
        self.logger.info("按 'q' 鍵退出")
        
        # 觸發延遲（秒）
        trigger_delay = 1.0
        
        try:
            while True:
                # 讀取畫面
                ret, frame = self.camera.read()
                
                if not ret:
                    self.logger.error("無法讀取攝影機畫面")
                    break
                
                # 調整大小
                display_frame = cv2.resize(frame, (540, 320))
                
                # 偵測人臉
                faces = self.detect_faces(display_frame)
                
                # 標記人臉
                if len(faces) > 0:
                    display_frame = self.draw_faces(display_frame, faces)
                    
                    # 首次偵測到人臉
                    if not self.face_detected:
                        self.face_detected = True
                        self.detection_start_time = time.time()
                        self.logger.info(f"偵測到 {len(faces)} 個人臉")
                    
                    # 計算經過時間
                    elapsed = time.time() - self.detection_start_time
                    
                    # 顯示倒數
                    countdown = max(0, trigger_delay - elapsed)
                    text = f"Detected! Starting in {countdown:.1f}s..."
                    cv2.putText(
                        display_frame,
                        text,
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2
                    )
                    
                    # 超過延遲時間，啟動主程式
                    if elapsed > trigger_delay:
                        self.logger.info(
                            f"人臉持續 {elapsed:.1f} 秒，啟動主程式"
                        )
                        
                        # 釋放攝影機給主程式使用
                        self.camera.release()
                        cv2.destroyAllWindows()
                        
                        # 啟動主程式
                        exit_code = self.launch_main_program()
                        
                        # 主程式結束後，重新初始化
                        if exit_code == ord('q'):
                            self.logger.info("主程式返回 'q'，退出系統")
                            return True
                        
                        # 重新初始化攝影機
                        self.logger.info("重新初始化攝影機...")
                        self.camera = open_camera_with_retry(0)
                        configure_camera(self.camera)
                        
                        # 重置狀態
                        self.face_detected = False
                        self.detection_start_time = None
                
                else:
                    # 未偵測到人臉，重置狀態
                    if self.face_detected:
                        self.logger.info("人臉消失，重置偵測")
                    
                    self.face_detected = False
                    self.detection_start_time = None
                    
                    # 顯示等待訊息
                    cv2.putText(
                        display_frame,
                        "Waiting for face...",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255),
                        2
                    )
                
                # 顯示畫面
                cv2.imshow('Auto Trigger System', display_frame)
                
                # 檢查使用者輸入
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    self.logger.info("使用者按下 'q'，退出系統")
                    break
                
                self.frame_count += 1
            
            self.logger.info("監控結束")
            return True
            
        except KeyboardInterrupt:
            self.logger.info("使用者中斷程式")
            return True
        except Exception as e:
            self.logger.error(f"執行時發生錯誤：{e}", exc_info=True)
            return False
    
    def cleanup(self):
        """清理資源"""
        if self.logger:
            self.logger.info("清理資源...")
        
        # 釋放攝影機
        if self.camera is not None:
            self.camera.release()
        
        # 關閉所有視窗
        cv2.destroyAllWindows()
        
        if self.logger:
            self.logger.info("資源清理完成")


def main():
    """主函式"""
    system = AutoTriggerSystem()
    
    try:
        # 執行系統
        success = system.run()
        
        # 清理資源
        system.cleanup()
        
        # 返回退出碼
        sys.exit(0 if success else 1)
        
    except Exception as e:
        if system.logger:
            system.logger.error(f"程式異常終止：{e}", exc_info=True)
        else:
            print(f"程式異常終止：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
