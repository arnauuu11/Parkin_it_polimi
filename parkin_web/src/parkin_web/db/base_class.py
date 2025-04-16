# src/parkin_web/db/base_class.py
import datetime
from typing import Any

from sqlalchemy import Column, DateTime
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    id: Any
    __name__: str
    
    # Create 'tablename' automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    
    # Add created_at and updated_at for all models
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)