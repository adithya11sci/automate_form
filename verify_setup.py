
import sys
import importlib

def check_package(package_name):
    try:
        importlib.import_module(package_name)
        print(f"✅ {package_name} is installed.")
        return True
    except ImportError:
        print(f"❌ {package_name} is MISSING.")
        return False

print("🔍 Verifying AutoFill-GForm Pro Setup...")
print(f"Python: {sys.version}")

packages = [
    "fastapi", "uvicorn", "sqlalchemy", "jose", "passlib", 
    "multipart", "pydantic", "playwright", "sentence_transformers", 
    "sklearn", "numpy", "aiofiles", "httpx"
]

missing = []
for pkg in packages:
    if not check_package(pkg):
        missing.append(pkg)

if missing:
    print(f"\n⚠️ The following packages are missing: {', '.join(missing)}")
    print("Please run 'setup.bat' or 'pip install -r requirements.txt'")
else:
    print("\n🎉 All dependencies are installed! You can run 'launch.bat' now.")
