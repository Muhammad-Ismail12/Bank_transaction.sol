from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..auth.security import decode_access_token
from ..core.config import settings
from ..database import get_db
from ..models import Doctor


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def require_user(access_token: Optional[str] = Cookie(default=None, alias=settings.cookie_name)) -> str:
	username = decode_access_token(access_token) if access_token else None
	if not username:
		raise HTTPException(status_code=status.HTTP_302_FOUND, detail="Redirect", headers={"Location": "/login"})
	return username


@router.get("/", response_class=HTMLResponse)
def list_doctors(request: Request, db: Session = Depends(get_db), username: str = Depends(require_user)):
	doctors = db.query(Doctor).order_by(Doctor.last_name, Doctor.first_name).all()
	return templates.TemplateResponse("doctors/list.html", {"request": request, "doctors": doctors, "username": username})


@router.get("/new", response_class=HTMLResponse)
def new_doctor(request: Request, username: str = Depends(require_user)):
	return templates.TemplateResponse("doctors/form.html", {"request": request, "doctor": None, "username": username})


@router.post("/new")
def create_doctor(
	request: Request,
	db: Session = Depends(get_db),
	username: str = Depends(require_user),
	first_name: str = Form(...),
	last_name: str = Form(...),
	specialty: Optional[str] = Form(None),
	phone: Optional[str] = Form(None),
	email: Optional[str] = Form(None),
):
	doctor = Doctor(
		first_name=first_name.strip(),
		last_name=last_name.strip(),
		specialty=(specialty or "").strip() or None,
		phone=(phone or "").strip() or None,
		email=(email or "").strip() or None,
	)
	db.add(doctor)
	db.commit()
	return RedirectResponse(url="/doctors", status_code=status.HTTP_302_FOUND)


@router.get("/{doctor_id}", response_class=HTMLResponse)
def edit_doctor(doctor_id: int, request: Request, db: Session = Depends(get_db), username: str = Depends(require_user)):
	doctor = db.get(Doctor, doctor_id)
	if not doctor:
		raise HTTPException(status_code=404, detail="Doctor not found")
	return templates.TemplateResponse("doctors/form.html", {"request": request, "doctor": doctor, "username": username})


@router.post("/{doctor_id}")
def update_doctor(
	doctor_id: int,
	request: Request,
	db: Session = Depends(get_db),
	username: str = Depends(require_user),
	first_name: str = Form(...),
	last_name: str = Form(...),
	specialty: Optional[str] = Form(None),
	phone: Optional[str] = Form(None),
	email: Optional[str] = Form(None),
):
	doctor = db.get(Doctor, doctor_id)
	if not doctor:
		raise HTTPException(status_code=404, detail="Doctor not found")
	doctor.first_name = first_name.strip()
	doctor.last_name = last_name.strip()
	doctor.specialty = (specialty or "").strip() or None
	doctor.phone = (phone or "").strip() or None
	doctor.email = (email or "").strip() or None
	db.add(doctor)
	db.commit()
	return RedirectResponse(url="/doctors", status_code=status.HTTP_302_FOUND)


@router.post("/{doctor_id}/delete")
def delete_doctor(doctor_id: int, db: Session = Depends(get_db), username: str = Depends(require_user)):
	doctor = db.get(Doctor, doctor_id)
	if not doctor:
		raise HTTPException(status_code=404, detail="Doctor not found")
	db.delete(doctor)
	db.commit()
	return RedirectResponse(url="/doctors", status_code=status.HTTP_302_FOUND)
