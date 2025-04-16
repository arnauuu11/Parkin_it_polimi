# src/parkin_web/api/routes/users.py
from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import EmailStr
from sqlalchemy.orm import Session

from src.parkin_web import crud, models, schemas
from src.parkin_web.api import deps
from src.parkin_web.core.config import settings

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=schemas.User)
def read_user_me(
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.put("/me", response_model=schemas.User)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update current user.
    """
    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.get("/me/parking-spaces", response_model=List[schemas.ParkingSpace])
def read_user_parking_spaces(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get current user's parking spaces.
    """
    return crud.parking_space.get_multi_by_owner(
        db=db, owner_id=current_user.id, skip=skip, limit=limit
    )


@router.get("/me/reviews", response_model=List[schemas.Review])
def read_user_reviews(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get reviews for current user.
    """
    return crud.review.get_user_reviews(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )


@router.post("/me/driver-info", response_model=schemas.User)
def update_driver_info(
    *,
    db: Session = Depends(deps.get_db),
    driver_info: schemas.DriverInfo,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update driver information for current user.
    """
    # Update user_type if needed
    if current_user.user_type not in ["driver", "both"]:
        current_user.user_type = "both" if current_user.user_type == "host" else "driver"
    
    # Update driver info
    for key, value in driver_info.dict(exclude_unset=True).items():
        setattr(current_user, key, value)
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/me/host-info", response_model=schemas.User)
def update_host_info(
    *,
    db: Session = Depends(deps.get_db),
    host_info: schemas.HostInfo,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update host information for current user.
    """
    # Update user_type if needed
    if current_user.user_type not in ["host", "both"]:
        current_user.user_type = "both" if current_user.user_type == "driver" else "host"
    
    # Update host info
    for key, value in host_info.dict(exclude_unset=True).items():
        setattr(current_user, key, value)
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user = crud.user.get(db, id=user_id)
    if user == current_user:
        return user
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return user


# Admin endpoints
@router.get("/", response_model=List[schemas.User])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_superuser),
) -> Any:
    """
    Retrieve users.
    """
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    return users


@router.put("/{user_id}", response_model=schemas.User)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_superuser),
) -> Any:
    """
    Update a user.
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user


@router.delete("/{user_id}", response_model=schemas.Msg)
def delete_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    current_user: models.User = Depends(deps.get_current_superuser),
) -> Any:
    """
    Delete a user.
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Users cannot delete themselves",
        )
    user = crud.user.remove(db, id=user_id)
    return {"msg": "User deleted successfully"}