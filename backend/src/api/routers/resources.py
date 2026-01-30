from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from src.database import get_db
from src.models import Lab, Instructor, Module, Department
from src.auth.dependencies import get_current_user, get_current_active_admin
from src.auth.csrf import validate_csrf
from src.auth.security import get_password_hash

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")

# ================= 1. Labs =================
@router.post("/labs/create")
def create_lab(name: str = Form(...), dept: str = Form(...), capacity: int = Form(...), db: Session = Depends(get_db), user: Instructor = Depends(get_current_active_admin), csrf_protect: None = Depends(validate_csrf)):
    db.add(Lab(name=name, department_code=dept, capacity=capacity))
    db.commit()
    return RedirectResponse(url="/?success=Lab Created", status_code=303)

@router.post("/labs/delete/{lab_id}")
def delete_lab(lab_id: int, db: Session = Depends(get_db), user: Instructor = Depends(get_current_active_admin), csrf_protect: None = Depends(validate_csrf)):
    try:
        db.query(Lab).filter(Lab.id == lab_id).delete()
        db.commit()
        return RedirectResponse(url="/?success=Lab Deleted", status_code=303)
    except: return RedirectResponse(url=f"/?error=Cannot delete Lab (likely in use)", status_code=303)

@router.post("/labs/toggle/{lab_id}")
def toggle_lab(lab_id: int, db: Session = Depends(get_db), user: Instructor = Depends(get_current_active_admin), csrf_protect: None = Depends(validate_csrf)):
    lab = db.query(Lab).get(lab_id)
    if lab: 
        lab.is_active = not lab.is_active
        db.commit()
    return RedirectResponse(url="/?success=Lab Status Updated", status_code=303)

