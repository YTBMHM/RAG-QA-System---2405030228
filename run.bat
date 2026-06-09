@echo off
echo ================================
echo      RAG问答系统启动脚本
echo ================================
echo.
echo 正在启动Ollama服务...
start /B ollama serve
timeout /t 3 /nobreak > nul
echo.
echo 启动Web应用...
python -m streamlit run app.py -server.port 8501 -server.address 0.0.0.0
pause