from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base
import enum

class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class TravelType(str, enum.Enum):
    FLIGHT = "flight"
    TRAIN = "train"
    HOTEL = "hotel"
    PACKAGE = "package"

class Booking(Base):
    """Model for travel bookings."""
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String(12), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    travel_type = Column(Enum(TravelType), nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    
    # Travel details (stored as JSON for flexibility)
    travel_details = Column(JSON, nullable=False)
    
    # Payment information
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    payment_status = Column(String(20), default="pending", nullable=False)
    payment_reference = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    departure_date = Column(DateTime(timezone=True), nullable=True)
    return_date = Column(DateTime(timezone=True), nullable=True)
    
    # Cancellation
    is_cancellable = Column(Boolean, default=True)
    cancellation_policy = Column(JSON, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="bookings")
    passengers = relationship("Passenger", back_populates="booking")
    
    def __repr__(self):
        return f"<Booking {self.reference} - {self.travel_type} - {self.status}>"

class Passenger(Base):
    """Model for passenger information."""
    __tablename__ = "passengers"
    
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    passport_number = Column(String(20), nullable=True)
    nationality = Column(String(2), nullable=True)  # ISO 3166-1 alpha-2
    
    # Seat/berth preferences
    seat_preference = Column(String(20), nullable=True)
    meal_preference = Column(String(20), nullable=True)
    
    # Special requirements
    special_requests = Column(JSON, nullable=True)
    
    # Relationships
    booking = relationship("Booking", back_populates="passengers")
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<Passenger {self.full_name} - Booking {self.booking_id}>"
