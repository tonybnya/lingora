from datetime import datetime
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Request

# define a FastAPI app
app = FastAPI()

# mount the 'static' folder to be accessible via /static
app.mount('/static', StaticFiles(directory='static'), name='static')

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
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='index.html',
        context={'request': request}
    )
