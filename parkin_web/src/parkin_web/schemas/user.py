# src/parkin_web/schemas/user.py
from typing import Optional, List
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime


# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    bio: Optional[str] = None
    user_type: Optional[str] = "driver"
    is_active: Optional[bool] = True


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str
    
    @validator('password')
    def password_min_length(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None
    
    @validator('password')
    def password_min_length(cls, v):
        if v is not None and len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


# Driver-specific information
class DriverInfo(BaseModel):
    driving_license: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_plate: Optional[str] = None


# Host-specific information
class HostInfo(BaseModel):
    bank_account: Optional[str] = None
    tax_id: Optional[str] = None


# Additional properties to return via API
class User(UserBase):
    id: int
    profile_image: Optional[str] = None
    rating: float
    total_ratings: int
    created_at: datetime
    updated_at: datetime
    is_superuser: bool
    is_verified: bool
    
    class Config:
        orm_mode = True


# Additional properties for detailed user information
class UserDetail(User):
    driver_info: Optional[DriverInfo] = None
    host_info: Optional[HostInfo] = None
    
    class Config:
        orm_mode = True