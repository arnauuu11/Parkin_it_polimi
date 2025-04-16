# src/parkin_web/crud/booking.py
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from fastapi.encoders import jsonable_encoder

from src.parkin_web.crud.base import CRUDBase
from src.parkin_web.models.booking import Booking, Review, BookingStatus
from src.parkin_web.models.parking_space import ParkingSpace
from src.parkin_web.schemas.booking import BookingCreate, BookingUpdate


class CRUDBooking(CRUDBase[Booking, BookingCreate, BookingUpdate]):
    def create_with_details(
        self, db: Session, *, obj_in: BookingCreate, user_id: int, parking_space: ParkingSpace
    ) -> Booking:
        """
        Create a new booking with full details.
        
        Args:
            db: Database session
            obj_in: Schema containing the data to create the booking
            user_id: ID of the user making the booking
            parking_space: Parking space being booked
            
        Returns:
            The created booking instance
        """
        # Calculate pricing based on duration type
        duration = obj_in.end_time - obj_in.start_time
        hours = duration.total_seconds() / 3600
        days = hours / 24
        
        if obj_in.duration_type == "hourly":
            base_price = parking_space.hourly_rate * hours
        elif obj_in.duration_type == "daily":
            base_price = parking_space.daily_rate * days if parking_space.daily_rate else parking_space.hourly_rate * hours
        elif obj_in.duration_type == "monthly":
            base_price = parking_space.monthly_rate if parking_space.monthly_rate else parking_space.hourly_rate * hours
        
        # Calculate fees
        service_fee = base_price * 0.15  # 15% service fee
        ev_charging_fee = 0.0
        if obj_in.has_ev_charging and parking_space.has_ev_charging and parking_space.ev_charging_rate:
            ev_charging_fee = parking_space.ev_charging_rate * hours
        
        insurance_fee = 0.0
        if obj_in.has_insurance:
            # Calculate insurance fee based on coverage
            insurance_fee = 5.0  # Base insurance fee
            if obj_in.insurance_coverage and obj_in.insurance_coverage > 10000:
                insurance_fee = 10.0  # Higher coverage fee
        
        total_price = base_price + service_fee + ev_charging_fee + insurance_fee
        
        # Create booking object
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = Booking(
            **obj_in_data,
            user_id=user_id,
            base_price=base_price,
            service_fee=service_fee,
            ev_charging_fee=ev_charging_fee,
            insurance_fee=insurance_fee,
            total_price=total_price,
            status=BookingStatus.PENDING if not parking_space.instant_booking else BookingStatus.CONFIRMED,
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_user_bookings(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Booking]:
        """
        Get bookings made by a user.
        
        Args:
            db: Database session
            user_id: ID of the user
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of booking instances
        """
        return (
            db.query(Booking)
            .filter(Booking.user_id == user_id)
            .order_by(Booking.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_host_bookings(
        self, db: Session, *, host_id: int, skip: int = 0, limit: int = 100
    ) -> List[Booking]:
        """
        Get bookings for a host's parking spaces.
        
        Args:
            db: Database session
            host_id: ID of the host
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of booking instances
        """
        return (
            db.query(Booking)
            .join(ParkingSpace, Booking.parking_space_id == ParkingSpace.id)
            .filter(ParkingSpace.owner_id == host_id)
            .order_by(Booking.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def has_conflict(
        self, db: Session, *, parking_space_id: int, start_time: datetime, end_time: datetime, exclude_id: Optional[int] = None
    ) -> bool:
        """
        Check if there's a booking conflict for a parking space.
        
        Args:
            db: Database session
            parking_space_id: ID of the parking space
            start_time: Start time of the proposed booking
            end_time: End time of the proposed booking
            exclude_id: ID of booking to exclude from conflict check
            
        Returns:
            True if there's a conflict, False otherwise
        """
        query = (
            db.query(Booking)
            .filter(
                Booking.parking_space_id == parking_space_id,
                Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
                or_(
                    # New booking starts during an existing booking
                    and_(
                        Booking.start_time <= start_time,
                        Booking.end_time > start_time
                    ),
                    # New booking ends during an existing booking
                    and_(
                        Booking.start_time < end_time,
                        Booking.end_time >= end_time
                    ),
                    # New booking completely contains an existing booking
                    and_(
                        Booking.start_time >= start_time,
                        Booking.end_time <= end_time
                    )
                )
            )
        )
        
        if exclude_id:
            query = query.filter(Booking.id != exclude_id)
        
        return db.query(query.exists()).scalar()
    
    def confirm(self, db: Session, *, id: int) -> Booking:
        """
        Confirm a booking.
        
        Args:
            db: Database session
            id: ID of the booking
            
        Returns:
            The updated booking instance
        """
        booking = db.query(Booking).filter(Booking.id == id).first()
        if booking:
            booking.status = BookingStatus.CONFIRMED
            db.add(booking)
            db.commit()
            db.refresh(booking)
        return booking
    
    def cancel(self, db: Session, *, id: int, cancellation_reason: str = "") -> Booking:
        """
        Cancel a booking.
        
        Args:
            db: Database session
            id: ID of the booking
            cancellation_reason: Reason for cancellation
            
        Returns:
            The updated booking instance
        """
        booking = db.query(Booking).filter(Booking.id == id).first()
        if booking:
            booking.status = BookingStatus.CANCELED
            booking.cancellation_reason = cancellation_reason
            db.add(booking)
            db.commit()
            db.refresh(booking)
        return booking
    
    def complete(self, db: Session, *, id: int) -> Booking:
        """
        Mark a booking as completed.
        
        Args:
            db: Database session
            id: ID of the booking
            
        Returns:
            The updated booking instance
        """
        booking = db.query(Booking).filter(Booking.id == id).first()
        if booking:
            booking.status = BookingStatus.COMPLETED
            db.add(booking)
            db.commit()
            db.refresh(booking)
        return booking
    
    def reject(self, db: Session, *, id: int, rejection_reason: str = "") -> Booking:
        """
        Reject a booking.
        
        Args:
            db: Database session
            id: ID of the booking
            rejection_reason: Reason for rejection
            
        Returns:
            The updated booking instance
        """
        booking = db.query(Booking).filter(Booking.id == id).first()
        if booking:
            booking.status = BookingStatus.REJECTED
            booking.cancellation_reason = rejection_reason
            db.add(booking)
            db.commit()
            db.refresh(booking)
        return booking


class CRUDReview(CRUDBase[Review, Any, Any]):
    def create_with_details(
        self, db: Session, *, obj_in: Any, booking_id: int, reviewer_id: int, reviewed_id: int
    ) -> Review:
        """
        Create a new review.
        
        Args:
            db: Database session
            obj_in: Schema containing the data to create the review
            booking_id: ID of the booking
            reviewer_id: ID of the user writing the review
            reviewed_id: ID of the user being reviewed
            
        Returns:
            The created review instance
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = Review(
            **obj_in_data,
            booking_id=booking_id,
            reviewer_id=reviewer_id,
            reviewed_id=reviewed_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_booking(self, db: Session, *, booking_id: int) -> Optional[Review]:
        """
        Get a review by booking ID.
        
        Args:
            db: Database session
            booking_id: ID of the booking
            
        Returns:
            The review instance if found, None otherwise
        """
        return db.query(Review).filter(Review.booking_id == booking_id).first()
    
    def get_user_reviews(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Review]:
        """
        Get reviews for a user.
        
        Args:
            db: Database session
            user_id: ID of the user
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of review instances
        """
        return (
            db.query(Review)
            .filter(Review.reviewed_id == user_id)
            .order_by(Review.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )


booking = CRUDBooking(Booking)
review = CRUDReview(Review)