"""
打包脚本 - 极致精简版
只打包必需的模块，删除所有不需要的文件
"""

import subprocess
import sys
import os
import shutil
import glob


def get_pyside6_path():
    """获取 PySide6 安装路径"""
    try:
        import PySide6
        return os.path.dirname(PySide6.__file__)
    except ImportError:
        return None


def build():
    """打包应用"""

    # 所有要排除的模块（更激进）
    excludes = [
        # PySide6 不需要的模块
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
        'PySide6.QtHttpServer', 'PySide6.QtGraphs', 'PySide6.QtGraphsWidgets',
        'PySide6.QtAsyncio', 'PySide6.QtSpatialAudio', 'PySide6.QtShaderTools',
        'PySide6.QtVirtualKeyboard', 'PySide6.QtSerialBus', 'PySide6.QtUiTools',
        'PySide6.QtQuick3D', 'PySide6.QtQuick3DRuntimeRender',
        # 其他不需要的标准库（保留 requests 需要的模块）
        'unittest', 'test', 'pydoc', 'doctest', 'lib2to3',
        'tkinter', 'sqlite3', 'multiprocessing',
        'ftplib', 'imaplib', 'mailbox',
        'nntplib', 'poplib', 'smtpd', 'smtplib', 'telnetlib',
    ]

    exclude_args = []
    for mod in excludes:
        exclude_args.extend(['--exclude-module', mod])

    # PyInstaller 命令
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--windowed',
        '--clean',
        '--noconfirm',
        '--name', 'AnyGold',
        '--strip',  # 去除调试符号
        *exclude_args,
        'run.py'
    ]

    # 如果有图标
    if os.path.exists('assets/icon.ico'):
        cmd.extend(['--icon', 'assets/icon.ico'])

    print("=" * 50)
    print("开始打包（精简版）...")
    print("=" * 50)

    result = subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)) or '.')

    if result.returncode != 0:
        print("\n✗ 打包失败!")
        return 1

    exe_path = os.path.join('dist', 'AnyGold.exe')

    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print("\n" + "=" * 50)
        print("✓ 打包成功!")
        print(f"输出文件: {exe_path}")
        print(f"文件大小: {size_mb:.1f} MB")
        print("=" * 50)

    return 0


def build_with_spec():
    """使用 spec 文件打包（更精细控制）"""

    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

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
'''

    # 写入 spec 文件
    spec_path = 'AnyGold_slim.spec'
    with open(spec_path, 'w', encoding='utf-8') as f:
        f.write(spec_content)

    print("=" * 50)
    print("使用精简 spec 文件打包...")
    print("=" * 50)

    # 使用 spec 文件打包
    cmd = [sys.executable, '-m', 'PyInstaller', '--clean', '--noconfirm', spec_path]
    result = subprocess.run(cmd)

    if result.returncode != 0:
        print("\n✗ 打包失败!")
        return 1

    exe_path = os.path.join('dist', 'AnyGold.exe')

    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print("\n" + "=" * 50)
        print("✓ 打包成功!")
        print(f"输出文件: {exe_path}")
        print(f"文件大小: {size_mb:.1f} MB")
        print("=" * 50)

    return 0


if __name__ == '__main__':
    # 使用 spec 文件方式打包（更精细控制）
    sys.exit(build_with_spec())

