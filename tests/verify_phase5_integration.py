"""
Phase 5 Integration Verification Script

這個腳本驗證 AsyncDeepFaceAnalyzer 是否成功整合到主程式中。
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logging_config import get_logger

logger = get_logger(__name__)


def verify_imports():
    """測試 1: 驗證所有必要的導入"""
    print("\n" + "="*60)
    print("測試 1: 驗證導入")
    print("="*60)

    try:
        from project_refactored import EmotionAnalysisSystem
        print("✓ EmotionAnalysisSystem 導入成功")

        from utils import AsyncDeepFaceAnalyzer
        print("✓ AsyncDeepFaceAnalyzer 導入成功")

        from config import Config
        print("✓ Config 導入成功")

        return True
    except Exception as e:
        print(f"✗ 導入失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_system_initialization():
    """測試 2: 驗證系統初始化（不開啟鏡頭）"""
    print("\n" + "="*60)
    print("測試 2: 驗證系統基本結構")
    print("="*60)

    try:
        from project_refactored import EmotionAnalysisSystem

        # 創建系統實例
        system = EmotionAnalysisSystem()
        print("✓ EmotionAnalysisSystem 實例創建成功")

        # 檢查必要的屬性
        required_attrs = [
            'config', 'logger', 'model', 'class_names',
            'cameras', 'camera_states', 'video_writers',
            'analyzers',  # 新添加的屬性
            'frame_count', 'exit_by_user', 'previous_results'
        ]

        for attr in required_attrs:
            if hasattr(system, attr):
                print(f"✓ 屬性 '{attr}' 存在")
            else:
                print(f"✗ 屬性 '{attr}' 不存在")
                return False

        # 檢查 analyzers 初始化為空字典
        if isinstance(system.analyzers, dict):
            print("✓ analyzers 正確初始化為字典")
        else:
            print(f"✗ analyzers 類型錯誤: {type(system.analyzers)}")
            return False

        return True

    except Exception as e:
        print(f"✗ 系統初始化驗證失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_async_analyzer_integration():
    """測試 3: 驗證 Async Analyzer 整合邏輯"""
    print("\n" + "="*60)
    print("測試 3: 驗證 Async Analyzer 整合邏輯")
    print("="*60)

    try:
        from project_refactored import EmotionAnalysisSystem
        import inspect

        system = EmotionAnalysisSystem()

        # 檢查 _initialize_async_analyzers 方法
        if hasattr(system, '_initialize_async_analyzers'):
            print("✓ _initialize_async_analyzers 方法存在")

            # 檢查方法簽名
            sig = inspect.signature(system._initialize_async_analyzers)
            print(f"  方法簽名: {sig}")
        else:
            print("✗ _initialize_async_analyzers 方法不存在")
            return False

        # 檢查 process_frame 方法是否更新
        if hasattr(system, 'process_frame'):
            source = inspect.getsource(system.process_frame)

            # 檢查關鍵字
            async_keywords = [
                'self.analyzers',
                'analyzer.submit_frame',
                'analyzer.get_result'
            ]

            for keyword in async_keywords:
                if keyword in source:
                    print(f"✓ process_frame 包含 '{keyword}'")
                else:
                    print(f"✗ process_frame 缺少 '{keyword}'")
                    return False
        else:
            print("✗ process_frame 方法不存在")
            return False

        # 檢查 cleanup 方法是否更新
        if hasattr(system, 'cleanup'):
            source = inspect.getsource(system.cleanup)

            if 'analyzer.stop' in source:
                print("✓ cleanup 包含 analyzer.stop 邏輯")
            else:
                print("✗ cleanup 缺少 analyzer.stop 邏輯")
                return False
        else:
            print("✗ cleanup 方法不存在")
            return False

        return True

    except Exception as e:
        print(f"✗ Async Analyzer 整合驗證失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_config_compatibility():
    """測試 4: 驗證配置兼容性"""
    print("\n" + "="*60)
    print("測試 4: 驗證配置兼容性")
    print("="*60)

    try:
        from config import Config

        config = Config()

        # 檢查必要的配置屬性
        required_configs = [
            ('camera', 'MODE'),
            ('camera', 'TARGET_FPS'),
            ('analysis', 'PRESENCE_DETECTION_DELAY_SEC'),
            ('analysis', 'MIN_CONFIDENCE'),
            ('paths', 'MODEL_DIR'),
        ]

        for section, attr in required_configs:
            section_obj = getattr(config, section)
            if hasattr(section_obj, attr):
                value = getattr(section_obj, attr)
                print(f"✓ Config.{section}.{attr} = {value}")
            else:
                print(f"✗ Config.{section}.{attr} 不存在")
                return False

        return True

    except Exception as e:
        print(f"✗ 配置驗證失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_summary(results):
    """打印測試摘要"""
    print("\n" + "="*60)
    print("測試摘要")
    print("="*60)

    test_names = [
        "導入驗證",
        "系統初始化驗證",
        "Async Analyzer 整合驗證",
        "配置兼容性驗證"
    ]

    for i, (name, passed) in enumerate(zip(test_names, results), 1):
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: 測試 {i} - {name}")

    passed_count = sum(results)
    total = len(results)

    print(f"\n總計: {passed_count}/{total} 測試通過")

    if passed_count == total:
        print("\n🎉 所有驗證測試通過！Phase 5.2 整合成功！")
        print("\n下一步:")
        print("1. 使用真實鏡頭測試系統: python project_refactored.py")
        print("2. 觀察日誌以確認 async analyzers 正常運行")
        print("3. 檢查 FPS 提升效果（預期 10-30x）")
        return 0
    else:
        print(f"\n⚠ {total - passed_count} 個測試失敗")
        print("請檢查上述錯誤訊息並修復問題")
        return 1


def main():
    """執行所有驗證測試"""
    print("="*60)
    print("Phase 5.2 整合驗證測試")
    print("="*60)
    print("這個腳本驗證 AsyncDeepFaceAnalyzer 是否成功整合")
    print("不需要連接鏡頭或執行完整系統")

    tests = [
        verify_imports,
        verify_system_initialization,
        verify_async_analyzer_integration,
        verify_config_compatibility,
    ]

    results = []
    for test_func in tests:
        try:
            passed = test_func()
            results.append(passed)
        except Exception as e:
            print(f"\n✗ 測試執行異常: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)

    return print_summary(results)


if __name__ == "__main__":
    sys.exit(main())
