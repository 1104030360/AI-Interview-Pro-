import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config

def verify_config():
    print("=== Verifying Configuration ===")
    
    # Check paths
    print(f"Model Dir: {Config.paths.MODEL_DIR}")
    print(f"Keras Model: {Config.paths.KERAS_MODEL_PATH}")
    print(f"Labels: {Config.paths.LABELS_PATH}")
    print(f"Font: {Config.paths.FONT_PATH}")
    
    # Validate
    is_valid, error_msg = Config.validate()
    
    if is_valid:
        print("\n✅ Configuration is VALID.")
        return True
    else:
        print(f"\n❌ Configuration is INVALID:\n{error_msg}")
        return False

if __name__ == "__main__":
    success = verify_config()
    sys.exit(0 if success else 1)
