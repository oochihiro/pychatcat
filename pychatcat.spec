# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['run_app.py'],
    pathex=[],
    binaries=[],
    datas=[('config', 'config')],
    hiddenimports=['main', 'config.backend_config', 'integrations.cloud_integration', 'integrations.sqlite_integration', 'core.user_identity', 'core.sqlite_analytics', 'ui.pixel_code_editor', 'ui.pixel_console', 'ui.pixel_ai_assistant', 'ui.debugger_panel', 'core.file_manager', 'core.code_executor', 'core.deepseek_client', 'cat_icon'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='pychatcat',
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
)
