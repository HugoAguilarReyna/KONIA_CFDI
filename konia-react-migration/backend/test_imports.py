import sys
import os

# Add the project root to sys.path to mimic running from backend/
sys.path.append(os.getcwd())

print(f"Testing imports from {os.getcwd()}")

try:
    from app.main import app
    print("✅ app.main imported successfully")
except ImportError as e:
    print(f"❌ Error importing app.main: {e}")
    sys.exit(1)

try:
    from app.services.trazabilidad_wrapper import TrazabilidadService
    print("✅ TrazabilidadService imported successfully")
    
    # Test the internal import of legacy module
    # We need to instantiate it or check the module cache to see if trazabilidad_module was loaded
    if 'trazabilidad_module' in sys.modules:
        print("✅ trazabilidad_module loaded via wrapper")
    else:
        print("⚠️ trazabilidad_module NOT loaded (lazy import?)")
        
except ImportError as e:
    print(f"❌ Error importing services: {e}")
    sys.exit(1)

print("Backend structure verification passed.")
