cat > src/parkin_web/crud/payment.py << 'EOF'
# src/parkin_web/crud/payment.py
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from src.parkin_web.crud.base import CRUDBase
from src.parkin_web.models.payment import Payment, PaymentStatus
from src.parkin_web.schemas.payment import PaymentCreate, PaymentUpdate


class CRUDPayment(CRUDBase[Payment, PaymentCreate, PaymentUpdate]):
    def create_with_booking(
        self, db: Session, *, obj_in: PaymentCreate, booking_id: int
    ) -> Payment:
        """
        Create a new payment for a booking.
        
        Args:
            db: Database session
            obj_in: Schema containing the data to create the payment
            booking_id: ID of the booking
            
        Returns:
            The created payment instance
        """
        obj_in_data = jsonable_encoder(obj_in)
        
        # Calculate host payout amount (70% of payment amount)
        host_payout_amount = obj_in.amount * 0.7
        
        db_obj = Payment(
            **obj_in_data,
            booking_id=booking_id,
            status=PaymentStatus.COMPLETED,  # Assume payment is completed for simplicity
            payment_date=datetime.utcnow(),
            payment_processor="stripe",  # Mock payment processor
            host_payout_amount=host_payout_amount,
            host_payout_status="pending",
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_user_payments(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Payment]:
        """
        Get payments made by a user.
        
        Args:
            db: Database session
            user_id: ID of the user
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of payment instances
        """
        from src.parkin_web.models.booking import Booking
        
        return (
            db.query(Payment)
            .join(Booking, Payment.booking_id == Booking.id)
            .filter(Booking.user_id == user_id)
            .order_by(Payment.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def refund(
        self, db: Session, *, id: int, refund_amount: float, refund_reason: str = ""
    ) -> Payment:
        """
        Process a refund.
        
        Args:
            db: Database session
            id: ID of the payment
            refund_amount: Amount to refund
            refund_reason: Reason for the refund
            
        Returns:
            The updated payment instance
        """
        payment = db.query(Payment).filter(Payment.id == id).first()
        if payment:
            # In a real-world application, you would integrate with a payment provider here
            # For now, we'll simulate a successful refund
            
            payment.refund_amount = refund_amount
            payment.refund_reason = refund_reason
            payment.refund_date = datetime.utcnow()
            
            # Update status based on refund amount
            if refund_amount >= payment.amount:
                payment.status = PaymentStatus.REFUNDED
            else:
                payment.status = PaymentStatus.PARTIALLY_REFUNDED
            
            # Update host payout
            if payment.host_payout_status == "pending":
                # If payout hasn't been processed yet, adjust it
                payment.host_payout_amount -= refund_amount
                if payment.host_payout_amount <= 0:
                    payment.host_payout_status = "canceled"
                    payment.host_payout_amount = 0
            else:
                # If payout has been processed, a separate clawback would be needed
                # This is simplified for the example
                pass
            
            db.add(payment)
            db.commit()
            db.refresh(payment)
        return payment
    
    def process_host_payout(
        self, db: Session, *, id: int
    ) -> Payment:
        """
        Process host payout.
        
        Args:
            db: Database session
            id: ID of the payment
            
        Returns:
            The updated payment instance
        """
        payment = db.query(Payment).filter(Payment.id == id).first()
        if payment and payment.host_payout_status == "pending":
            # In a real-world application, you would integrate with a payment provider here
            # For now, we'll simulate a successful payout
            
            payment.host_payout_date = datetime.utcnow()
            payment.host_payout_status = "completed"
            
            db.add(payment)
            db.commit()
            db.refresh(payment)
        return payment


payment = CRUDPayment(Payment)
EOF