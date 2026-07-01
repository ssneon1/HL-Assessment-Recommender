from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

from models import ChatRequest, ChatResponse
from agent import process_chat

# Load environment variables
load_dotenv()

app = FastAPI(title="SHL Assessment Recommender")

# Mount static files under /static (just in case)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_index():
    return FileResponse("static/index.html")

@app.get("/styles.css")
def get_css():
    return FileResponse("static/styles.css")

@app.get("/script.js")
def get_js():
    return FileResponse("static/script.js")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    return process_chat(request)
