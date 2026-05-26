import os
import asyncio
import base64
import cv2
import speech_recognition as sr
import pyttsx3
import ollama
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import socketio
from dotenv import load_dotenv

# Import the isolated system commands page we just created
from system_commands import SystemController

load_dotenv()

# 1. Initialize FastAPI App & Socket.IO Async Server Gateway
app = FastAPI(title="FRIDAY Core Tactical Interface")
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

# Mount the static web UI asset folder
app.mount("/interface", StaticFiles(directory="web", html=True), name="web")

class FridayAsyncCore:
    def __init__(self):
        self.is_processing = False
        self.chat_history = []
        
        # Local AI Core Models
        self.text_model = "llama3.2"   # Ultra-fast text processing model
        self.vision_model = "llava"     # Heavy multimodal visual analysis model
        
        # Computer Vision Pipelines
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.latest_frame = None        # Shared memory cache to prevent hardware conflicts
        
        # Initialize the new App-Opening Sub-System Page Controller
        self.system_controller = SystemController()
        
        # Prime Friday's internal logic memory system
        self.chat_history.append({
            "role": "system",
            "content": "You are FRIDAY, an elite tactical artificial intelligence assistant. Keep responses restricted to 1-2 sharp sentences. Always address the user as Sir."
        })

    def speak(self, text):
        """Dispatches voice tracks safely on an isolated background execution thread."""
        print(f"[FRIDAY REPLY]: {text}\n")
        
        def _speak_worker():
            try:
                # Ephemeral local engine instance prevents async thread resource blocks
                engine = pyttsx3.init()
                voices = engine.getProperty('voices')
                for voice in voices:
                    if any(x in voice.id.upper() or x in voice.name.upper() for x in ["EN-GB", "HAZEL", "ZIRA", "DAVID"]):
                        engine.setProperty('voice', voice.id)
                        break
                engine.setProperty('rate', 190)
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                print(f"[TTS AUDIO ERROR]: {e}")

        import threading
        threading.Thread(target=_speak_worker, daemon=True).start()

    async def run_voice_listener(self):
        """Asynchronous microphone capture and Google Speech recognition translator loop."""
        recognizer = sr.Recognizer()
        print("[SYSTEM]: Initializing Microphone Node...")
        
        while True:
            try:
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.4)
                    recognizer.dynamic_energy_threshold = False
                    recognizer.energy_threshold = 350 # Filters ambient background room noise
                    recognizer.pause_threshold = 0.8
                    
                    # Offload the blocking listen loop to an executor thread to keep FastAPI breathing
                    loop = asyncio.get_event_loop()
                    audio = await loop.run_in_executor(None, lambda: recognizer.listen(source, timeout=None, phrase_time_limit=6))
                    
                    if self.is_processing:
                        continue
                        
                    query = await loop.run_in_executor(None, lambda: recognizer.recognize_google(audio))
                    if not query.strip() or len(query.split()) < 2:
                        continue
                        
                    print(f"\n[YOU DETECTED]: {query}")
                    # Push user text immediately to the browser chat box
                    await sio.emit('chat_msg', {'sender': 'sir', 'text': query})
                    
                    self.is_processing = True
                    asyncio.create_task(self.process_intelligence(query))
                    
            except Exception:
                await asyncio.sleep(0.1)

    async def run_optical_stream(self):
        """Real-time camera matrix publisher using low-overhead DirectShow parsing."""
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        print("[SYSTEM]: Initializing Optical HUD Matrix via DirectShow backend...")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                await asyncio.sleep(0.01)
                continue
                
            frame = cv2.flip(frame, 1)
            
            # Cache frame directly into shared memory so process_intelligence can access it
            self.latest_frame = frame.copy()
            
            # Process face markers
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(30, 30))
            
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 240, 0), 2)
                cv2.putText(frame, "TARGET IDENTIFIED: SIR", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 240, 0), 1)
                            
            # Compress and encode into base64 text for WebSocket shipment
            _, buffer = cv2.imencode('.jpg', frame)
            b64_frame = base64.b64encode(buffer).decode('utf-8')
            
            await sio.emit('video_frame', {'image': b64_frame})
            await asyncio.sleep(0.03) # Mainstream target output frame boundary: 30 FPS

    async def process_intelligence(self, user_input):
        """Processes operations by balancing system page commands and AI models."""
        try:
            await sio.emit('status_update', {'text': 'Processing Logic...'})
            
            # INTERCEPT: Pass text through our separate system command page engine first
            system_reply = self.system_controller.execute_command(user_input)
            if system_reply:
                # If an app trigger matches, push feedback immediately and bypass the AI models entirely!
                await sio.emit('chat_msg', {'sender': 'friday', 'text': system_reply})
                await sio.emit('status_update', {'text': 'Core Secure'})
                self.speak(system_reply)
                return

            # FALLBACK: If it's not a local application command, forward it to Ollama
            vision_triggers = ["look", "see", "what am i", "holding", "this", "camera", "view"]
            requires_vision = any(word in user_input.lower() for word in vision_triggers)
            current_model = self.vision_model if requires_vision else self.text_model
            
            payload = []
            if requires_vision and self.latest_frame is not None:
                # Use the clean cached image snapshot from shared memory
                _, buffer = cv2.imencode('.jpg', self.latest_frame)
                b64_image = base64.b64encode(buffer).decode('utf-8')
                payload = [{
                    "role": "user",
                    "content": user_input,
                    "images": [b64_image]
                }]
            else:
                self.chat_history.append({"role": "user", "content": user_input})
                payload = self.chat_history

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, lambda: ollama.chat(model=current_model, messages=payload))
            response_text = response['message']['content']
            
            if not requires_vision:
                self.chat_history.append({"role": "assistant", "content": response_text})
            
            # Send text string down to client HTML browser page
            await sio.emit('chat_msg', {'sender': 'friday', 'text': response_text})
            await sio.emit('status_update', {'text': 'Core Secure'})
            self.speak(response_text)
            
        except Exception as e:
            print(f"[AI ERROR MATRIX]: {e}")
            self.speak("Operational fault inside my processing core, Sir.")
        finally:
            self.is_processing = False

friday_core = FridayAsyncCore()

@sio.event
async def connect(sid, environ):
    print(f"[UI HANDSHAKE secured]: Client node {sid} attached to matrix.")
    await sio.emit('status_update', {'text': 'Matrices Online. System Unlocked.'}, room=sid)
    friday_core.speak("All local asynchronous systems initialized, Sir. Friday interface ready.")

@app.on_event("startup")
async def startup_event():
    # Spin up our parallel hardware processing streams inside the event loop matrix concurrently
    asyncio.create_task(friday_core.run_voice_listener())
    asyncio.create_task(friday_core.run_optical_stream())

if __name__ == "__main__":
    uvicorn.run(socket_app, host="127.0.0.1", port=8000, log_level="info")