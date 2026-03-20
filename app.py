import webview
import os
import json
import sys
from datetime import datetime

def get_base_path():
    """Exe olarak çalışırken _MEIPASS, normal çalışırken script dizini"""
    if getattr(sys, 'frozen', False):
        # PyInstaller exe: geçici çıkarma klasörü
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

def get_data_path():
    """Token gibi yazılabilir dosyalar için exe'nin yanındaki klasör"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

TOKEN_FILE = os.path.join(get_data_path(), '.usbhub_token.json')
HTML_FILE = os.path.join(get_base_path(), 'index.html')
FILES_DIR = os.path.join(get_data_path(), 'files')

# Dosya türlerini belirle
def get_file_type(filename):
    ext = os.path.splitext(filename)[1].lower().lstrip('.')
    if not ext:
        return 'txt'  # uzantısız dosyalar için
    type_map = {
        'html': 'html', 'css': 'css', 'js': 'js', 'json': 'json', 'ts': 'ts', 'py': 'py',
        'md': 'md', 'xml': 'xml', 'sql': 'sql', 'sh': 'sh', 'csv': 'csv', 'txt': 'txt',
        'jpg': 'image', 'jpeg': 'image', 'png': 'image', 'gif': 'image', 'bmp': 'image',
        'mp3': 'audio', 'wav': 'audio', 'flac': 'audio', 'ogg': 'audio',
        'mp4': 'video', 'avi': 'video', 'mkv': 'video', 'mov': 'video',
        'pdf': 'pdf', 'doc': 'doc', 'docx': 'doc', 'xls': 'doc', 'xlsx': 'doc', 'ppt': 'doc', 'pptx': 'doc'
    }
    return type_map.get(ext, 'txt')

def get_file_size(path):
    try:
        size = os.path.getsize(path)
        if size < 1024:
            return f"{size} B"
        elif size < 1024*1024:
            return f"{size/1024:.1f} KB"
        else:
            return f"{size/(1024*1024):.1f} MB"
    except:
        return "—"

def get_file_date(path):
    try:
        mtime = os.path.getmtime(path)
        dt = datetime.fromtimestamp(mtime)
        return dt.strftime('%d %b %Y')
    except:
        return "—"

class Api:
    def save_token(self, token_data):
        """Google Drive token'ı USB'deki dosyaya kaydet"""
        try:
            with open(TOKEN_FILE, 'w') as f:
                json.dump(token_data, f)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def load_token(self):
        """Kaydedilmiş token'ı oku"""
        try:
            if os.path.exists(TOKEN_FILE):
                with open(TOKEN_FILE, 'r') as f:
                    return json.load(f)
            return None
        except:
            return None

    def clear_token(self):
        """Token'ı sil (çıkış yap)"""
        try:
            if os.path.exists(TOKEN_FILE):\
                os.remove(TOKEN_FILE)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def list_files(self, path=""):
        """files klasöründen dosya listesi al"""
        try:
            full_path = os.path.join(FILES_DIR, path)
            if not os.path.exists(full_path):
                os.makedirs(full_path, exist_ok=True)
            
            files = []
            for item in os.listdir(full_path):
                item_path = os.path.join(full_path, item)
                is_dir = os.path.isdir(item_path)
                file_info = {
                    'name': item,
                    'type': 'folder' if is_dir else get_file_type(item),
                    'size': '0 öğe' if is_dir else get_file_size(item_path),
                    'date': get_file_date(item_path),
                    'source': 'local',
                    'path': os.path.join(path, item).replace('\\', '/')
                }
                if is_dir:
                    try:
                        sub_items = os.listdir(item_path)
                        file_info['size'] = f"{len(sub_items)} öğe"
                        file_info['children'] = []  # children'ı sonra doldur
                    except:
                        file_info['size'] = "0 öğe"
                files.append(file_info)
            
            # Klasörleri önce sırala
            files.sort(key=lambda x: (x['type'] != 'folder', x['name'].lower()))
            return files
        except Exception as e:
            return {'error': str(e)}

    def read_file(self, path):
        """Dosya içeriği oku"""
        try:
            full_path = os.path.join(FILES_DIR, path)
            if not os.path.exists(full_path) or os.path.isdir(full_path):
                return {'error': 'Dosya bulunamadı'}
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {'content': content}
        except UnicodeDecodeError:
            return {'error': 'Dosya metin değil, düzenlenemez'}
        except Exception as e:
            return {'error': str(e)}

    def write_file(self, path, content):
        """Dosya yaz"""
        try:
            full_path = os.path.join(FILES_DIR, path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def create_folder(self, path):
        """Klasör oluştur"""
        try:
            full_path = os.path.join(FILES_DIR, path)
            os.makedirs(full_path, exist_ok=True)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def delete_file(self, path):
        """Dosya veya klasör sil"""
        try:
            full_path = os.path.join(FILES_DIR, path)
            if os.path.isdir(full_path):
                os.rmdir(full_path)  # boş klasörler için
            else:
                os.remove(full_path)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def rename_file(self, old_path, new_path):
        """Dosya veya klasör yeniden adlandır"""
        try:
            old_full = os.path.join(FILES_DIR, old_path)
            new_full = os.path.join(FILES_DIR, new_path)
            os.rename(old_full, new_full)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

if __name__ == '__main__':
    api = Api()
    window = webview.create_window(
        'USB Hub',
        HTML_FILE,
        js_api=api,
        width=1100,
        height=700,
        min_size=(800, 500),
        resizable=True,
    )
    webview.start(debug=False)
