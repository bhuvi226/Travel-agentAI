from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from app import schemas, models
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.agents.agent_manager import agent_manager
from app.schemas.agent import AgentRequest

router = APIRouter()

@router.post("/", response_model=schemas.Booking)
async def create_booking(
    booking_in: schemas.BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Create a new booking."""
    # Generate a unique booking reference
    booking_ref = f"BK{uuid.uuid4().hex[:8].upper()}"
    
    # Create the booking in the database
    db_booking = models.Booking(
        reference=booking_ref,
        user_id=current_user.id,
        travel_type=booking_in.travel_type,
        status="pending",
        travel_details=booking_in.travel_details.dict(),
        amount=booking_in.amount,
        currency=booking_in.currency,
        departure_date=booking_in.departure_date,
        return_date=booking_in.return_date,
        is_cancellable=booking_in.is_cancellable,
        cancellation_policy=booking_in.cancellation_policy
    )
    
    db.add(db_booking)
    await db.commit()
    await db.refresh(db_booking)
    
    # Add passengers if provided
    if booking_in.passengers:
        for passenger_in in booking_in.passengers:
            db_passenger = models.Passenger(
                booking_id=db_booking.id,
                **passenger_in.dict()
            )
            db.add(db_passenger)
        
        await db.commit()
        await db.refresh(db_booking)
    
    # Notify the user about the booking
    await agent_manager.process(
        agent_name="notification",
        input_data={
            "query": "send_notification",
            "context": {
                "user_id": current_user.id,
                "title": "Booking Confirmed",
                "message": f"Your booking {booking_ref} has been created successfully.",
                "notification_type": "email"
            }
        }
    )
    
    return db_booking

@router.get("/{booking_id}", response_model=schemas.Booking)
async def get_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get a booking by ID."""
    from sqlalchemy import select
    
    result = await db.execute(
        select(models.Booking)
        .where(models.Booking.id == booking_id)
        .where(models.Booking.user_id == current_user.id)
    )
    
    booking = result.scalars().first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    return booking

@router.get("/", response_model=List[schemas.Booking])
async def list_bookings(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    travel_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """List all bookings for the current user with optional filters."""
    from sqlalchemy import select, and_
    
    query = select(models.Booking).where(
        models.Booking.user_id == current_user.id
    )
    
    # Apply filters
    if status:
        query = query.where(models.Booking.status == status)
    
    if travel_type:
        query = query.where(models.Booking.travel_type == travel_type)
    
    if start_date:
        query = query.where(models.Booking.departure_date >= start_date)
    
    if end_date:
        query = query.where(models.Booking.departure_date <= end_date)
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/{booking_id}/cancel", response_model=schemas.Booking)
async def cancel_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Cancel a booking."""
    from sqlalchemy import select, update
    
    # Get the booking
    result = await db.execute(
        select(models.Booking)
        .where(models.Booking.id == booking_id)
        .where(models.Booking.user_id == current_user.id)
    )
    booking = result.scalars().first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    if booking.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking is already cancelled"
        )
    
    if not booking.is_cancellable:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This booking cannot be cancelled"
        )
    
    # Update booking status
    booking.status = "cancelled"
    booking.updated_at = datetime.utcnow()
    
    # Process refund if applicable
    if booking.payment_status == "completed":
        # In a real app, this would call the payment service
        refund_result = await agent_manager.process(
            agent_name="payment",
            input_data={
                "query": "refund_payment",
                "context": {
                    "transaction_id": booking.payment_reference,
                    "amount": booking.amount
                }
            }
        )
        
        if refund_result.get("status") == "success":
            booking.payment_status = "refunded"
        else:
            # Handle refund failure
            pass
    
    await db.commit()
    await db.refresh(booking)
    
    # Notify the user
    await agent_manager.process(
        agent_name="notification",
        input_data={
            "query": "send_notification",
            "context": {
                "user_id": current_user.id,
                "title": "Booking Cancelled",
                "message": f"Your booking {booking.reference} has been cancelled.",
                "notification_type": "email"
            }
        }
    )
    
    return booking
