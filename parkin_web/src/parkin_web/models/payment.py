# src/parkin_web/models/payment.py
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, Enum, DateTime
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from src.parkin_web.db.base_class import Base


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class PaymentMethod(str, enum.Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    BANK_TRANSFER = "bank_transfer"
    CRYPTO = "crypto"


class Payment(Base):
    id = Column(Integer, primary_key=True, index=True)
    
    # Payment details
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_method = Column(Enum(PaymentMethod))
    transaction_id = Column(String)  # External payment provider transaction ID
    
    # Payment dates
    payment_date = Column(DateTime)
    refund_date = Column(DateTime)
    
    # Refund details
    refund_amount = Column(Float)
    refund_reason = Column(Text)
    
    # Payment breakdown
    base_amount = Column(Float, nullable=False)
    service_fee = Column(Float, nullable=False)
    insurance_fee = Column(Float, default=0.0)
    ev_charging_fee = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    
    # Payment processor details
    payment_processor = Column(String)  # e.g., "stripe", "paypal"
    payment_processor_fee = Column(Float, default=0.0)
    
    # Receipt information
    receipt_url = Column(String)
    
    # Host payout
    host_payout_amount = Column(Float)
    host_payout_status = Column(String)
    host_payout_date = Column(DateTime)
    
    # Relationships
    booking = relationship("Booking", back_populates="payment", uselist=False)