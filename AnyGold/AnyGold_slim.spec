# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 只收集必需的 PySide6 模块
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

# 手动指定需要的二进制文件
pyside6_binaries = []
pyside6_datas = []

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=pyside6_binaries,
    datas=pyside6_datas,
    hiddenimports=['PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'PySide6.QtWebEngine', 'PySide6.QtWebEngineCore', 'PySide6.QtWebEngineWidgets',
        'PySide6.QtNetwork', 'PySide6.QtQml', 'PySide6.QtQuick', 'PySide6.QtQuickWidgets',
        'PySide6.Qt3DCore', 'PySide6.Qt3DRender', 'PySide6.Qt3DInput', 'PySide6.Qt3DLogic',
        'PySide6.Qt3DExtras', 'PySide6.Qt3DAnimation', 'PySide6.QtCharts',
        'PySide6.QtDataVisualization', 'PySide6.QtMultimedia', 'PySide6.QtMultimediaWidgets',
        'PySide6.QtPositioning', 'PySide6.QtLocation', 'PySide6.QtBluetooth', 'PySide6.QtNfc',
        'PySide6.QtWebSockets', 'PySide6.QtWebChannel', 'PySide6.QtSerialPort',
        'PySide6.QtSensors', 'PySide6.QtTest', 'PySide6.QtXml', 'PySide6.QtSvg',
        'PySide6.QtSvgWidgets', 'PySide6.QtPdf', 'PySide6.QtPdfWidgets', 'PySide6.QtOpenGL',
        'PySide6.QtOpenGLWidgets', 'PySide6.QtDBus', 'PySide6.QtDesigner', 'PySide6.QtHelp',
        'PySide6.QtSql', 'PySide6.QtStateMachine', 'PySide6.QtScxml', 'PySide6.QtRemoteObjects',
        'PySide6.QtConcurrent', 'PySide6.QtPrintSupport', 'PySide6.QtTextToSpeech',
        'unittest', 'test', 'tkinter', 'sqlite3', 'multiprocessing',
        'pydoc', 'doctest', 'lib2to3', 'ftplib', 'imaplib', 'mailbox',
        'nntplib', 'poplib', 'smtpd', 'smtplib', 'telnetlib',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 过滤掉不需要的 DLL
def filter_binaries(binaries):
    """过滤不需要的二进制文件"""
    exclude_dlls = [
        'Qt6WebEngine', 'Qt6Qml', 'Qt6Quick', 'Qt6Network', 'Qt6Sql',
        'Qt6Svg', 'Qt6Pdf', 'Qt6Multimedia', 'Qt6OpenGL', 'Qt63D',
        'Qt6Charts', 'Qt6DataVisualization', 'Qt6Bluetooth', 'Qt6Nfc',
        'Qt6Sensors', 'Qt6SerialPort', 'Qt6Test', 'Qt6WebSockets',
        'Qt6WebChannel', 'Qt6Positioning', 'Qt6Location', 'Qt6Designer',
        'Qt6Help', 'Qt6Concurrent', 'Qt6PrintSupport', 'Qt6DBus',
        'Qt6StateMachine', 'Qt6Scxml', 'Qt6RemoteObjects',
        'Qt6TextToSpeech', 'Qt6VirtualKeyboard', 'Qt6SerialBus',
        'Qt6Quick3D', 'Qt6ShaderTools', 'Qt6SpatialAudio',
        'icudt', 'icuin', 'icuuc',  # ICU 国际化库（很大）
        'd3dcompiler', 'opengl32sw',  # OpenGL 相关
        'QtVirtualKeyboard', 'QtQuick',
    ]
    
    filtered = []
    for name, path, typ in binaries:
        exclude = False
        for dll in exclude_dlls:
            if dll.lower() in name.lower():
                exclude = True
                print(f"  排除: {name}")
                break
        if not exclude:
            filtered.append((name, path, typ))
    
    return filtered

a.binaries = filter_binaries(a.binaries)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AnyGold',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',
)
