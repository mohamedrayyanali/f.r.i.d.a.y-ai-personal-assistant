import subprocess
import sys
import threading

def stream_pipe(pipe, prefix=""):
    """Reads a pipe line by line and flushes it immediately to the console."""
    try:
        with pipe:
            for line in iter(pipe.readline, ''):
                print(f"{prefix}{line.strip()}")
    except Exception:
        pass

def run_agent():
    print("[SYSTEM]: Launching Agent with Unbuffered Multi-Thread Diagnostics...\n")
    
    # Launch subprocess with unbuffered streams
    process = subprocess.Popen(
        [sys.executable, "-u", "agent.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )
    
    # Create background threads to read stdout and stderr simultaneously
    stdout_thread = threading.Thread(target=stream_pipe, args=(process.stdout, ""))
    stderr_thread = threading.Thread(target=stream_pipe, args=(process.stderr, "[ERROR]: "))
    
    stdout_thread.start()
    stderr_thread.start()
    
    try:
        # Wait for the process to finish naturally or crash
        return_code = process.wait()
        stdout_thread.join()
        stderr_thread.join()
        
        if return_code != 0:
            print(f"\n[SYSTEM]: Agent terminated with exit code {return_code}")
        else:
            print("\n[SYSTEM]: Agent exited cleanly.")
            
    except KeyboardInterrupt:
        print("\n[SYSTEM]: Force terminating agent due to user interrupt...")
        process.terminate()

if __name__ == "__main__":
    run_agent()