from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.exceptions import HTTPException
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

@app.get("/how-it-works")
def how_it_works():
    return FileResponse("static/how-it-works.html")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return FileResponse("static/404.html", status_code=404)

@app.exception_handler(500)
async def server_error_handler(request: Request, exc: Exception):
    return FileResponse("static/500.html", status_code=500)

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    return process_chat(request)
