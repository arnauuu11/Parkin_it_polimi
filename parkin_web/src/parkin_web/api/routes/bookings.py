# src/parkin_web/api/routes/bookings.py (continued)
@router.put("/{id}/confirm", response_model=schemas.Booking)
def confirm_booking(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Confirm booking.
    """
    booking = crud.booking.get(db=db, id=id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )
    
    # Check if user is authorized to confirm this booking
    parking_space = crud.parking_space.get(db=db, id=booking.parking_space_id)
    if parking_space.owner_id != current_user.id and not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to confirm this booking",
        )
    
    # Check if booking is pending
    if booking.status != schemas.BookingStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot confirm a booking with status {booking.status}",
        )
    
    booking = crud.booking.confirm(db=db, id=id)
    return booking


@router.put("/{id}/complete", response_model=schemas.Booking)
def complete_booking(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Mark booking as completed.
    """
    booking = crud.booking.get(db=db, id=id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )
    
    # Check if user is authorized to complete this booking
    parking_space = crud.parking_space.get(db=db, id=booking.parking_space_id)
    if booking.user_id != current_user.id and parking_space.owner_id != current_user.id and not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to complete this booking",
        )
    
    # Check if booking is confirmed
    if booking.status != schemas.BookingStatus.CONFIRMED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot complete a booking with status {booking.status}",
        )
    
    booking = crud.booking.complete(db=db, id=id)
    return booking


@router.post("/{id}/review", response_model=schemas.Review)
def create_review(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    review_in: schemas.ReviewCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create review for a booking.
    """
    booking = crud.booking.get(db=db, id=id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )
    
    # Check if user is authorized to review this booking
    if booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to review this booking",
        )
    
    # Check if booking is completed
    if booking.status != schemas.BookingStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can only review completed bookings",
        )
    
    # Check if booking already has a review
    if crud.review.get_by_booking(db=db, booking_id=id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This booking already has a review",
        )
    
    # Get the parking space owner
    parking_space = crud.parking_space.get(db=db, id=booking.parking_space_id)
    
    review = crud.review.create_with_details(
        db=db,
        obj_in=review_in,
        booking_id=id,
        reviewer_id=current_user.id,
        reviewed_id=parking_space.owner_id,
    )
    
    # Update parking space rating
    crud.parking_space.update_rating(db=db, id=booking.parking_space_id, rating=review.rating)
    
    # Update host rating
    crud.user.update_rating(db=db, id=parking_space.owner_id, rating=review.rating)
    
    return review