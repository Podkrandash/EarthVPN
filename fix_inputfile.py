"""
Скрипт для исправления файла inputfile.py в библиотеке python-telegram-bot.
Запустите этот скрипт с правами администратора или от имени пользователя с правами на запись в директорию с библиотекой.
"""

import os
import sys

def fix_inputfile():
    # Определяем путь к файлу inputfile.py в библиотеке python-telegram-bot
    site_packages = [p for p in sys.path if 'site-packages' in p or 'dist-packages' in p]
    
    if not site_packages:
        print("Не удалось найти директорию с установленными пакетами.")
        return False
    
    for site_package in site_packages:
        inputfile_path = os.path.join(site_package, 'telegram', 'files', 'inputfile.py')
        if os.path.exists(inputfile_path):
            # Читаем содержимое файла
            with open(inputfile_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Заменяем импорт imghdr на встроенную функцию
            if 'import imghdr' in content:
                new_content = content.replace('import imghdr', '')
                
                # Добавляем функцию для определения типа изображения
                img_func = '''
def _get_image_type(data):
    """Простая функция для определения типа изображения на основе сигнатур файлов"""
    if data.startswith(b'\\xff\\xd8'):
        return 'jpeg'
    elif data.startswith(b'\\x89PNG\\r\\n\\x1a\\n'):
        return 'png'
    elif data.startswith(b'GIF87a') or data.startswith(b'GIF89a'):
        return 'gif'
    elif data.startswith(b'RIFF') and data[8:12] == b'WEBP':
        return 'webp'
    elif data.startswith(b'BM'):
        return 'bmp'
    return None
'''
                
                # Вставляем функцию после импортов
                import_end = content.find('\n\n', content.find('import'))
                if import_end == -1:
                    import_end = content.find('\n', content.find('import'))
                
                if import_end != -1:
                    new_content = content[:import_end] + img_func + content[import_end:]
                else:
                    new_content = img_func + content
                
                # Заменяем вызовы imghdr.what на _get_image_type
                new_content = new_content.replace('imghdr.what(', '_get_image_type(')
                
                # Сохраняем обновленный файл
                with open(inputfile_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"Файл {inputfile_path} успешно исправлен.")
                return True
            else:
                print(f"В файле {inputfile_path} не найден импорт imghdr, возможно, он уже исправлен.")
    
    print("Файл telegram/files/inputfile.py не найден.")
    return False

if __name__ == "__main__":
    if fix_inputfile():
        print("Исправление успешно выполнено.")
    else:
        print("Не удалось выполнить исправление.") 