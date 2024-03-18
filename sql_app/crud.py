import os
from mimetypes import guess_type
from dotenv import load_dotenv
import requests
from sqlalchemy.orm import Session, joinedload
from fastapi import UploadFile
from . import models, schemas


load_dotenv(dotenv_path=".env.development.local")  # testing
# load_dotenv(dotenv_path=".env")  # production

BLOB_READ_WRITE_TOKEN = os.getenv("BLOB_READ_WRITE_TOKEN")
VERCEL_API_URL = "https://blob.vercel-storage.com"
API_VERSION = "4"
DEFAULT_CACHE_AGE = 365 * 24 * 60 * 60


# CRUD operations for Department
async def create_department(db: Session, department: schemas.DepartmentCreate):
    db_department = models.Department(**department.model_dump())
    db.add(db_department)
    db.commit()
    db.refresh(db_department)
    return db_department


async def get_departments(db: Session, skip: int = 0, limit: int = 10):
    return (
        db.query(models.Department)
        .options(joinedload(models.Department.members))
        .offset(skip)
        .limit(limit)
        .all()
    )


async def update_department(
    db: Session, department_id: int, department: schemas.DepartmentCreate
):
    db_department = (
        db.query(models.Department)
        .filter(models.Department.id == department_id)
        .first()
    )
    if db_department:
        for key, value in department.model_dump.items():
            setattr(db_department, key, value)
        db.commit()
        db.refresh(db_department)
    return db_department


async def delete_department(db: Session, department_id: int):
    db_department = (
        db.query(models.Department)
        .filter(models.Department.id == department_id)
        .first()
    )
    if db_department:
        db.delete(department_id)
        db.commit()
        return True
    return False


def guess_mime_type(url):
    return guess_type(url, strict=False)[0]


def photo_upload(file: UploadFile, file_name: str, upload_folder: str):
    file_extension = file.filename.split(".")[-1]
    file_name = f"{upload_folder}/{file_name}.{file_extension}"
    headers = {
        "access": "public",
        "authorization": f"Bearer {BLOB_READ_WRITE_TOKEN}",
        "x-api-version": API_VERSION,
        "x-content-type": guess_mime_type(file_name),
        "x-cache-control-max-age": str(DEFAULT_CACHE_AGE),
    }
    resp = requests.put(
        f"{VERCEL_API_URL}/{file_name}",
        data=file.read(),
        headers=headers,
    )
    return resp.json().get("url")


async def create_member(
    db: Session,
    member: schemas.MemberCreate,
):
    if member.photo:
        photo_uri = photo_upload(
            file=member.photo, file_name=member.name, upload_folder="uploaded_images"
        )
    else:
        photo_uri = "https://akmiccoer19irir6.public.blob.vercel-storage.com/uploaded_images/placeholder-LfUscThhRnJRb0vT6hqOrhgNptslJC.png"  # url to placeholder image

    member.photo_uri = photo_uri
    db_member = models.Member(**member.model_dump(exclude={"photo", "department_ids"}))
    for department_id in member.department_ids:
        department = (
            db.query(models.Department)
            .filter(models.Department.id == department_id)
            .first()
        )
        if department:
            db_member.departments.append(department)

    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


async def get_members(db: Session, skip: int = 0, limit: int = 10):
    return (
        db.query(models.Member)
        .options(joinedload(models.Member.departments))
        .offset(skip)
        .limit(limit)
        .all()
    )


# async def update_member(db: Session, member_id: int, member: schemas.MemberCreate):
#     db_member = db.query(models.Member).filter(models.Member.id == member_id).first()
#     if member.photo
#     for key, value in member.model_dump.items():
#         setattr(db_member, key, value)


async def get_members_by_role(db: Session, role: str, skip: int = 0, limit: int = 10):
    return (
        db.query(models.Member)
        .filter(models.Member.role == role)
        .offset(skip)
        .limit(limit)
        .all()
    )


async def create_blog(db: Session, blog: schemas.BlogCreate):
    if blog.photo:
        photo_uri = photo_upload(
            file=blog.photo, file_name=blog.title, upload_folder="blog_cover_images"
        )
    else:
        # If no photo is uploaded, use placeholder image
        photo_uri = "https://akmiccoer19irir6.public.blob.vercel-storage.com/uploaded_images/placeholder-LfUscThhRnJRb0vT6hqOrhgNptslJC.png"
    blog.cover_image_uri = photo_uri
    db_blog = models.Blog(**blog.model_dump(exclude={"photo"}))
    db.add(db_blog)
    db.commit()
    db.refresh(db_blog)
    return db_blog


async def get_blog(db: Session, blog_id: int):
    return db.query(models.Blog).filter(models.Blog.id == blog_id).first()


async def update_blog(db: Session, blog_id: int, blog: schemas.BlogCreate):
    db_blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if db_blog:
        for key, value in blog.dict().items():
            setattr(db_blog, key, value)
        db.commit()
        db.refresh(db_blog)
    return db_blog


async def delete_blog(db: Session, blog_id: int):
    db_blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if db_blog:
        db.delete(db_blog)
        db.commit()
        return True
    return False
