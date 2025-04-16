# src/parkin_web/api/routes/web.py
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.parkin_web import crud, models
from src.parkin_web.api import deps

router = APIRouter(tags=["web"])

templates = Jinja2Templates(directory="templates")


@router.get("/")
async def home(request: Request):
    """
    Render the home page.
    """
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/login")
async def login_page(request: Request):
    """
    Render the login page.
    """
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.get("/register")
async def register_page(request: Request):
    """
    Render the registration page.
    """
    return templates.TemplateResponse("auth/register.html", {"request": request})


@router.get("/profile")
async def profile_page(
    request: Request, 
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Render the user profile page.
    """
    return templates.TemplateResponse(
        "profile/index.html", 
        {"request": request, "user": current_user}
    )


@router.get("/dashboard")
async def dashboard_page(
    request: Request, 
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Render the user dashboard page.
    """
    return templates.TemplateResponse(
        "profile/dashboard.html", 
        {"request": request, "user": current_user}
    )


@router.get("/my-bookings")
async def my_bookings_page(
    request: Request, 
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Render the user's bookings page.
    """
    bookings = crud.booking.get_user_bookings(db, user_id=current_user.id)
    return templates.TemplateResponse(
        "profile/bookings.html", 
        {"request": request, "user": current_user, "bookings": bookings}
    )


@router.get("/my-spaces")
async def my_spaces_page(
    request: Request, 
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Render the user's parking spaces page.
    """
    parking_spaces = crud.parking_space.get_multi_by_owner(db, owner_id=current_user.id)
    return templates.TemplateResponse(
        "profile/spaces.html", 
        {"request": request, "user": current_user, "parking_spaces": parking_spaces}
    )


@router.get("/hosting")
async def hosting_page(
    request: Request, 
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Render the hosting dashboard page.
    """
    bookings = crud.booking.get_host_bookings(db, host_id=current_user.id)
    return templates.TemplateResponse(
        "profile/hosting.html", 
        {"request": request, "user": current_user, "bookings": bookings}
    )


@router.get("/list-space")
async def list_space_page(
    request: Request, 
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Render the list space page.
    """
    return templates.TemplateResponse(
        "profile/list-space.html", 
        {"request": request, "user": current_user}
    )


@router.get("/search")
async def search_page(
    request: Request,
    location: str = None,
    start_time: str = None,
    end_time: str = None,
    has_ev_charging: bool = None,
    has_security_camera: bool = None,
):
    """
    Render the search results page.
    """
    return templates.TemplateResponse(
        "search.html", 
        {
            "request": request,
            "location": location,
            "start_time": start_time,
            "end_time": end_time,
            "has_ev_charging": has_ev_charging,
            "has_security_camera": has_security_camera,
        }
    )


@router.get("/spaces/{space_id}")
async def space_details_page(
    request: Request, 
    space_id: int,
    db: Session = Depends(deps.get_db),
):
    """
    Render the parking space details page.
    """
    space = crud.parking_space.get(db, id=space_id)
    if not space:
        raise HTTPException(status_code=404, detail="Parking space not found")
    
    # Increment views count
    crud.parking_space.increment_views(db, id=space_id)
    
    return templates.TemplateResponse(
        "space-details.html", 
        {"request": request, "space": space}
    )


@router.get("/booking/{booking_id}")
async def booking_details_page(
    request: Request, 
    booking_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Render the booking details page.
    """
    booking = crud.booking.get(db, id=booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check if user is authorized to view this booking
    space = crud.parking_space.get(db, id=booking.parking_space_id)
    if booking.user_id != current_user.id and space.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this booking")
    
    return templates.TemplateResponse(
        "booking-details.html", 
        {"request": request, "booking": booking, "user": current_user}
    )