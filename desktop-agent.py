import base64, io, json, os, platform, secrets, subprocess, sys, threading, webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

try:
    import pyautogui
except ImportError:
    pyautogui = None

HOST = "127.0.0.1"
PORT = 8765
TOKEN = os.environ.get("HAYAGRIVA_AGENT_TOKEN") or secrets.token_urlsafe(24)
ALLOWED_APPS = {
    "chrome": ["chrome"],
    "google chrome": ["chrome"],
    "edge": ["msedge"],
    "microsoft edge": ["msedge"],
    "notepad": ["notepad"],
    "calculator": ["calc"],
    "calc": ["calc"],
    "paint": ["mspaint"],
    "explorer": ["explorer"],
    "file explorer": ["explorer"],
    "terminal": ["wt"],
    "cmd": ["cmd"],
    "powershell": ["powershell"],
}
KEYS = {"esc":"esc","escape":"esc","return":"enter","space":"space","backspace":"backspace",
        "delete":"delete","del":"delete","tab":"tab","up":"up","down":"down","left":"left","right":"right",
        "home":"home","end":"end"}

def launch_app(name):
    key = name.strip().lower()
    if key not in ALLOWED_APPS:
        raise ValueError("App is not on the safe allow-list.")
    cmd = ALLOWED_APPS[key]
    if platform.system() == "Windows":
        subprocess.Popen(cmd, shell=False)
    else:
        subprocess.Popen(cmd, shell=False)

def require_token(h):
    if h.headers.get("X-Hayagriva-Token") != TOKEN:
        raise PermissionError("Invalid desktop agent token.")

class Handler(BaseHTTPRequestHandler):
    server_version = "HayagrivaDesktopAgent/1.0"

    def send_json(self, code, payload):
        raw = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type","application/json")
        self.send_header("Access-Control-Allow-Origin","*")
        self.send_header("Access-Control-Allow-Headers","Content-Type, X-Hayagriva-Token")
        self.send_header("Access-Control-Allow-Methods","POST, OPTIONS")
        self.end_headers()
        self.wfile.write(raw)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin","*")
        self.send_header("Access-Control-Allow-Headers","Content-Type, X-Hayagriva-Token")
        self.send_header("Access-Control-Allow-Methods","POST, OPTIONS")
        self.end_headers()

    def do_POST(self):
        try:
            require_token(self)
            length = int(self.headers.get("Content-Length","0"))
            body = json.loads(self.rfile.read(length) or b"{}")
            if self.path == "/health":
                return self.send_json(200, {"ok":True,"platform":platform.platform()})
            if self.path == "/screenshot":
                if pyautogui is None:
                    raise RuntimeError("Install pyautogui to enable screenshots.")
                img = pyautogui.screenshot()
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                return self.send_json(200, {"ok":True,"image":base64.b64encode(buf.getvalue()).decode()})
            if self.path == "/action":
                action = body.get("action","")
                if action == "open_url":
                    url = str(body.get("value","")).strip()
                    if not (url.startswith("https://") or url.startswith("http://")):
                        raise ValueError("Only http/https URLs are allowed.")
                    webbrowser.open(url)
                    return self.send_json(200, {"ok":True,"message":"Opened "+url})
                if action == "open_app":
                    launch_app(str(body.get("value","")))
                    return self.send_json(200, {"ok":True,"message":"Opened "+str(body.get("value",""))})
                if pyautogui is None:
                    raise RuntimeError("Install pyautogui to use keyboard actions.")
                if action == "type":
                    text = str(body.get("value",""))
                    if len(text) > 1000:
                        raise ValueError("Typed text is limited to 1000 characters.")
                    pyautogui.write(text, interval=0.01)
                    return self.send_json(200, {"ok":True,"message":"Typed the requested text."})
                if action == "press":
                    key = KEYS.get(str(body.get("value","")).lower(), str(body.get("value","")).lower())
                    pyautogui.press(key)
                    return self.send_json(200, {"ok":True,"message":"Pressed "+key+"."})
                if action == "hotkey":
                    parts = [x.strip().lower() for x in str(body.get("value","")).split("+") if x.strip()]
                    if not parts or len(parts) > 4:
                        raise ValueError("Hotkey must contain 1 to 4 keys.")
                    pyautogui.hotkey(*parts)
                    return self.send_json(200, {"ok":True,"message":"Pressed "+"+".join(parts)+"."})
                if action == "click":
                    x,y=int(body.get("x")),int(body.get("y"))
                    pyautogui.click(x,y)
                    return self.send_json(200, {"ok":True,"message":f"Clicked {x},{y}."})
                raise ValueError("Unsupported desktop action.")
        except PermissionError as e:
            self.send_json(401, {"ok":False,"error":str(e)})
        except Exception as e:
            self.send_json(400, {"ok":False,"error":str(e)})

    def log_message(self, fmt, *args):
        print("[Hayagriva Agent]", fmt % args)

if __name__ == "__main__":
    print("\nHAYAGRIVA DESKTOP AGENT")
    print("Local address: http://127.0.0.1:%d" % PORT)
    print("Agent token (paste into Hayagriva > Desktop Agent):")
    print(TOKEN)
    print("\nKeep this terminal running while you use PC control. Press Ctrl+C to stop.\n")
    ThreadingHTTPServer((HOST,PORT), Handler).serve_forever()
