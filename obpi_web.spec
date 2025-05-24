# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src', 'src'),
        ('css', 'css'),
        ('js', 'js'),
        ('img', 'img'),
        ('favicon.ico', '.'),
        ('icon.png', '.'),
        ('icon.svg', '.'),
        ('site.webmanifest', '.'),
        ('robots.txt', '.'),
        ('404.html', '.'),
    ],
    hiddenimports=[
        'pyusb',
        'usb.backend.libusb1',
        'cv2',
        'psutil',
        'backend.ai_core',
        'backend.backend_api',
        'backend.compiler_runner',
        'backend.db_manager',
        'backend.pepx_data_store',
        'backend.peripheral_scanner',
        'backend.vfs_manager',
        'backend.webgl_hex_compiler_concept',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# For web deployment, we create a directory structure that can be served by a web server
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='OBPI-Web',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Console is True for web server mode
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='OBPI-Web',
)

# Note: This spec file creates a directory structure that can be deployed to a web server.
# The actual web server functionality needs to be implemented in the application code.
