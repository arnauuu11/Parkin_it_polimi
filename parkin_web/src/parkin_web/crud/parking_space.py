# src/parkin_web/crud/parking_space.py
from typing import List, Optional, Dict, Any, Union

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from fastapi.encoders import jsonable_encoder

from src.parkin_web.crud.base import CRUDBase
from src.parkin_web.models.parking_space import ParkingSpace, ParkingSpaceImage, AvailabilitySchedule
from src.parkin_web.schemas.parking_space import ParkingSpaceCreate, ParkingSpaceUpdate


class CRUDParkingSpace(CRUDBase[ParkingSpace, ParkingSpaceCreate, ParkingSpaceUpdate]):
    def create_with_owner(
        self, db: Session, *, obj_in: ParkingSpaceCreate, owner_id: int
    ) -> ParkingSpace:
        """
        Create a new parking space with an owner.
        
        Args:
            db: Database session
            obj_in: Schema containing the data to create the parking space
            owner_id: ID of the owner
            
        Returns:
            The created parking space instance
        """
        obj_in_data = jsonable_encoder(obj_in, exclude={"availability_schedules"})
        db_obj = ParkingSpace(**obj_in_data, owner_id=owner_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Create availability schedules if provided
        if obj_in.availability_schedules:
            for schedule in obj_in.availability_schedules:
                db_schedule = AvailabilitySchedule(
                    **jsonable_encoder(schedule),
                    parking_space_id=db_obj.id
                )
                db.add(db_schedule)
            db.commit()
        
        return db_obj
    
    def get_multi_by_owner(
        self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[ParkingSpace]:
        """
        Get multiple parking spaces by owner ID.
        
        Args:
            db: Database session
            owner_id: ID of the owner
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of parking space instances
        """
        return (
            db.query(ParkingSpace)
            .filter(ParkingSpace.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def search(
        self,
        db: Session,
        *,
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
        limit: int = 100
    ) -> List[ParkingSpace]:
        """
        Search for parking spaces with filters.
        
        Args:
            db: Database session
            latitude: Latitude for location-based search
            longitude: Longitude for location-based search
            city: City filter
            start_time: Start time for availability filter
            end_time: End time for availability filter
            has_security_camera: Security camera filter
            has_ev_charging: EV charging filter
            has_covered_parking: Covered parking filter
            min_price: Minimum hourly rate filter
            max_price: Maximum hourly rate filter
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of parking space instances
        """
        query = db.query(ParkingSpace).filter(ParkingSpace.is_active == True)
        
        # Apply filters
        if city:
            query = query.filter(ParkingSpace.city.ilike(f"%{city}%"))
        
        if has_security_camera is not None:
            query = query.filter(ParkingSpace.has_security_camera == has_security_camera)
            
        if has_ev_charging is not None:
            query = query.filter(ParkingSpace.has_ev_charging == has_ev_charging)
            
        if has_covered_parking is not None:
            query = query.filter(ParkingSpace.has_covered_parking == has_covered_parking)
            
        if min_price is not None:
            query = query.filter(ParkingSpace.hourly_rate >= min_price)
            
        if max_price is not None:
            query = query.filter(ParkingSpace.hourly_rate <= max_price)
        
        # If latitude and longitude are provided, order by distance
        # This is a simplified approach - in production you'd use PostGIS or a similar spatial extension
        if latitude is not None and longitude is not None:
            # Calculate distance using Euclidean distance (simplified)
            # In production, you would use a proper geospatial function
            distance = func.sqrt(
                func.pow(ParkingSpace.latitude - latitude, 2) +
                func.pow(ParkingSpace.longitude - longitude, 2)
            )
            query = query.order_by(distance)
        
        # Apply availability filters if start_time and end_time are provided
        # This is a simplified approach - in production you'd check for overlapping bookings
        if start_time and end_time:
            # Here you would join with availability schedules and check time ranges
            pass
        
        return query.offset(skip).limit(limit).all()
    
    def increment_views(self, db: Session, *, id: int) -> None:
        """
        Increment the views count for a parking space.
        
        Args:
            db: Database session
            id: ID of the parking space
        """
        parking_space = db.query(ParkingSpace).filter(ParkingSpace.id == id).first()
        if parking_space:
            parking_space.views_count += 1
            db.add(parking_space)
            db.commit()
    
    def increment_bookings(self, db: Session, *, id: int) -> None:
        """
        Increment the bookings count for a parking space.
        
        Args:
            db: Database session
            id: ID of the parking space
        """
        parking_space = db.query(ParkingSpace).filter(ParkingSpace.id == id).first()
        if parking_space:
            parking_space.bookings_count += 1
            db.add(parking_space)
            db.commit()
    
    def update_rating(self, db: Session, *, id: int, rating: int) -> None:
        """
        Update the average rating for a parking space.
        
        Args:
            db: Database session
            id: ID of the parking space
            rating: New rating to add (1-5)
        """
        parking_space = db.query(ParkingSpace).filter(ParkingSpace.id == id).first()
        if parking_space:
            # Update the average rating
            total_ratings = parking_space.reviews_count
            current_average = parking_space.average_rating
            
            new_total = total_ratings + 1
            new_average = ((current_average * total_ratings) + rating) / new_total
            
            parking_space.reviews_count = new_total
            parking_space.average_rating = new_average
            
            db.add(parking_space)
            db.commit()


class CRUDParkingSpaceImage(CRUDBase[ParkingSpaceImage, Any, Any]):
    def create_with_parking_space(
        self, db: Session, *, obj_in: Any, parking_space_id: int
    ) -> ParkingSpaceImage:
        """
        Create a new parking space image.
        
        Args:
            db: Database session
            obj_in: Schema containing the data to create the image
            parking_space_id: ID of the parking space
            
        Returns:
            The created image instance
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = ParkingSpaceImage(**obj_in_data, parking_space_id=parking_space_id)
        
        # If this is marked as the main image, update the parking space's main_image field
        if obj_in.is_main:
            parking_space = db.query(ParkingSpace).filter(ParkingSpace.id == parking_space_id).first()
            if parking_space:
                parking_space.main_image = obj_in.url
                db.add(parking_space)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_parking_space(
        self, db: Session, *, parking_space_id: int
    ) -> List[ParkingSpaceImage]:
        """
        Get images for a parking space.
        
        Args:
            db: Database session
            parking_space_id: ID of the parking space
            
        Returns:
            List of image instances
        """
        return db.query(ParkingSpaceImage).filter(
            ParkingSpaceImage.parking_space_id == parking_space_id
        ).all()


class CRUDAvailabilitySchedule(CRUDBase[AvailabilitySchedule, Any, Any]):
    def create_with_parking_space(
        self, db: Session, *, obj_in: Any, parking_space_id: int
    ) -> AvailabilitySchedule:
        """
        Create a new availability schedule.
        
        Args:
            db: Database session
            obj_in: Schema containing the data to create the schedule
            parking_space_id: ID of the parking space
            
        Returns:
            The created schedule instance
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = AvailabilitySchedule(**obj_in_data, parking_space_id=parking_space_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_parking_space(
        self, db: Session, *, parking_space_id: int
    ) -> List[AvailabilitySchedule]:
        """
        Get availability schedules for a parking space.
        
        Args:
            db: Database session
            parking_space_id: ID of the parking space
            
        Returns:
            List of schedule instances
        """
        return db.query(AvailabilitySchedule).filter(
            AvailabilitySchedule.parking_space_id == parking_space_id
        ).all()


parking_space = CRUDParkingSpace(ParkingSpace)
parking_space_image = CRUDParkingSpaceImage(ParkingSpaceImage)
availability_schedule = CRUDAvailabilitySchedule(AvailabilitySchedule)

