@echo off
echo =====================================================================
echo    SENTINEL-RISK: S^&P Global ^& CRISIL Campus Hackathon Platform
echo    Unified AI/NLP Risk Engine ^& Strategic Wholesale Stress Tester
echo =====================================================================
echo.
echo [1/3] Verifying Python Environment...
python --version
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b 1
)

echo.
echo [2/3] Running System Verification Suite...
python run_tests.py
if %errorlevel% neq 0 (
    echo [WARNING] Some tests encountered issues. Review log above.
)

echo.
echo [3/3] Launching Sentinel-Risk Applications...
echo ---------------------------------------------------------------------
echo  Starting FastAPI Backend on http://127.0.0.1:8000
echo  Starting Streamlit Dashboard on http://127.0.0.1:8501
echo ---------------------------------------------------------------------
echo.

start "Sentinel-Risk FastAPI Backend" cmd /k "python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload"
timeout /t 3 /nobreak >nul
start "Sentinel-Risk Streamlit Terminal" cmd /k "streamlit run src/dashboard/app.py"

echo Applications launched in separate windows!
echo  - Swagger API Docs: http://127.0.0.1:8000/docs
echo  - Interactive Dashboard: http://127.0.0.1:8501
echo.
pause
