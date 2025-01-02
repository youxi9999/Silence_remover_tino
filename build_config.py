from PyInstaller.utils.hooks import collect_data_files
import os
import site
import tkinterdnd2

# 获取 tkdnd 库文件路径
tkdnd_path = os.path.join(os.path.dirname(tkinterdnd2.__file__), 'tkdnd')

# 指定需要排除的模块
excludes = [
    'matplotlib', 'numpy', 'pandas', 'scipy', 'PIL._webp',
    'PIL.ImageQt', 'PyQt5', 'PySide2', 'wx', 'IPython',
    'notebook', 'pytest', 'sphinx', 'docutils', 'jedi',
    'setuptools'
]

# 指定需要的隐藏导入
hiddenimports = [
    'tkinter',
    'tkinter.ttk',
    'tkinterdnd2'
]

# 获取 tkdnd 相关文件
tkdnd_files = []
if os.path.exists(tkdnd_path):
    for root, dirs, files in os.walk(tkdnd_path):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, os.path.dirname(tkdnd_path))
            tkdnd_files.append((full_path, os.path.join('tkdnd', rel_path)))

# 创建 spec 文件的配置
a = Analysis(
    ['silence_remover.py'],
    pathex=[],
    binaries=tkdnd_files,  # 添加 tkdnd 文件
    datas=[
        ('icon.png', '.'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='自动剪辑气口工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon='icon.ico'
) 