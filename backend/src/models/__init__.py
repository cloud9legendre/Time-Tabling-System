from sqlalchemy import Column, Integer, String, Boolean, Date, Time, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base
import uuid

class Department(Base):
    __tablename__ = "departments"
    code = Column(String(10), primary_key=True)
    name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)

class Lab(Base):
    __tablename__ = "labs"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    department_code = Column(String(10), ForeignKey("departments.code"))
    capacity = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True) # Added to model

class Instructor(Base):
    __tablename__ = "instructors"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    department_code = Column(String(10), ForeignKey("departments.code")) 
    role = Column(String(20), default="INSTRUCTOR")
    password = Column(String(100), default="password123")
    
    # New Profile Fields
    university = Column(String(150), nullable=True)
    degree = Column(String(150), nullable=True)
    graduated_date = Column(Date, nullable=True)
    photo_url = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

class Module(Base):
    __tablename__ = "modules"
    code = Column(String(15), primary_key=True)
    title = Column(String(200), nullable=False)
    offering_dept = Column(String(10), ForeignKey("departments.code"))
    enrolled_count = Column(Integer, default=0)
    semester = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    series_id = Column(UUID(as_uuid=True), nullable=True)
    lab_id = Column(Integer, ForeignKey("labs.id"))
    module_code = Column(String(15), ForeignKey("modules.code"))
    booked_by_id = Column(Integer, ForeignKey("instructors.id"))
    booking_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    status = Column(String(20), default="PENDING")
    purpose = Column(String(20), default="CLASS")
    practical_name = Column(String(150), nullable=True)
    
    lab = relationship("Lab")
    instructor = relationship("Instructor", foreign_keys=[booked_by_id])
    module = relationship("Module")