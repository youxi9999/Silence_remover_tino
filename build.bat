@echo off
echo 清理旧的构建文件...
rmdir /s /q build dist
del /f /q *.spec

echo 开始打包...
pyinstaller --clean silence_remover.spec

echo 打包完成！
pause 