@router.get("/labs/edit/{lab_id}", response_class=HTMLResponse)
def edit_lab_page(request: Request, lab_id: int, user: Optional[Instructor] = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user: return RedirectResponse("/login")
    return templates.TemplateResponse("edit_lab.html", {
        "request": request, "lab": db.query(Lab).get(lab_id), "departments": db.query(Department).all(),
        "csrf_token": request.state.csrf_token
    })

@router.post("/labs/update/{lab_id}")
def update_lab(lab_id: int, name: str = Form(...), dept: str = Form(...), capacity: int = Form(...), db: Session = Depends(get_db), user: Instructor = Depends(get_current_active_admin), csrf_protect: None = Depends(validate_csrf)):
    l = db.query(Lab).get(lab_id)
    if l: l.name = name; l.department_code = dept; l.capacity = capacity; db.commit()
    return RedirectResponse(url="/?success=Lab Updated", status_code=303)


# ================= 2. Modules =================
@router.post("/modules/create")
def create_module(code: str = Form(...), title: str = Form(...), dept: str = Form(...), semester: int = Form(...), db: Session = Depends(get_db), user: Instructor = Depends(get_current_active_admin), csrf_protect: None = Depends(validate_csrf)):
    db.add(Module(code=code, title=title, offering_dept=dept, semester=semester))
    db.commit()
    return RedirectResponse(url="/?success=Module Created", status_code=303)

@router.post("/modules/delete/{code}")
def delete_module(code: str, db: Session = Depends(get_db), user: Instructor = Depends(get_current_active_admin), csrf_protect: None = Depends(validate_csrf)):
    try:
        db.query(Module).filter(Module.code == code).delete()
        db.commit()
        return RedirectResponse(url="/?success=Module Deleted", status_code=303)
    except: return RedirectResponse(url=f"/?error=Cannot delete Module (likely in use)", status_code=303)

@router.post("/modules/toggle/{code}")
def toggle_module(code: str, db: Session = Depends(get_db), user: Instructor = Depends(get_current_active_admin), csrf_protect: None = Depends(validate_csrf)):
    mod = db.query(Module).get(code)
    if mod: 
        mod.is_active = not mod.is_active
        db.commit()
    return RedirectResponse(url="/?success=Module Status Updated", status_code=303)

@router.get("/modules/edit/{code}", response_class=HTMLResponse)
def edit_module_page(request: Request, code: str, user: Optional[Instructor] = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user: return RedirectResponse("/login")
    return templates.TemplateResponse("edit_module.html", {
        "request": request, "module": db.query(Module).get(code), "departments": db.query(Department).all(),
        "csrf_token": request.state.csrf_token
    })

@router.post("/modules/update/{code}")
def update_module(code: str, new_code: str = Form(None), title: str = Form(...), dept: str = Form(...), semester: int = Form(...), db: Session = Depends(get_db), user: Instructor = Depends(get_current_active_admin), csrf_protect: None = Depends(validate_csrf)):
    m = db.query(Module).get(code)
    if not m:
         return RedirectResponse(url="/?error=Module not found", status_code=303)
         
    if new_code and new_code != code:
        # Check if new code exists
        if db.query(Module).get(new_code):
            return RedirectResponse(url=f"/?error=Module Code {new_code} already exists", status_code=303)
        # Update PK
        m.code = new_code
        
    m.title = title
    m.offering_dept = dept
    m.semester = semester
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        return RedirectResponse(url=f"/?error=Cannot update code (Bookings exist?): {str(e)}", status_code=303)
        
    return RedirectResponse(url="/?success=Module Updated", status_code=303)


# ================= 3. Instructors =================
@router.post("/instructors/create")
def create_instructor(
    email: str = Form(...), name: str = Form(...), dept: str = Form(...),
    university: str = Form(""), degree: str = Form(""), graduated_date: str = Form(None),
    photo_url: str = Form(""), role: str = Form("INSTRUCTOR"),
    db: Session = Depends(get_db),
    user: Instructor = Depends(get_current_active_admin),
    csrf_protect: None = Depends(validate_csrf)
):
    g_date = datetime.strptime(graduated_date, "%Y-%m-%d").date() if graduated_date else None
    
    # SECURITY: Hash the default password for new users
    hashed_default = get_password_hash("password123")
    
    db.add(Instructor(
        email=email, name=name, department_code=dept, role=role,
        university=university, degree=degree, graduated_date=g_date, photo_url=photo_url,
        password=hashed_default # Use hashed version
    ))
    db.commit()
    return RedirectResponse(url="/?success=Instructor Created", status_code=303)

@router.post("/instructors/delete/{id}")
def delete_instructor(id: int, db: Session = Depends(get_db), user: Instructor = Depends(get_current_active_admin), csrf_protect: None = Depends(validate_csrf)):
    try:
        db.query(Instructor).filter(Instructor.id == id).delete()
        db.commit()
        return RedirectResponse(url="/?success=Instructor Deleted", status_code=303)
    except: return RedirectResponse(url=f"/?error=Cannot delete Instructor (likely has bookings)", status_code=303)

@router.post("/instructors/toggle/{id}")
def toggle_instructor(id: int, db: Session = Depends(get_db), user: Instructor = Depends(get_current_active_admin), csrf_protect: None = Depends(validate_csrf)):
    inst = db.query(Instructor).get(id)
    if inst: 
        inst.is_active = not inst.is_active
        db.commit()
    return RedirectResponse(url="/?success=Instructor Status Updated", status_code=303)

@router.get("/instructors/edit/{id}", response_class=HTMLResponse)
def edit_instructor_page(request: Request, id: int, user: Optional[Instructor] = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user: return RedirectResponse("/login")
    return templates.TemplateResponse("edit_instructor.html", {
        "request": request, "instructor": db.query(Instructor).get(id), "departments": db.query(Department).all(),
        "csrf_token": request.state.csrf_token
    })

@router.post("/instructors/update/{id}")
def update_instructor(
    id: int, name: str = Form(...), email: str = Form(...), dept: str = Form(...),
    university: str = Form(""), degree: str = Form(""), graduated_date: str = Form(None),
    photo_url: str = Form(""), role: str = Form("INSTRUCTOR"),
    db: Session = Depends(get_db),
    csrf_protect: None = Depends(validate_csrf)
):
    i = db.query(Instructor).get(id)
    if i:
        g_date = datetime.strptime(graduated_date, "%Y-%m-%d").date() if graduated_date else None
        i.name = name; i.email = email; i.department_code = dept; i.role = role
        i.university = university; i.degree = degree; i.graduated_date = g_date; i.photo_url = photo_url
        db.commit()
    return RedirectResponse(url="/?success=Instructor Updated", status_code=303)
