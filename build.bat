@echo off
echo 清理旧的构建文件...
rmdir /s /q build dist
del /f /q *.spec
del /f /q icon.ico

echo 清除图标缓存...
taskkill /f /im explorer.exe
del /f /q %localappdata%\IconCache.db
del /f /q %localappdata%\Microsoft\Windows\Explorer\iconcache*
start explorer.exe

echo 创建高质量图标文件...
python -c "from PIL import Image; img = Image.open('icon.png'); img.save('icon.ico', format='ICO', sizes=[(16,16), (24,24), (32,32), (48,48), (64,64), (128,128), (256,256)])"

echo 开始打包...
pyinstaller --noconfirm --onefile --windowed --icon="icon.ico" --add-data "icon.png;." --hidden-import tkinter --hidden-import tkinter.ttk --name "自动剪辑气口工具" silence_remover.py

echo 打包完成！
pause 