# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 分析主程序
a = Analysis(
    ['app_launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('backend/*.py', 'backend'),
        ('frontend/dist', 'frontend/dist'),
    ],
    hiddenimports=[
        'flask',
        'flask.json',
        'werkzeug',
        'requests',
        'webview',
        'webview.platforms.cocoa',
        'webview.platforms.cef',
        'proxy_tools',
        'bottle',
        'objc',
        'Foundation',
        'AppKit',
        'WebKit',
        'backend.app',
        'backend.game_logic',
        'backend.stage_handlers',
        'backend.task_handlers',
        'backend.memory_generator',
        'backend.tz_routes',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'jupyter',
        'notebook',
        'IPython',
        'pytest',
        'test',
        'tests',
        '_pytest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 使用 onefile + .app bundle 模式
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TZ_War_Robot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # 启用 UPX 压缩以减小文件大小
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 隐藏终端窗口（使用 pywebview 原生窗口）
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

# 创建 macOS .app bundle - 双击直接启动，无终端窗口
app = BUNDLE(
    exe,
    name='TZ_War_Robot.app',
    icon=None,
    bundle_identifier='com.tz.warrobot',
    info_plist={
        'CFBundleName': 'TZ War Robot',
        'CFBundleDisplayName': 'TZ: The Lost War Robot',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'NSHighResolutionCapable': True,
        'LSBackgroundOnly': False,
        'LSUIElement': False,  # 确保显示在 Dock
    },
)
