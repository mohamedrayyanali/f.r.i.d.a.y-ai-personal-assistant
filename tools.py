import os
import subprocess
import pyautogui
import time

def get_weather(city: str) -> str:
    """Mock weather routine for system fallback."""
    return f"The environmental matrix readouts for {city} indicate 28 degrees Celsius with clear visibility."

def search_web(query: str) -> str:
    """Mock web grid query routine."""
    return f"Web grid search executed for: '{query}'. Data packets retrieved successfully."

def send_email(to_address: str, subject: str, body: str) -> str:
    """Mock communication link routing routine."""
    return f"Communication link routed to {to_address}. Message queued."

def open_application(app_name: str) -> str:
    """
    Launches desktop applications based on user voice command strings.
    """
    app_lower = app_name.lower()
    
    try:
        # Standard Quick Launch Apps via Windows Commands
        if "chrome" in app_lower or "browser" in app_lower:
            subprocess.Popen(["start", "chrome"], shell=True)
            return "Launching Google Chrome, Sir."
            
        elif "code" in app_lower or "vs code" in app_lower or "visual studio" in app_lower:
            subprocess.Popen(["code"], shell=True)
            return "Opening Visual Studio Code environment."
            
        elif "notepad" in app_lower:
            subprocess.Popen(["notepad.exe"])
            return "Opening a blank text matrix canvas in Notepad."
            
        elif "calculator" in app_lower:
            subprocess.Popen(["calc.exe"])
            return "Initializing system calculator."
            
        elif "spotify" in app_lower:
            try:
                subprocess.Popen([os.path.expandvars(r"%APPDATA%\Spotify\Spotify.exe")])
            except Exception:
                pyautogui.hotkey('win', 'r')
                time.sleep(0.2)
                pyautogui.write('spotify')
                pyautogui.press('enter')
            return "Initializing Spotify audio frequencies, Sir."
            
        elif "discord" in app_lower:
            pyautogui.hotkey('win', 'r')
            time.sleep(0.2)
            pyautogui.write('discord')
            pyautogui.press('enter')
            return "Opening Discord communications array."

        # Dynamic Generic Fallback using Windows Search for any other app
        else:
            pyautogui.press('win')
            time.sleep(0.3)
            pyautogui.write(app_name)
            time.sleep(0.3)
            pyautogui.press('enter')
            return f"Attempting to locate and execute {app_name} via system search parameters."
            
    except Exception as e:
        return f"Failed to execute system application hook: {str(e)}"