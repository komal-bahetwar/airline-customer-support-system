import os
import subprocess
import threading
import time
import sys

def run_api():
    # Change current working directory to where api.py is located
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print("Starting FastAPI server...")
    # Use 'exec' to replace the current process, ensuring signals are handled correctly
    # This assumes uvicorn is installed and accessible in the environment
    subprocess.run([sys.executable, "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"])

def run_streamlit():
    # Change current working directory to where streamlit_app.py is located
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print("Starting Streamlit app...")
    # This assumes streamlit is installed and accessible in the environment
    subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py", "--server.port", "8501", "--server.address", "0.0.0.0", "--server.headless", "true"])

if __name__ == "__main__":
    # Start FastAPI in a separate thread
    api_thread = threading.Thread(target=run_api)
    api_thread.daemon = True # Allow main program to exit even if threads are still running
    api_thread.start()

    print("Giving FastAPI a moment to start...")
    time.sleep(10) # Give FastAPI server time to spin up

    # Start Streamlit in the main thread (or another thread, but here for simplicity)
    # It's better to run Streamlit in the main process for better signal handling and browser opening
    # If you want it in a separate thread, make sure to handle its lifecycle properly.
    print("Starting Streamlit app...")
    run_streamlit()
    # If streamlit was also threaded, you'd join both threads here.

    print("Application finished.")
