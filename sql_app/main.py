from fastapi import Depends, APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Annotated
from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

router = APIRouter()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/departments/", response_model=schemas.Department)
async def create_department(
    department: schemas.DepartmentCreate, db: Session = Depends(get_db)
):
    return await crud.create_department(db=db, department=department)


@router.get("/departments/", response_model=List[schemas.Department])
async def read_departments(
    skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    return await crud.get_departments(db=db, skip=skip, limit=limit)


@router.post("/members")
async def create_member(
    name: Annotated[str, Form()],
    role: Annotated[str, Form()],
    department_ids: Annotated[List[int], Form()],
    active_member: Annotated[bool, Form()] = True,
    photo: Annotated[UploadFile, File()] = None,
    db: Session = Depends(get_db),
):
    member = schemas.MemberCreate(
        name=name,
        photo=photo,
        role=role,
        department_ids=department_ids,
        active_member=active_member,
    )
    return await crud.create_member(db=db, member=member)


@router.get("/members/{photo_name}")
async def get_member_photo(photo_name: str):
    path = f"static/{photo_name}"
    print(path)
    try:
        file = FileResponse(path=path)
        return file
    except:
        return {"error": "given path is not a valid path"}


@router.get("/members/", response_model=List[schemas.Member])
async def read_members(
    skip: int = 0, limit: int = 10, role: str = None, db: Session = Depends(get_db)
):
    if role:
        return await crud.get_members_by_role(db=db, role=role, skip=skip, limit=limit)
    else:
        return await crud.get_members(db=db, skip=skip, limit=limit)


async def get_members_by_role(db: Session, role: str, skip: int = 0, limit: int = 10):
    return (
        db.query(models.Member)
        .filter(models.Member.role == role)
        .offset(skip)
        .limit(limit)
        .all()
    )


# Create a blog
@router.post("/blogs/", response_model=schemas.Blog)
async def create_blog(
    title: Annotated[str, Form()],
    author: Annotated[str, Form()],
    body: Annotated[str, Form()],
    photo: Annotated[UploadFile, File()] = None,
    db: Session = Depends(get_db),
):
    blog = schemas.BlogCreate(title=title, author=author, photo=photo, body=body)
    return await crud.create_blog(db=db, blog=blog)


# Get a blog by ID
@router.get("/blogs/{blog_id}", response_model=schemas.Blog)
async def read_blog(blog_id: int, db: Session = Depends(get_db)):
    db_blog = await crud.get_blog(db=db, blog_id=blog_id)
    if db_blog is None:
        raise HTTPException(status_code=404, detail="Blog not found")
    return db_blog


# Update a blog
@router.put("/blogs/{blog_id}", response_model=schemas.Blog)
async def update_blog(
    blog_id: int, blog: schemas.BlogCreate, db: Session = Depends(get_db)
):
    db_blog = await crud.update_blog(db=db, blog_id=blog_id, blog=blog)
    if db_blog is None:
        raise HTTPException(status_code=404, detail="Blog not found")
    return db_blog


# Delete a blog
@router.delete("/blogs/{blog_id}")
async def delete_blog(blog_id: int, db: Session = Depends(get_db)):
    success = await crud.delete_blog(db=db, blog_id=blog_id)
    if not success:
        raise HTTPException(status_code=404, detail="Blog not found")
    return {"message": "Blog deleted successfully"}
