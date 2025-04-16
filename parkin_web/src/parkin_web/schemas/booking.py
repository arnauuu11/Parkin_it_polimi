# src/parkin_web/schemas/booking.py
from typing import Optional, List
from pydantic import BaseModel, validator
from datetime import datetime
from enum import Enum


class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELED = "canceled"
    COMPLETED = "completed"
    REJECTED = "rejected"


class BookingDuration(str, Enum):
    HOURLY = "hourly"
    DAILY = "daily"
    MONTHLY = "monthly"


# Base Review schema
class ReviewBase(BaseModel):
    rating: int
    comment: Optional[str] = None
    
    @validator('rating')
    def rating_range(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Rating must be between 1 and 5')
        return v


class ReviewCreate(ReviewBase):
    pass


class Review(ReviewBase):
    id: int
    booking_id: int
    reviewer_id: int
    reviewed_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True


# Base Booking schema
class BookingBase(BaseModel):
    start_time: datetime
    end_time: datetime
    duration_type: BookingDuration = BookingDuration.HOURLY
    has_ev_charging: bool = False
    has_insurance: bool = False
    insurance_coverage: Optional[float] = None
    special_instructions: Optional[str] = None
    
    @validator('end_time')
    def end_time_after_start_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('End time must be after start time')
        return v


# Schema for creating a booking
class BookingCreate(BookingBase):
    parking_space_id: int


# Schema for updating a booking
class BookingUpdate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[BookingStatus] = None
    has_ev_charging: Optional[bool] = None
    has_insurance: Optional[bool] = None
    insurance_coverage: Optional[float] = None
    special_instructions: Optional[str] = None
    cancellation_reason: Optional[str] = None
    
    @validator('end_time')
    def end_time_after_start_time(cls, v, values, **kwargs):
        if v is not None and 'start_time' in values and values['start_time'] is not None and v <= values['start_time']:
            raise ValueError('End time must be after start time')
        return v


# Schema for reading a booking
class Booking(BookingBase):
    id: int
    status: BookingStatus
    
    # Pricing
    base_price: float
    ev_charging_fee: float
    insurance_fee: float
    service_fee: float
    total_price: float
    
    # Security
    security_access_code: Optional[str] = None
    security_camera_feed_url: Optional[str] = None
    
    # IDs
    user_id: int
    parking_space_id: int
    payment_id: Optional[int] = None
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


# Schema for detailed booking information
class BookingDetail(Booking):
    cancellation_reason: Optional[str] = None
    review: Optional[Review] = None
    
    class Config:
        orm_mode = True


# Schema for booking list
class BookingList(BaseModel):
    total: int
    bookings: List[Booking]
    
    class Config:
        orm_mode = True