from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()

# Setup static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get('/')
def home():
    return FileResponse('templates/index.html')

@app.get('/content')
def content():
    with open('data.txt', 'r') as file:
        content = file.read().replace('\n', ' <br> ')
    return {'content': content.split()}
