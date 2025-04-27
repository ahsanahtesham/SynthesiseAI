from fastapi import FastAPI, Request, Form, Depends, HTTPException, status, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
import httpx
import os
import uvicorn
from typing import Optional
from pydantic import BaseModel
import json
from pathlib import Path

# Initialize FastAPI client application
client_app = FastAPI(
    title="AI Service Client",
    description="Client application for interacting with AI Service API",
)

# Set up templates and static files
templates_dir = Path(__file__).parent / "templates"
static_dir = Path(__file__).parent / "static"

templates = Jinja2Templates(directory=templates_dir)
client_app.mount("/static", StaticFiles(directory=static_dir), name="static")

# API URL
API_URL = "http://localhost:8000"  # URL of the main FastAPI service


# Model for storing access token
class Token(BaseModel):
    access_token: str
    token_type: str


# Helper function to get API client with authentication
async def get_api_client(token: Optional[str] = Cookie(None)):
    if not token:
        return httpx.AsyncClient(base_url=API_URL)
    return httpx.AsyncClient(
        base_url=API_URL,
        headers={"Authorization": f"Bearer {token}"}
    )


# Check if user is authenticated
async def is_authenticated(token: Optional[str] = Cookie(None)) -> bool:
    if not token:
        return False
    
    async with httpx.AsyncClient(base_url=API_URL) as client:
        try:
            response = await client.get(
                "/users/me/",
                headers={"Authorization": f"Bearer {token}"}
            )
            return response.status_code == 200
        except:
            return False


# Routes
@client_app.get("/", response_class=HTMLResponse)
async def root(request: Request, token: Optional[str] = Cookie(None)):
    """Home page"""
    authenticated = await is_authenticated(token)
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "authenticated": authenticated}
    )


@client_app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("login.html", {"request": request})


@client_app.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    """Handle login form submission"""
    async with httpx.AsyncClient(base_url=API_URL) as client:
        try:
            response = await client.post(
                "/token",
                data={"username": username, "password": password}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                response = RedirectResponse(url="/dashboard", status_code=303)
                response.set_cookie(key="token", value=token_data["access_token"])
                return response
            else:
                error_detail = "Invalid username or password"
                if response.status_code != 401:  # If not unauthorized, show actual error
                    try:
                        error_data = response.json()
                        error_detail = error_data.get("detail", error_detail)
                    except:
                        pass
                
                return templates.TemplateResponse(
                    "login.html",
                    {"request": request, "error": error_detail}
                )
        except Exception as e:
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error": f"Error connecting to API: {str(e)}"}
            )


@client_app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Registration page"""
    return templates.TemplateResponse("register.html", {"request": request})


@client_app.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    """Handle registration form submission"""
    async with httpx.AsyncClient(base_url=API_URL) as client:
        try:
            print(f"Trying to connect to {API_URL}/users/")
            response = await client.post(
                "/users/",
                json={"username": username, "email": email, "password": password}
            )

            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")
            
            if response.status_code == 200:
                # Successful registration, redirect to login
                return RedirectResponse(
                    url="/login?registered=true",
                    status_code=303
                )
            else:
                error_detail = "Registration failed"
                try:
                    error_data = response.json()
                    error_detail = error_data.get("detail", error_detail)
                except:
                    pass
                
                return templates.TemplateResponse(
                    "register.html",
                    {
                        "request": request,
                        "error": error_detail,
                        "username": username,
                        "email": email
                    }
                )
        except Exception as e:
            return templates.TemplateResponse(
                "register.html",
                {
                    "request": request,
                    "error": f"Error connecting to API: {str(e)}",
                    "username": username,
                    "email": email
                }
            )


@client_app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, token: Optional[str] = Cookie(None)):
    """User dashboard"""
    if not token:
        return RedirectResponse(url="/login", status_code=303)
    
    client = await get_api_client(token)
    
    try:
        # Get user info
        user_response = await client.get("/users/me/")
        if user_response.status_code != 200:
            response = RedirectResponse(url="/login", status_code=303)
            response.delete_cookie(key="token")
            return response
        
        user_data = user_response.json()
        
        # Get user's jobs
        jobs_response = await client.get("/jobs/")
        jobs_data = []
        if jobs_response.status_code == 200:
            jobs_data = jobs_response.json()
        
        # Get notifications
        notifications_response = await client.get("/notifications/")
        notifications = []
        if notifications_response.status_code == 200:
            notifications = notifications_response.json()
        
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "user": user_data,
                "jobs": jobs_data,
                "notifications": notifications
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": f"Error: {str(e)}"}
        )
    finally:
        await client.aclose()


@client_app.post("/submit-job")
async def submit_job(
    request: Request,
    prompt: str = Form(...),
    token: Optional[str] = Cookie(None)
):
    """Submit a new job"""
    if not token:
        return RedirectResponse(url="/login", status_code=303)
    
    client = await get_api_client(token)
    
    try:
        response = await client.post("/jobs/", json={"prompt": prompt})
        
        if response.status_code == 200:
            # Job submitted successfully
            return RedirectResponse(url="/dashboard", status_code=303)
        else:
            error_detail = "Failed to submit job"
            try:
                error_data = response.json()
                error_detail = error_data.get("detail", error_detail)
            except:
                pass
            
            # Get user info and jobs for displaying dashboard with error
            user_response = await client.get("/users/me/")
            user_data = user_response.json()
            
            jobs_response = await client.get("/jobs/")
            jobs_data = []
            if jobs_response.status_code == 200:
                jobs_data = jobs_response.json()
            
            notifications_response = await client.get("/notifications/")
            notifications = []
            if notifications_response.status_code == 200:
                notifications = notifications_response.json()
            
            return templates.TemplateResponse(
                "dashboard.html",
                {
                    "request": request,
                    "user": user_data,
                    "jobs": jobs_data,
                    "notifications": notifications,
                    "error": error_detail
                }
            )
    except Exception as e:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": f"Error: {str(e)}"}
        )
    finally:
        await client.aclose()


@client_app.get("/job/{job_id}", response_class=HTMLResponse)
async def view_job(
    request: Request,
    job_id: int,
    token: Optional[str] = Cookie(None)
):
    """View a specific job"""
    if not token:
        return RedirectResponse(url="/login", status_code=303)
    
    client = await get_api_client(token)
    
    try:
        job_response = await client.get(f"/jobs/{job_id}")
        
        if job_response.status_code == 200:
            job_data = job_response.json()
            return templates.TemplateResponse(
                "job_detail.html",
                {"request": request, "job": job_data}
            )
        else:
            return templates.TemplateResponse(
                "error.html",
                {"request": request, "error": "Job not found"}
            )
    except Exception as e:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": f"Error: {str(e)}"}
        )
    finally:
        await client.aclose()


@client_app.get("/documentation", response_class=HTMLResponse)
async def documentation(request: Request):
    """API documentation page"""
    return templates.TemplateResponse("documentation.html", {"request": request})


@client_app.get("/logout")
async def logout():
    """Logout user"""
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="token")
    return response


if __name__ == "__main__":
    # Create templates and static directories if they don't exist
    templates_dir.mkdir(exist_ok=True)
    static_dir.mkdir(exist_ok=True)
    
    # Run the client app
    uvicorn.run("client:client_app", host="127.0.0.1", port=8080, reload=True)