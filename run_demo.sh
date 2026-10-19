#!/bin/bash
echo "====================================================================="
echo "   SENTINEL-RISK: S&P Global & CRISIL Campus Hackathon Platform"
echo "   Unified AI/NLP Risk Engine & Strategic Wholesale Stress Tester"
echo "====================================================================="
echo ""

echo "[1/3] Running System Verification Suite..."
python3 run_tests.py
if [ $? -ne 0 ]; then
    echo "[WARNING] Verification suite encountered errors."
fi

echo ""
echo "[2/3] Launching FastAPI Backend on port 8000..."
python3 -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000 &
API_PID=$!

sleep 2

echo "[3/3] Launching Streamlit Dashboard on port 8501..."
streamlit run src/dashboard/app.py --server.port 8501 &
STREAMLIT_PID=$!

echo ""
echo "Platform running!"
echo " - Swagger API Docs: http://127.0.0.1:8000/docs"
echo " - Executive Dashboard: http://127.0.0.1:8501"
echo ""
echo "Press Ctrl+C to stop servers."

trap "kill $API_PID $STREAMLIT_PID; exit" INT TERM
wait
