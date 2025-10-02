from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status, Cookie, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..auth.security import decode_access_token
from ..core.config import settings
from ..database import get_db
from ..models import Appointment, Doctor, Patient


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def require_user(access_token: Optional[str] = Cookie(default=None, alias=settings.cookie_name)) -> str:
	username = decode_access_token(access_token) if access_token else None
	if not username:
		raise HTTPException(status_code=status.HTTP_302_FOUND, detail="Redirect", headers={"Location": "/login"})
	return username


@router.get("/", response_class=HTMLResponse)
def list_appointments(request: Request, db: Session = Depends(get_db), username: str = Depends(require_user)):
	appointments = (
		db.query(Appointment)
		.order_by(Appointment.start_time.desc())
		.all()
	)
	return templates.TemplateResponse(
		"appointments/list.html",
		{"request": request, "appointments": appointments, "username": username},
	)


@router.get("/new", response_class=HTMLResponse)
def new_appointment(request: Request, db: Session = Depends(get_db), username: str = Depends(require_user)):
	patients = db.query(Patient).order_by(Patient.last_name, Patient.first_name).all()
	doctors = db.query(Doctor).order_by(Doctor.last_name, Doctor.first_name).all()
	return templates.TemplateResponse(
		"appointments/form.html",
		{"request": request, "appointment": None, "patients": patients, "doctors": doctors, "username": username},
	)


@router.post("/new")
def create_appointment(
	db: Session = Depends(get_db),
	username: str = Depends(require_user),
	patient_id: int = Form(...),
	doctor_id: int = Form(...),
	start_time: str = Form(...),
	end_time: str = Form(...),
	reason: Optional[str] = Form(None),
):
	start_dt = datetime.fromisoformat(start_time)
	end_dt = datetime.fromisoformat(end_time)
	if end_dt <= start_dt:
		raise HTTPException(status_code=400, detail="End time must be after start time")
	appointment = Appointment(
		patient_id=patient_id,
		doctor_id=doctor_id,
		start_time=start_dt,
		end_time=end_dt,
		reason=(reason or "").strip() or None,
	)
	db.add(appointment)
	db.commit()
	return RedirectResponse(url="/appointments", status_code=status.HTTP_302_FOUND)


@router.get("/{appointment_id}", response_class=HTMLResponse)
def edit_appointment(appointment_id: int, request: Request, db: Session = Depends(get_db), username: str = Depends(require_user)):
	appointment = db.get(Appointment, appointment_id)
	if not appointment:
		raise HTTPException(status_code=404, detail="Appointment not found")
	patients = db.query(Patient).order_by(Patient.last_name, Patient.first_name).all()
	doctors = db.query(Doctor).order_by(Doctor.last_name, Doctor.first_name).all()
	return templates.TemplateResponse(
		"appointments/form.html",
		{"request": request, "appointment": appointment, "patients": patients, "doctors": doctors, "username": username},
	)


@router.post("/{appointment_id}")
def update_appointment(
	appointment_id: int,
	db: Session = Depends(get_db),
	username: str = Depends(require_user),
	patient_id: int = Form(...),
	doctor_id: int = Form(...),
	start_time: str = Form(...),
	end_time: str = Form(...),
	reason: Optional[str] = Form(None),
):
	appointment = db.get(Appointment, appointment_id)
	if not appointment:
		raise HTTPException(status_code=404, detail="Appointment not found")
	start_dt = datetime.fromisoformat(start_time)
	end_dt = datetime.fromisoformat(end_time)
	if end_dt <= start_dt:
		raise HTTPException(status_code=400, detail="End time must be after start time")
	appointment.patient_id = patient_id
	appointment.doctor_id = doctor_id
	appointment.start_time = start_dt
	appointment.end_time = end_dt
	appointment.reason = (reason or "").strip() or None
	db.add(appointment)
	db.commit()
	return RedirectResponse(url="/appointments", status_code=status.HTTP_302_FOUND)


@router.post("/{appointment_id}/delete")
def delete_appointment(appointment_id: int, db: Session = Depends(get_db), username: str = Depends(require_user)):
	appointment = db.get(Appointment, appointment_id)
	if not appointment:
		raise HTTPException(status_code=404, detail="Appointment not found")
	db.delete(appointment)
	db.commit()
	return RedirectResponse(url="/appointments", status_code=status.HTTP_302_FOUND)


@router.get("/schedule", response_class=HTMLResponse)
def schedule(
	request: Request,
	db: Session = Depends(get_db),
	username: str = Depends(require_user),
	doctor_id: Optional[int] = Query(None),
	start: Optional[str] = Query(None),
):
	doctors = db.query(Doctor).order_by(Doctor.last_name, Doctor.first_name).all()
	if start:
		start_dt = datetime.fromisoformat(start)
	else:
		start_dt = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
	end_dt = start_dt + timedelta(days=7)
	query = db.query(Appointment).filter(Appointment.start_time >= start_dt, Appointment.start_time < end_dt)
	if doctor_id:
		query = query.filter(Appointment.doctor_id == doctor_id)
	appointments = query.order_by(Appointment.start_time).all()
	return templates.TemplateResponse(
		"appointments/schedule.html",
		{
			"request": request,
			"appointments": appointments,
			"doctors": doctors,
			"selected_doctor_id": doctor_id,
			"week_start": start_dt,
			"week_end": end_dt,
			"username": username,
		},
	)
