@echo off
cd /d %~dp0
rem 通用 TTS 服务（文本转语音），端口 9710，绑定 0.0.0.0 供局域网调用
netstat -ano | findstr ":9710 " | findstr "LISTENING" >nul && (echo [TTS] 9710 端口已被占用，服务可能已在运行 & pause & exit /b 0)
if not exist .venv (
    echo [TTS] 首次运行，创建 Python 虚拟环境并安装依赖...
    python -m venv .venv || (echo 未找到 Python 3.10+，请先安装并加入 PATH & pause & exit /b 1)
    .venv\Scripts\pip install -q -i https://pypi.tuna.tsinghua.edu.cn/simple sherpa-onnx==1.13.8 fastapi "uvicorn[standard]" soundfile numpy pydantic || (echo 依赖安装失败 & pause & exit /b 1)
)
echo [TTS] 启动通用 TTS 服务，端口 9710，加载模型约 5-15 秒...
.venv\Scripts\python.exe app.py
pause
