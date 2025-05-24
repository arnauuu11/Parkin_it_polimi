from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import os
import sys
from pathlib import Path
import starlette.routing
from datetime import datetime

# Create the FastAPI app first
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

# Adjust paths for Vercel deployment
# Vercel uses a different directory structure in production
base_dir = os.path.dirname(os.path.abspath(__file__))

# Use existing paths or default to creating temporary ones if possible
static_dir = os.path.join(base_dir, "static")
if not os.path.exists(static_dir):
    try:
        os.makedirs(static_dir)
    except:
        # If we can't create the directory, use a temporary path
        static_dir = "/tmp/static"
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)

# Set up templates with better error handling
templates_dir = os.path.join(base_dir, "templates")
if not os.path.exists(templates_dir):
    try:
        os.makedirs(templates_dir)
    except:
        # If we can't create the directory, use a temporary path
        templates_dir = "/tmp/templates"
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir)

# Try to set up static files and templates, but with error handling
try:
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    templates = Jinja2Templates(directory=templates_dir)
except Exception as e:
    print(f"Error setting up static files or templates: {e}")
    templates = None

# Simple health check endpoint that doesn't rely on templates
@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "version": "0.1.0",
        "time": str(datetime.now()),
        "environment": os.environ.get("VERCEL_ENV", "local"),
        "directories": {
            "base_dir": base_dir,
            "static_dir": static_dir,
            "templates_dir": templates_dir,
            "static_exists": os.path.exists(static_dir),
            "templates_exists": os.path.exists(templates_dir),
        }
    }

# Simple API endpoint
@app.get("/api")
async def api_root():
    """
    API root endpoint.
    """
    return {"message": "Welcome to Parkin-It API"}

# Home page with error handling
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Render the home page with fallback to JSON response.
    """
    try:
        if templates:
            return templates.TemplateResponse("index.html", {"request": request})
        else:
            return JSONResponse(content={"message": "Templates are not available. Check /api/health for details."})
    except Exception as e:
        return JSONResponse(content={"error": str(e)})

# Other routes with error handling
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """
    Render the login page.
    """
    try:
        if templates:
            return templates.TemplateResponse("auth/login.html", {"request": request})
        else:
            return JSONResponse(content={"message": "Templates are not available. Check /api/health for details."})
    except Exception as e:
        return JSONResponse(content={"error": str(e)})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """
    Render the registration page.
    """
    try:
        if templates:
            return templates.TemplateResponse("register.html", {"request": request})
        else:
            return JSONResponse(content={"message": "Templates are not available. Check /api/health for details."})
    except Exception as e:
        return JSONResponse(content={"error": str(e)})

@app.get("/find-parking", response_class=HTMLResponse)
async def find_parking(request: Request):
    """
    Render the find parking page.
    """
    try:
        if templates:
            return templates.TemplateResponse("find-parking.html", {"request": request})
        else:
            return JSONResponse(content={"message": "Templates are not available. Check /api/health for details."})
    except Exception as e:
        return JSONResponse(content={"error": str(e)})

@app.get("/list-space", response_class=HTMLResponse)
async def list_space(request: Request):
    """
    Render the list space page.
    """
    try:
        if templates:
            return templates.TemplateResponse("list-space.html", {"request": request})
        else:
            return JSONResponse(content={"message": "Templates are not available. Check /api/health for details."})
    except Exception as e:
        return JSONResponse(content={"error": str(e)})

@app.get("/pricing", response_class=HTMLResponse)
async def pricing(request: Request):
    """
    Render the pricing page.
    """
    try:
        if templates:
            return templates.TemplateResponse("pricing.html", {"request": request})
        else:
            return JSONResponse(content={"message": "Templates are not available. Check /api/health for details."})
    except Exception as e:
        return JSONResponse(content={"error": str(e)})

@app.get("/security", response_class=HTMLResponse)
async def security(request: Request):
    """
    Render the security page.
    """
    try:
        if templates:
            return templates.TemplateResponse("security.html", {"request": request})
        else:
            return JSONResponse(content={"message": "Templates are not available. Check /api/health for details."})
    except Exception as e:
        return JSONResponse(content={"error": str(e)})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    """
    Render the about page.
    """
    try:
        if templates:
            return templates.TemplateResponse("about.html", {"request": request})
        else:
            return JSONResponse(content={"message": "Templates are not available. Check /api/health for details."})
    except Exception as e:
        return JSONResponse(content={"error": str(e)})

@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    """
    Render the contact page.
    """
    try:
        if templates:
            return templates.TemplateResponse("contact.html", {"request": request})
        else:
            return JSONResponse(content={"message": "Templates are not available. Check /api/health for details."})
    except Exception as e:
        return JSONResponse(content={"error": str(e)})

# Placeholder image handler
@app.get("/api/placeholder/{width}/{height}")
async def placeholder(width: int, height: int):
    """
    Serve placeholder images.
    """
    # Return a simple placeholder image or redirect to a service
    # For now, return a simple 404 since we don't have actual images
    return {"message": f"Placeholder image requested: {width}x{height}"}

# Special handler for Vercel - this needs to be AFTER all other routes
@app.get("/{full_path:path}")
async def catch_all(request: Request, full_path: str):
    """
    Catch-all route to handle all paths for Vercel serverless deployment.
    """
    try:
        # Try to serve a template if available
        if templates:
            try:
                return templates.TemplateResponse(f"{full_path}.html", {"request": request})
            except Exception:
                try:
                    return templates.TemplateResponse("index.html", {"request": request})
                except Exception:
                    return JSONResponse(content={"error": "Page not found", "path": full_path})
        else:
            return JSONResponse(content={"message": "Templates are not available. Check /api/health for details."})
    except Exception as e:
        return JSONResponse(content={"error": str(e)})