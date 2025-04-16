# src/parkin_web/api/routes/parking.py
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.parkin_web import crud, models, schemas
from src.parkin_web.api import deps

router = APIRouter(prefix="/parking", tags=["parking"])


@router.get("/", response_model=schemas.ParkingSpaceSearchResult)
def search_parking_spaces(
    *,
    db: Session = Depends(deps.get_db),
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    city: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    has_security_camera: Optional[bool] = None,
    has_ev_charging: Optional[bool] = None,
    has_covered_parking: Optional[bool] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    skip: int = 0,
    limit: int = 10,
) -> Any:
    """
    Search for parking spaces with filters.
    """
    parking_spaces = crud.parking_space.search(
        db,
        latitude=latitude,
        longitude=longitude,
        city=city,
        start_time=start_time,
        end_time=end_time,
        has_security_camera=has_security_camera,
        has_ev_charging=has_ev_charging,
        has_covered_parking=has_covered_parking,
        min_price=min_price,
        max_price=max_price,
        skip=skip,
        limit=limit,
    )
    return {"total": len(parking_spaces), "results": parking_spaces}


@router.post("/", response_model=schemas.ParkingSpace)
def create_parking_space(
    *,
    db: Session = Depends(deps.get_db),
    parking_space_in: schemas.ParkingSpaceCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new parking space.
    """
    parking_space = crud.parking_space.create_with_owner(
        db=db, obj_in=parking_space_in, owner_id=current_user.id
    )
    return parking_space


@router.get("/{id}", response_model=schemas.ParkingSpaceDetail)
def get_parking_space(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """
    Get parking space by ID.
    """
    parking_space = crud.parking_space.get(db=db, id=id)
    if not parking_space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parking space not found",
        )
    
    # Increment views count
    crud.parking_space.increment_views(db=db, id=id)
    
    return parking_space


@router.put("/{id}", response_model=schemas.ParkingSpace)
def update_parking_space(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    parking_space_in: schemas.ParkingSpaceUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update parking space.
    """
    parking_space = crud.parking_space.get(db=db, id=id)
    if not parking_space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parking space not found",
        )
    if parking_space.owner_id != current_user.id and not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this parking space",
        )
    parking_space = crud.parking_space.update(db=db, db_obj=parking_space, obj_in=parking_space_in)
    return parking_space


@router.delete("/{id}", response_model=schemas.Msg)
def delete_parking_space(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete parking space.
    """
    parking_space = crud.parking_space.get(db=db, id=id)
    if not parking_space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parking space not found",
        )
    if parking_space.owner_id != current_user.id and not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this parking space",
        )
    crud.parking_space.remove(db=db, id=id)
    return {"msg": "Parking space deleted successfully"}


@router.post("/{id}/images", response_model=schemas.ParkingSpaceImage)
def upload_parking_space_image(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    image_in: schemas.ParkingSpaceImageCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Upload parking space image.
    """
    parking_space = crud.parking_space.get(db=db, id=id)
    if not parking_space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parking space not found",
        )
    if parking_space.owner_id != current_user.id and not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to upload images for this parking space",
        )
    image = crud.parking_space_image.create_with_parking_space(
        db=db, obj_in=image_in, parking_space_id=id
    )
    return image


@router.get("/{id}/availability", response_model=List[schemas.AvailabilitySchedule])
def get_parking_space_availability(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """
    Get parking space availability schedules.
    """
    parking_space = crud.parking_space.get(db=db, id=id)
    if not parking_space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parking space not found",
        )
    return crud.availability_schedule.get_by_parking_space(db=db, parking_space_id=id)


@router.post("/{id}/availability", response_model=schemas.AvailabilitySchedule)
def create_availability_schedule(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    schedule_in: schemas.AvailabilityScheduleCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create parking space availability schedule.
    """
    parking_space = crud.parking_space.get(db=db, id=id)
    if not parking_space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parking space not found",
        )
    if parking_space.owner_id != current_user.id and not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to manage availability for this parking space",
        )
    schedule = crud.availability_schedule.create_with_parking_space(
        db=db, obj_in=schedule_in, parking_space_id=id
    )
    return schedule