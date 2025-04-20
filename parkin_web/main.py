from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
import os

app = FastAPI(
    title="Parkin-It",
    description="A secure parking rental platform connecting drivers with parking space owners",
    version="0.1.0"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files - make sure the directory exists
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
    
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Set up templates
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Render the home page.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """
    Render the login page.
    """
    return templates.TemplateResponse("auth/login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """
    Render the registration page.
    """
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/find-parking", response_class=HTMLResponse)
async def find_parking(request: Request):
    """
    Render the find parking page.
    """
    return templates.TemplateResponse("find-parking.html", {"request": request})

@app.get("/list-space", response_class=HTMLResponse)
async def list_space(request: Request):
    """
    Render the list space page.
    """
    return templates.TemplateResponse("list-space.html", {"request": request})

@app.get("/pricing", response_class=HTMLResponse)
async def pricing(request: Request):
    """
    Render the pricing page.
    """
    return templates.TemplateResponse("pricing.html", {"request": request})

@app.get("/security", response_class=HTMLResponse)
async def security(request: Request):
    """
    Render the security page.
    """
    return templates.TemplateResponse("security.html", {"request": request})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    """
    Render the about page.
    """
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    """
    Render the contact page.
    """
    return templates.TemplateResponse("contact.html", {"request": request})

# Placeholder image handler
@app.get("/api/placeholder/{width}/{height}")
async def placeholder(width: int, height: int):
    """
    Serve placeholder images.
    """
    # Return a simple placeholder image or redirect to a service
    # For now, return a simple 404 since we don't have actual images
    return {"message": f"Placeholder image requested: {width}x{height}"}

@app.get("/api")
async def api_root():
    """
    API root endpoint.
    """
    return {"message": "Welcome to Parkin-It API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)