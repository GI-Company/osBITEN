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

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='OBPI-macOS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.png',  # Using the existing PNG icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='OBPI-macOS',
)

app = BUNDLE(
    coll,
    name='OBPI.app',
    icon='icon.png',
    bundle_identifier='com.example.obpi',
    info_plist={
        'NSHighResolutionCapable': 'True',
        'NSCameraUsageDescription': 'OBPI needs access to your camera for the peripheral scanner feature.',
        'NSMicrophoneUsageDescription': 'OBPI needs access to your microphone for the peripheral scanner feature.',
    },
)
