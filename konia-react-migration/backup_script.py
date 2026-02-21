import os
import zipfile
from datetime import datetime

def make_backup():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    backup_name = f"konia_backup_v2_{timestamp}.zip"
    
    # Ruta padre
    current_dir = os.path.abspath(".")
    parent_dir = os.path.dirname(current_dir)
    zip_path = os.path.join(parent_dir, backup_name)
    
    exclusions = [
        "/node_modules/", "\\node_modules\\",
        "/__pycache__/", "\\__pycache__\\",
        "/.git/", "\\.git\\",
        "/frontend/dist/", "\\frontend\\dist\\",
        "/frontend/.vite/", "\\frontend\\.vite\\",
        "/backend/.venv/", "\\backend\\.venv\\",
        "/.venv/", "\\.venv\\",
        ".DS_Store", "Thumbs.db"
    ]
    
    def should_exclude(path):
        if path.endswith(".pyc"): return True
        # Check against exclusions
        path_check = f"/{path.replace(os.sep, '/')}/"
        for exc in exclusions:
            if exc.replace('\\', '/') in path_check or path.endswith(exc):
                return True
        return False

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk("."):
            # Exclude directories in-place so os.walk doesn't descend into them
            dirs[:] = [d for d in dirs if not should_exclude(os.path.relpath(os.path.join(root, d), "."))]
            
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), ".")
                if not should_exclude(rel_path):
                    zf.write(os.path.join(root, file), rel_path)
                    
    print(f"--- REPORTE ---")
    print(f"✅ Backup generado: {backup_name}")
    print(f"📦 Tamaño: {os.path.getsize(zip_path) / (1024*1024):.2f} MB")
    print(f"📁 Ubicación: {zip_path}")
    print(f"ZIP_FILE={zip_path}")

if __name__ == "__main__":
    make_backup()
