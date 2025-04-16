# src/parkin_web/models/booking.py
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, Enum, DateTime
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from src.parkin_web.db.base_class import Base


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELED = "canceled"
    COMPLETED = "completed"
    REJECTED = "rejected"


class BookingDuration(str, enum.Enum):
    HOURLY = "hourly"
    DAILY = "daily"
    MONTHLY = "monthly"


class Booking(Base):
    id = Column(Integer, primary_key=True, index=True)
    
    # Booking details
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    duration_type = Column(Enum(BookingDuration), default=BookingDuration.HOURLY)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING)
    
    # Pricing
    base_price = Column(Float, nullable=False)
    ev_charging_fee = Column(Float, default=0.0)
    insurance_fee = Column(Float, default=0.0)
    service_fee = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    
    # Booking features
    has_ev_charging = Column(Boolean, default=False)
    has_insurance = Column(Boolean, default=False)
    insurance_coverage = Column(Float, default=0.0)  # Coverage amount
    
    # Instructions and notes
    special_instructions = Column(Text)
    cancellation_reason = Column(Text)
    
    # Security
    security_access_code = Column(String)
    security_camera_feed_url = Column(String)
    
    # Relationships
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User", back_populates="bookings")
    
    parking_space_id = Column(Integer, ForeignKey("parkingspace.id"), nullable=False)
    parking_space = relationship("ParkingSpace", back_populates="bookings")
    
    payment_id = Column(Integer, ForeignKey("payment.id"))
    payment = relationship("Payment", back_populates="booking")
    
    review = relationship("Review", back_populates="booking", uselist=False)


class Review(Base):
    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    comment = Column(Text)
    
    # Relationships
    booking_id = Column(Integer, ForeignKey("booking.id"), nullable=False)
    booking = relationship("Booking", back_populates="review")
    
    reviewer_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    reviewer = relationship("User", foreign_keys=[reviewer_id], back_populates="reviews_given")
    
    reviewed_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    reviewed = relationship("User", foreign_keys=[reviewed_id], back_populates="reviews_received")