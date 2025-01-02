@echo off
echo 清理旧的构建文件...
rmdir /s /q build dist
del /f /q *.spec

echo 开始打包...
pyinstaller --noconfirm --onefile --windowed --icon=icon.png --add-data "icon.png;." --hidden-import tkinter --hidden-import tkinter.ttk --name "自动剪辑气口工具" silence_remover.py

echo 打包完成！
pause 