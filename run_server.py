"""
PAIMANA AI Infrastructure Monitoring Platform Launcher
Runs Uvicorn FastAPI Server on http://127.0.0.1:8000
"""

import os
import sys
import uvicorn
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

if __name__ == "__main__":
    print("=================================================================")
    print("  PAIMANA AI - Predictive Analytics & Early Warning Platform")
    print("  Ministry of Statistics & Programme Implementation (MoSPI)")
    print("=================================================================")
    print("Starting server on: http://127.0.0.1:8000")
    print("Press Ctrl+C to terminate.")
    
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=True)
