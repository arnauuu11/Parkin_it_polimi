# src/parkin_web/crud/payment.py (continued)
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