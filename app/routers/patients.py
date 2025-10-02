from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response, status, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..auth.security import decode_access_token
from ..core.config import settings
from ..database import get_db
from ..models import Patient


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def require_user(access_token: Optional[str] = Cookie(default=None, alias=settings.cookie_name)) -> str:
	username = decode_access_token(access_token) if access_token else None
	if not username:
		raise HTTPException(status_code=status.HTTP_302_FOUND, detail="Redirect", headers={"Location": "/login"})
	return username


@router.get("/", response_class=HTMLResponse)
def list_patients(request: Request, db: Session = Depends(get_db), username: str = Depends(require_user)):
	patients = db.query(Patient).order_by(Patient.last_name, Patient.first_name).all()
	return templates.TemplateResponse("patients/list.html", {"request": request, "patients": patients, "username": username})


@router.get("/new", response_class=HTMLResponse)
def new_patient(request: Request, username: str = Depends(require_user)):
	return templates.TemplateResponse("patients/form.html", {"request": request, "patient": None, "username": username})


@router.post("/new")
def create_patient(
	request: Request,
	db: Session = Depends(get_db),
	username: str = Depends(require_user),
	first_name: str = Form(...),
	last_name: str = Form(...),
	dob: Optional[str] = Form(None),
	phone: Optional[str] = Form(None),
	email: Optional[str] = Form(None),
	notes: Optional[str] = Form(None),
):
	patient = Patient(
		first_name=first_name.strip(),
		last_name=last_name.strip(),
		dob=date.fromisoformat(dob) if dob else None,
		phone=(phone or "").strip() or None,
		email=(email or "").strip() or None,
		notes=(notes or "").strip() or None,
	)
	db.add(patient)
	db.commit()
	return RedirectResponse(url="/patients", status_code=status.HTTP_302_FOUND)


@router.get("/{patient_id}", response_class=HTMLResponse)
def edit_patient(patient_id: int, request: Request, db: Session = Depends(get_db), username: str = Depends(require_user)):
	patient = db.get(Patient, patient_id)
	if not patient:
		raise HTTPException(status_code=404, detail="Patient not found")
	return templates.TemplateResponse("patients/form.html", {"request": request, "patient": patient, "username": username})


@router.post("/{patient_id}")
def update_patient(
	patient_id: int,
	request: Request,
	db: Session = Depends(get_db),
	username: str = Depends(require_user),
	first_name: str = Form(...),
	last_name: str = Form(...),
	dob: Optional[str] = Form(None),
	phone: Optional[str] = Form(None),
	email: Optional[str] = Form(None),
	notes: Optional[str] = Form(None),
):
	patient = db.get(Patient, patient_id)
	if not patient:
		raise HTTPException(status_code=404, detail="Patient not found")
	patient.first_name = first_name.strip()
	patient.last_name = last_name.strip()
	patient.dob = date.fromisoformat(dob) if dob else None
	patient.phone = (phone or "").strip() or None
	patient.email = (email or "").strip() or None
	patient.notes = (notes or "").strip() or None
	db.add(patient)
	db.commit()
	return RedirectResponse(url="/patients", status_code=status.HTTP_302_FOUND)


@router.post("/{patient_id}/delete")
def delete_patient(patient_id: int, db: Session = Depends(get_db), username: str = Depends(require_user)):
	patient = db.get(Patient, patient_id)
	if not patient:
		raise HTTPException(status_code=404, detail="Patient not found")
	db.delete(patient)
	db.commit()
	return RedirectResponse(url="/patients", status_code=status.HTTP_302_FOUND)
