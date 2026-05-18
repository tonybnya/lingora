from datetime import datetime
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Request

# define a FastAPI app
app = FastAPI()

# define the templates folder
templates = Jinja2Templates(directory='templates')


@app.get('/health')
def health():
    return {
        'status': 'ok',
        'service': 'Lingora API',
        'timestamp': datetime.now()
    }


@app.get('/index', response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})
