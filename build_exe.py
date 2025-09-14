#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IAR Firmware Publish Tool - Build Script
Build executable from Python source code
"""

import os
import sys
import subprocess
import shutil
import re
from pathlib import Path

# Constants
SPEC_NAME_BASE = "Embedded_Firmware_Manager"
RELEASE_DIR = "release"

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        print(f"[OK] PyInstaller installed, version: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("[ERROR] PyInstaller not installed")
        return False

def install_pyinstaller():
    """Install PyInstaller"""
    print("Installing PyInstaller...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                      check=True, capture_output=True, text=True)
        print("[OK] PyInstaller installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] PyInstaller installation failed: {e}")
        return False

def increment_version():
    """Increment tool version number"""
    print("Incrementing tool version...")
    try:
        from tool_version_manager import ToolVersionManager
        
        # Create version manager instance
        version_manager = ToolVersionManager()
        
        # Increment and update version
        success, new_version = version_manager.increment_and_update_advanced()
        
        if success and new_version:
            print(f"[OK] Tool version incremented to: {new_version}")
            return new_version
        else:
            print("[ERROR] Version increment failed")
            return None
    except Exception as e:
        print(f"[ERROR] Version increment failed: {e}")
        return None

def update_version_file(version):
    """Update version in version.py"""
    try:
        version_file_path = "version.py"
        if not os.path.exists(version_file_path):
            print(f"[ERROR] File not found: {version_file_path}")
            return False
        
        with open(version_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        pattern = r'VERSION\s*=\s*["\']([^"\']+)["\'](?:\s*#.*)?'
        replacement = f'VERSION = "{version}"'
        
        if re.search(pattern, content):
            new_content = re.sub(pattern, replacement, content)
            with open(version_file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"[OK] Updated version to: {version}")
            return True
        else:
            print("[ERROR] Version pattern not found in version.py")
            return False
    except Exception as e:
        print(f"[ERROR] Failed to update version: {e}")
        return False

def get_current_version():
    """Get current version from version.py"""
    try:
        with open("version.py", "r", encoding="utf-8") as f:
            content = f.read()
        match = re.search(r'VERSION\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
        else:
            print("[ERROR] Failed to get version: Version pattern not found in version.py")
            return None
    except Exception as e:
        print(f"[ERROR] Failed to get version: {e}")
        return None

def create_spec_file(spec_name, exe_name):
    """Create PyInstaller spec file"""
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('user_config.example.json', '.'),
        ('docs', 'docs'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{exe_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(os.getcwd(), 'icon_efm.ico'),
)
'''
    
    # Skip backup spec file creation
    
    try:
        with open(f"{spec_name}.spec", "w", encoding="utf-8") as f:
            f.write(spec_content)
        print(f"[OK] Spec file created: {spec_name}.spec")
        return True
    except Exception as e:
        print(f"[ERROR] Spec file creation failed: {e}")
        return False

def build_exe_from_spec(spec_name, exe_name):
    """Build exe file from spec file"""
    print(f"Building exe from spec file...")
    
    try:
        # Run PyInstaller with spec file
        cmd = [sys.executable, "-m", "PyInstaller", "--clean", f"{spec_name}.spec"]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print(f"[OK] Exe file built successfully: {exe_name}.exe")
            return True
        else:
            print(f"[ERROR] Exe file build failed")
            print(f"Error output: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] Exe file build failed: {e}")
        return False

def build_exe():
    """Build exe file"""
    print("Starting exe build...")
    
    # Get current version
    current_version = get_current_version()
    if not current_version:
        print("Failed to get current version")
        return False
    
    # Increment version
    new_version = increment_version()
    if not new_version:
        print("Failed to increment version")
        return False
    
    # Update version file
    update_version_file(new_version)
    
    # Create spec file
    spec_name = SPEC_NAME_BASE
    exe_name = f"{SPEC_NAME_BASE}_v{new_version}"
    
    if not create_spec_file(spec_name, exe_name):
        return False
    
    # Build exe
    if not build_exe_from_spec(spec_name, exe_name):
        return False
    
    return new_version

def create_release_package(final_version):
    """Create release package"""
    print("Creating release package...")
    
    # Create release directory
    release_dir = Path(RELEASE_DIR)
    release_dir.mkdir(exist_ok=True)
    
    # Copy exe file
    exe_name = f"{SPEC_NAME_BASE}_v{final_version}"
    exe_path = Path("dist") / f"{exe_name}.exe"
    
    if exe_path.exists():
        shutil.copy2(exe_path, release_dir / f"{exe_name}.exe")
        print(f"[OK] Exe file copied to release directory: {exe_name}")
    else:
        print("[ERROR] Exe file not found")
        return False
    
    # 只拷贝exe文件，不拷贝其他文件
    print("[INFO] Only copying exe file to release directory")
    
    # Create usage guide
    usage_guide = f"""# IAR Firmware Publish Tool v{final_version}

## Usage
1. Run {exe_name}.exe
2. Configure settings in the application
3. Start building

## Configuration
The application will create a user_config.json file automatically when you first run it.
You can modify the settings through the application's settings interface.

## Version
{final_version}
"""
    
    with open(release_dir / "README.txt", "w", encoding="utf-8") as f:
        f.write(usage_guide)
    
    print("[OK] Created usage guide")
    print(f"[OK] Release package created in: {release_dir.absolute()}")
    return True

def main():
    """Main function"""
    print("=" * 50)
    print("IAR Firmware Publish Tool - Build Script")
    print("=" * 50)

    # Check PyInstaller
    if not check_pyinstaller():
        if not install_pyinstaller():
            print("Cannot install PyInstaller, please install manually: pip install pyinstaller")
            return False

    # Build exe
    final_version = build_exe()
    if not final_version:
        print("Build failed")
        return False

    # Create release package
    if not create_release_package(final_version):
        print("Release package creation failed")
        return False

    print("[OK] Build completed!")
    print(f"Release files located in {RELEASE_DIR}/ directory")
    print(f"Executable: {RELEASE_DIR}/{SPEC_NAME_BASE}_v{final_version}.exe")
    print(f"Version: {final_version}")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
