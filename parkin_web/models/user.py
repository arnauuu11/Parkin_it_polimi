cat > src/parkin_web/models/user.py << 'EOF'
# src/parkin_web/models/user.py
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, Enum, DateTime
from sqlalchemy.orm import relationship

from src.parkin_web.db.base_class import Base


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # Profile information
    first_name = Column(String)
    last_name = Column(String)
    phone_number = Column(String)
    profile_image = Column(String)
    bio = Column(Text)
    
    # User type
    user_type = Column(String, default="driver")  # driver, host, both
    
    # Driver-specific information
    driving_license = Column(String)
    vehicle_model = Column(String)
    vehicle_plate = Column(String)
    
    # Host-specific information
    bank_account = Column(String)
    tax_id = Column(String)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    
    # Ratings
    rating = Column(Float, default=0.0)
    total_ratings = Column(Integer, default=0)
    
    # Relationships
    parking_spaces = relationship("ParkingSpace", back_populates="owner")
    bookings = relationship("Booking", back_populates="user")
    reviews_given = relationship("Review", foreign_keys="[Review.reviewer_id]", back_populates="reviewer")
    reviews_received = relationship("Review", foreign_keys="[Review.reviewed_id]", back_populates="reviewed")
EOF