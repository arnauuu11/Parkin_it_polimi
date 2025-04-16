# src/parkin_web/api/routes/payments.py
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.parkin_web import crud, models, schemas
from src.parkin_web.api import deps
from src.parkin_web.core.config import settings

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/", response_model=schemas.Payment)
def create_payment(
    *,
    db: Session = Depends(deps.get_db),
    payment_in: schemas.PaymentCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new payment.
    """
    # Check if booking exists and belongs to the current user
    booking = crud.booking.get(db=db, id=payment_in.booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )
    
    if booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to make a payment for this booking",
        )
    
    # Check if booking already has a payment
    if booking.payment_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This booking already has a payment",
        )
    
    # Check if booking is in a payable state
    if booking.status not in [schemas.BookingStatus.PENDING, schemas.BookingStatus.CONFIRMED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot make payment for booking with status {booking.status}",
        )
    
    # Process payment (this would integrate with a payment provider in production)
    payment = crud.payment.create_with_booking(
        db=db,
        obj_in=payment_in,
        booking_id=payment_in.booking_id,
    )
    
    # Update booking with payment ID
    booking.payment_id = payment.id
    db.add(booking)
    db.commit()
    
    # If payment is successful, confirm the booking if it's pending
    if payment.status == schemas.PaymentStatus.COMPLETED and booking.status == schemas.BookingStatus.PENDING:
        booking = crud.booking.confirm(db=db, id=booking.id)
    
    return payment


@router.get("/", response_model=List[schemas.Payment])
def get_user_payments(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 10,
) -> Any:
    """
    Get current user's payments.
    """
    return crud.payment.get_user_payments(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )


@router.get("/{id}", response_model=schemas.Payment)
def get_payment(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get payment by ID.
    """
    payment = crud.payment.get(db=db, id=id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )
    
    # Check if user is authorized to view this payment
    booking = crud.booking.get(db=db, id=payment.booking_id)
    parking_space = crud.parking_space.get(db=db, id=booking.parking_space_id)
    
    if booking.user_id != current_user.id and parking_space.owner_id != current_user.id and not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this payment",
        )
    
    return payment


@router.post("/{id}/refund", response_model=schemas.Payment)
def refund_payment(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    refund_amount: float,
    refund_reason: str = "",
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Refund a payment.
    """
    payment = crud.payment.get(db=db, id=id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )
    
    # Check if user is authorized to refund this payment
    booking = crud.booking.get(db=db, id=payment.booking_id)
    parking_space = crud.parking_space.get(db=db, id=booking.parking_space_id)
    
    if parking_space.owner_id != current_user.id and not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to refund this payment",
        )
    
    # Check if refund amount is valid
    if refund_amount <= 0 or refund_amount > payment.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid refund amount",
        )
    
    # Check if payment can be refunded
    if payment.status not in [schemas.PaymentStatus.COMPLETED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot refund a payment with status {payment.status}",
        )
    
    # Check if booking was canceled or completed long ago
    # This would typically involve checking dates in a real implementation
    
    # Process refund (this would integrate with a payment provider in production)
    payment = crud.payment.refund(
        db=db,
        id=id,
        refund_amount=refund_amount,
        refund_reason=refund_reason,
    )
    
    # If full refund, cancel the booking if it's not already canceled or completed
    if payment.status == schemas.PaymentStatus.REFUNDED and booking.status == schemas.BookingStatus.CONFIRMED:
        booking = crud.booking.cancel(db=db, id=booking.id, cancellation_reason=f"Refunded: {refund_reason}")
    
    return payment


# Admin endpoint for managing payments
@router.put("/{id}", response_model=schemas.Payment)
def update_payment(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    payment_in: schemas.PaymentUpdate,
    current_user: models.User = Depends(deps.get_current_superuser),
) -> Any:
    """
    Update payment details (admin only).
    """
    payment = crud.payment.get(db=db, id=id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )
    
    payment = crud.payment.update(db=db, db_obj=payment, obj_in=payment_in)
    return payment