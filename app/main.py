from datetime import datetime
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.exceptions import HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi import FastAPI, Request

# define a FastAPI app
app = FastAPI()

# mount the 'static' folder to be accessible via /static
app.mount('/static', StaticFiles(directory='static'), name='static')

# define the templates folder
templates = Jinja2Templates(directory='templates')

# override the HTTPException handler for 404 template
@app.exception_handler(StarletteHTTPException)  # <-- Use StarletteHTTPException
async def custom_404_handler(request: Request, exc: StarletteHTTPException):
    # render the 404 template for 404 errors
    # pass other errors to default handlers
    if exc.status_code == 404:
        return templates.TemplateResponse(
            request=request,
            name="404.html",
            status_code=404
        )
    # for other errors (like 401, 403, 500), return the default behavior
    return exc


@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='index.html',
        context={'request': request},
        status_code=200
    )


@app.get('/health', status_code=200)
def health() -> dict[str, str]:
    return {
        'status': 'ok',
        'service': 'Lingora API',
        'timestamp': datetime.now().isoformat()
    }


@app.get('/translator', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='translator.html',
        context={'request': request},
        status_code=200
    )
