@echo off
cd /d "c:\Users\21827\Desktop\新建文件夹"
call venv\Scripts\Activate.ps1
echo. | python -m streamlit run app.py -server.port 8501 -server.address 0.0.0.0