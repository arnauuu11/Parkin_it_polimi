# src/parkin_web/schemas/parking_space.py
from typing import Optional, List
from pydantic import BaseModel, validator, Field
from datetime import datetime
from enum import Enum


# Enum for parking type
class ParkingType(str, Enum):
    DRIVEWAY = "driveway"
    GARAGE = "garage"
    LOT = "lot"
    STREET = "street"
    UNDERGROUND = "underground"


# Schema for parking space image
class ParkingSpaceImageBase(BaseModel):
    url: str
    description: Optional[str] = None
    is_main: bool = False


class ParkingSpaceImageCreate(ParkingSpaceImageBase):
    pass


class ParkingSpaceImage(ParkingSpaceImageBase):
    id: int
    parking_space_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True


# Schema for availability schedule
class AvailabilityScheduleBase(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6)  # 0-6 for Monday-Sunday
    start_time: str  # Format: HH:MM
    end_time: str  # Format: HH:MM
    is_available: bool = True
    
    @validator('day_of_week')
    def validate_day_of_week(cls, v):
        if v < 0 or v > 6:
            raise ValueError('Day of week must be between 0 (Monday) and 6 (Sunday)')
        return v
    
    @validator('start_time', 'end_time')
    def validate_time_format(cls, v):
        try:
            hour, minute = v.split(':')
            if not (0 <= int(hour) <= 23 and 0 <= int(minute) <= 59):
                raise ValueError()
        except:
            raise ValueError('Time must be in HH:MM format')
        return v


class AvailabilityScheduleCreate(AvailabilityScheduleBase):
    pass


class AvailabilitySchedule(AvailabilityScheduleBase):
    id: int
    parking_space_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True


# Base schema for parking space
class ParkingSpaceBase(BaseModel):
    title: str
    description: Optional[str] = None
    
    # Location details
    address: str
    city: str
    state: str
    zip_code: str
    country: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Parking details
    parking_type: ParkingType = ParkingType.DRIVEWAY
    hourly_rate: float
    daily_rate: Optional[float] = None
    monthly_rate: Optional[float] = None
    width: Optional[float] = None  # in feet
    length: Optional[float] = None  # in feet
    height: Optional[float] = None  # in feet (for garages)
    
    # Availability
    is_available: bool = True
    is_active: bool = True
    instant_booking: bool = False
    
    # Special features
    has_security_camera: bool = False
    has_ev_charging: bool = False
    ev_charging_rate: Optional[float] = None  # per kWh
    has_covered_parking: bool = False
    has_gate_access: bool = False
    access_instructions: Optional[str] = None


# Schema for creating a parking space
class ParkingSpaceCreate(ParkingSpaceBase):
    availability_schedules: Optional[List[AvailabilityScheduleCreate]] = None


# Schema for updating a parking space
class ParkingSpaceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    
    # Location details
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Parking details
    parking_type: Optional[ParkingType] = None
    hourly_rate: Optional[float] = None
    daily_rate: Optional[float] = None
    monthly_rate: Optional[float] = None
    width: Optional[float] = None
    length: Optional[float] = None
    height: Optional[float] = None
    
    # Availability
    is_available: Optional[bool] = None
    is_active: Optional[bool] = None
    instant_booking: Optional[bool] = None
    
    # Special features
    has_security_camera: Optional[bool] = None
    has_ev_charging: Optional[bool] = None
    ev_charging_rate: Optional[float] = None
    has_covered_parking: Optional[bool] = None
    has_gate_access: Optional[bool] = None
    access_instructions: Optional[str] = None


# Schema for reading a parking space
class ParkingSpace(ParkingSpaceBase):
    id: int
    owner_id: int
    main_image: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Analytics
    views_count: int
    bookings_count: int
    average_rating: float
    reviews_count: int
    
    class Config:
        orm_mode = True


# Schema for detailed parking space information
class ParkingSpaceDetail(ParkingSpace):
    images: List[ParkingSpaceImage] = []
    availability_schedules: List[AvailabilitySchedule] = []
    
    class Config:
        orm_mode = True


# Schema for search results
class ParkingSpaceSearchResult(BaseModel):
    total: int
    results: List[ParkingSpace]
    
    class Config:
        orm_mode = True