import os
import subprocess
import webbrowser

class SystemController:
    def __init__(self):
        # Dictionary mapping voice keywords to application paths
        # Update these paths if your applications are installed elsewhere!
        self.app_mapping = {
            "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "vs code": r"C:\Users\{username}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
            "discord": r"C:\Users\{username}\AppData\Local\Discord\Update.exe --processStart Discord.exe",
        }

    def execute_command(self, user_input: str) -> str:
        """Parses the user text and executes system operations."""
        text = user_input.lower()

        # 1. Handle Web URL Searches
        if "open website" in text or "go to" in text:
            # Extract domain (e.g., "go to youtube.com" -> "youtube.com")
            domain = text.replace("open website", "").replace("go to", "").strip()
            if not domain.startswith("http"):
                domain = "https://" + domain
            webbrowser.open(domain)
            return f"Opening connection to {domain}, Sir."

        # 2. Handle Application Launching
        if "open" in text:
            app_name = text.replace("open", "").strip()
            
            # Check matches inside our mapping array
            for key, path in self.app_mapping.items():
                if key in app_name:
                    try:
                        # Auto-fix pathing if it relies on a dynamic Windows profile name
                        if "{username}" in path:
                            path = path.format(username=os.getlogin())
                        
                        # Launch application in a detached background thread
                        subprocess.Popen(path, shell=True if " " in path else False)
                        return f"Initializing {key}, Sir."
                    except Exception as e:
                        return f"Failed to launch {key}. Path target obstructed."
            
            return f"Application {app_name} is not mapped in my current system directory, Sir."

        return ""