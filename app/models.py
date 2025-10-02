from datetime import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key=True, index=True)
	username = Column(String(50), unique=True, nullable=False, index=True)
	hashed_password = Column(String(255), nullable=False)
	is_active = Column(Boolean, nullable=False, default=True)
	is_admin = Column(Boolean, nullable=False, default=False)
	created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class Patient(Base):
	__tablename__ = "patients"

	id = Column(Integer, primary_key=True, index=True)
	first_name = Column(String(100), nullable=False)
	last_name = Column(String(100), nullable=False)
	dob = Column(Date, nullable=True)
	phone = Column(String(30), nullable=True)
	email = Column(String(255), nullable=True)
	notes = Column(Text, nullable=True)

	appointments = relationship(
		"Appointment",
		back_populates="patient",
		cascade="all, delete-orphan",
	)


class Doctor(Base):
	__tablename__ = "doctors"

	id = Column(Integer, primary_key=True, index=True)
	first_name = Column(String(100), nullable=False)
	last_name = Column(String(100), nullable=False)
	specialty = Column(String(120), nullable=True)
	phone = Column(String(30), nullable=True)
	email = Column(String(255), nullable=True)

	appointments = relationship(
		"Appointment",
		back_populates="doctor",
		cascade="all, delete-orphan",
	)


class Appointment(Base):
	__tablename__ = "appointments"

	id = Column(Integer, primary_key=True, index=True)
	patient_id = Column(
		Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True
	)
	doctor_id = Column(
		Integer, ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False, index=True
	)
	start_time = Column(DateTime, nullable=False, index=True)
	end_time = Column(DateTime, nullable=False, index=True)
	reason = Column(String(255), nullable=True)
	status = Column(String(30), nullable=False, default="scheduled")

	patient = relationship("Patient", back_populates="appointments")
	doctor = relationship("Doctor", back_populates="appointments")
