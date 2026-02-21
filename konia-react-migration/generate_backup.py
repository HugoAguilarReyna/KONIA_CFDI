import os
import zipfile
from datetime import datetime

# Configuración
TIMESTAMP = "20260220_1928"
BACKUP_NAME = f"konia_backup_v2_{TIMESTAMP}.zip"
DEST_PATH = os.path.join("..", BACKUP_NAME)
EXCLUDE_DIRS = {"node_modules", "__pycache__", ".git", "dist", ".vite", ".venv"}
EXCLUDE_EXTS = {".pyc", ".DS_Store", "Thumbs.db"}

def should_exclude(path):
    parts = path.split(os.sep)
    # Check for excluded directories
    for d in EXCLUDE_DIRS:
        if d in parts:
            return True
    # Check for excluded extensions or filenames
    filename = os.path.basename(path)
    if filename in EXCLUDE_EXTS:
        return True
    for ext in EXCLUDE_EXTS:
        if ext.startswith(".") and filename.endswith(ext):
            return True
    return False

print(f"🚀 Iniciando generación de backup: {BACKUP_NAME}")

with zipfile.ZipFile(DEST_PATH, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk("."):
        for file in files:
            file_path = os.path.join(root, file)
            # Remove leading './' or '.'
            rel_path = os.path.relpath(file_path, ".")
            
            if not should_exclude(rel_path):
                zipf.write(file_path, rel_path)

size_bytes = os.path.getsize(DEST_PATH)
size_mb = size_bytes / (1024 * 1024)
abs_path = os.path.abspath(DEST_PATH)

print(f"✅ Backup generado: {BACKUP_NAME}")
print(f"📦 Tamaño: {size_mb:.2f} MB")
print(f"📁 Ubicación: {abs_path}")
print("\n📋 Archivos más importantes incluidos:")
# List some important files if they exist in the zip
important_files = [
    "BACKUP_INFO.txt",
    "frontend/src/features/dashboard/MatrizResumen.jsx",
    "frontend/src/components/ui/KPICard.jsx",
    "frontend/src/components/layout/Navbar.jsx",
    "frontend/src/components/layout/Sidebar.jsx",
    "backend/app/api/dashboard.py",
    "backend/app/services/fiscal_wrapper.py",
    "docker-compose.yml",
    "frontend/package.json",
    "backend/requirements.txt"
]
for f in important_files:
    if os.path.exists(f):
        print(f" - {f}")
