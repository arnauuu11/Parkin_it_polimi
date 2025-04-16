# src/parkin_web/models/parking_space.py
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
import enum

from src.parkin_web.db.base_class import Base


class ParkingType(str, enum.Enum):
    DRIVEWAY = "driveway"
    GARAGE = "garage"
    LOT = "lot"
    STREET = "street"
    UNDERGROUND = "underground"


class ParkingSpace(Base):
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text)
    
    # Location details
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    zip_code = Column(String, nullable=False)
    country = Column(String, nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Parking details
    parking_type = Column(Enum(ParkingType), default=ParkingType.DRIVEWAY)
    hourly_rate = Column(Float, nullable=False)
    daily_rate = Column(Float)
    monthly_rate = Column(Float)
    width = Column(Float)  # in feet
    length = Column(Float)  # in feet
    height = Column(Float)  # in feet (for garages)
    
    # Availability
    is_available = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    instant_booking = Column(Boolean, default=False)
    
    # Special features
    has_security_camera = Column(Boolean, default=False)
    has_ev_charging = Column(Boolean, default=False)
    ev_charging_rate = Column(Float)  # per kWh
    has_covered_parking = Column(Boolean, default=False)
    has_gate_access = Column(Boolean, default=False)
    access_instructions = Column(Text)
    
    # Images
    main_image = Column(String)
    
    # Relationships
    owner_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    owner = relationship("User", back_populates="parking_spaces")
    bookings = relationship("Booking", back_populates="parking_space")
    images = relationship("ParkingSpaceImage", back_populates="parking_space")
    availability_schedules = relationship("AvailabilitySchedule", back_populates="parking_space")
    
    # Analytics
    views_count = Column(Integer, default=0)
    bookings_count = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    reviews_count = Column(Integer, default=0)


class ParkingSpaceImage(Base):
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    description = Column(String)
    is_main = Column(Boolean, default=False)
    
    parking_space_id = Column(Integer, ForeignKey("parkingspace.id"), nullable=False)
    parking_space = relationship("ParkingSpace", back_populates="images")


class AvailabilitySchedule(Base):
    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(Integer)  # 0-6 for Monday-Sunday
    start_time = Column(String)  # Format: HH:MM
    end_time = Column(String)  # Format: HH:MM
    is_available = Column(Boolean, default=True)
    
    parking_space_id = Column(Integer, ForeignKey("parkingspace.id"), nullable=False)
    parking_space = relationship("ParkingSpace", back_populates="availability_schedules")