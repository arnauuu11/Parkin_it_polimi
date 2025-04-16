# src/parkin_web/schemas/payment.py
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    BANK_TRANSFER = "bank_transfer"
    CRYPTO = "crypto"


# Base Payment schema
class PaymentBase(BaseModel):
    amount: float
    currency: str = "USD"
    payment_method: PaymentMethod
    
    # Payment breakdown
    base_amount: float
    service_fee: float
    insurance_fee: float = 0.0
    ev_charging_fee: float = 0.0
    tax_amount: float = 0.0


# Schema for creating a payment
class PaymentCreate(PaymentBase):
    booking_id: int


# Schema for updating a payment
class PaymentUpdate(BaseModel):
    status: Optional[PaymentStatus] = None
    transaction_id: Optional[str] = None
    payment_date: Optional[datetime] = None
    refund_date: Optional[datetime] = None
    refund_amount: Optional[float] = None
    refund_reason: Optional[str] = None
    receipt_url: Optional[str] = None
    host_payout_amount: Optional[float] = None
    host_payout_status: Optional[str] = None
    host_payout_date: Optional[datetime] = None


# Schema for reading a payment
class Payment(PaymentBase):
    id: int
    status: PaymentStatus
    transaction_id: Optional[str] = None
    
    # Payment dates
    payment_date: Optional[datetime] = None
    refund_date: Optional[datetime] = None
    
    # Refund details
    refund_amount: Optional[float] = None
    refund_reason: Optional[str] = None
    
    # Payment processor details
    payment_processor: Optional[str] = None
    payment_processor_fee: float = 0.0
    
    # Receipt information
    receipt_url: Optional[str] = None
    
    # Host payout
    host_payout_amount: Optional[float] = None
    host_payout_status: Optional[str] = None
    host_payout_date: Optional[datetime] = None
    
    booking_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True