from datetime import datetime
from typing import Optional

from fastapi import Cookie, Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .auth.security import create_access_token, decode_access_token, hash_password, verify_password
from .core.config import settings
from .database import Base, engine, get_db
from .models import User


def create_db_and_seed(db: Session) -> None:
	Base.metadata.create_all(bind=engine)
	admin = db.query(User).filter(User.username == settings.admin_username).first()
	if not admin:
		user = User(
			username=settings.admin_username,
			hashed_password=hash_password(settings.admin_password),
			is_active=True,
			is_admin=True,
		)
		db.add(user)
		db.commit()
		db.refresh(user)


app = FastAPI(title=settings.app_name, debug=settings.debug)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


def get_current_username(access_token: Optional[str] = Cookie(default=None, alias=settings.cookie_name)) -> Optional[str]:
	if not access_token:
		return None
	return decode_access_token(access_token)


@app.on_event("startup")
def on_startup() -> None:
	db = next(get_db())
	try:
		create_db_and_seed(db)
	finally:
		db.close()


@app.get("/", response_class=HTMLResponse)
def index(request: Request, username: Optional[str] = Depends(get_current_username)):
	if not username:
		return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
	return templates.TemplateResponse("base.html", {"request": request, "username": username})


@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
	return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.post("/login")
async def login():
	return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)


# Proper login handler using form parsing explicitly
@app.post("/login/submit")
async def login_submit(request: Request, db: Session = Depends(get_db)):
	form = await request.form()
	username = str(form.get("username", "")).strip()
	password = str(form.get("password", "")).strip()
	user = db.query(User).filter(User.username == username).first()
	if not user or not verify_password(password, user.hashed_password):
		return templates.TemplateResponse(
			"login.html",
			{"request": request, "error": "Invalid credentials"},
			status_code=status.HTTP_400_BAD_REQUEST,
		)
	access_token = create_access_token(subject=username)
	response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
	response.set_cookie(
		key=settings.cookie_name,
		value=access_token,
		http_only=True,
		secure=False,
		samesite="lax",
	)
	return response


@app.get("/logout")
def logout():
	response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
	response.delete_cookie(settings.cookie_name)
	return response


# Routers will be included after creation
from .routers.patients import router as patients_router
from .routers.doctors import router as doctors_router
from .routers.appointments import router as appointments_router

app.include_router(patients_router, prefix="/patients", tags=["patients"])
app.include_router(doctors_router, prefix="/doctors", tags=["doctors"])
app.include_router(appointments_router, prefix="/appointments", tags=["appointments"])
