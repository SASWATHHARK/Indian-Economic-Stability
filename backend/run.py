"""
Alternative entry point for running the FastAPI server
Can be used if main.py imports don't work correctly
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    from main import app
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

