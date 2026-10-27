@echo off
cd /d %~dp0
set MODEL_DIR=models\vits-melo-tts-zh_en
if exist "%MODEL_DIR%\model.onnx" (
    echo [TTS] 模型已存在，无需下载。
    pause
    exit /b 0
)
echo [TTS] 开始下载 MeloTTS 中英模型（约 160MB 压缩包）...
set GH=https://gh-proxy.com/https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-melo-tts-zh_en.tar.bz2
if not exist models mkdir models
curl -L -o "%TEMP%\melo.tar.bz2" "%GH%" || goto :err
echo [TTS] 解压中...
tar -xzf "%TEMP%\melo.tar.bz2" -C models || goto :err
del "%TEMP%\melo.tar.bz2"
echo [TTS] 模型就绪：%MODEL_DIR%
pause
exit /b 0

:err
echo [TTS] 下载失败，请检查网络。可手动下载：
echo   %GH%
echo 解压到 %MODEL_DIR% 后重跑 start.bat
pause
exit /b 1
