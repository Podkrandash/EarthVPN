import sys
import subprocess
import os

def fix_dependencies():
    print("Fixing dependencies...")
    
    # Устанавливаем базовые зависимости
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "urllib3==1.26.15", "six==1.16.0", "certifi>=2023.7.22"])
    
    # Устанавливаем python-telegram-bot отдельно
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-telegram-bot==13.10"])
    
    # Проверяем установку
    try:
        import urllib3
        print(f"urllib3 version: {urllib3.__version__}")
        import six
        print(f"six version: {six.__version__}")
        import telegram
        print(f"python-telegram-bot version: {telegram.__version__}")
        print("Dependencies installed successfully!")
    except ImportError as e:
        print(f"Error importing dependencies: {e}")
        return False
    
    return True

if __name__ == "__main__":
    fix_dependencies() 