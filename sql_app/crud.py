import os
from dotenv import load_dotenv
from typing import List
from mimetypes import guess_type
from sqlalchemy.orm import Session, joinedload

# from vercel_storage import blob
import requests
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


# CRUD operations for Member


# async def create_member(
#     db: Session,
#     # member: dict,
#     member: schemas.MemberCreate,
#     # department_ids: List[int],
#     # photo: UploadFile = None,
# ):
#     if member.photo:
#         file_extension = member.photo.filename.split(".")[-1]
#         file_name = f"uploaded_images/{member.name}.{file_extension}"
#         # file_path = os.path.join(UPLOAD_DIR, file_name)
#         #     with open(file_path, "wb") as file:
#         #         file.write(member.photo.file.read())
#         #     photo_uri = file_name
#         # else:
#         #     # If no photo is uploaded, use placeholder image
#         #     photo_uri = "static/uploaded_photos/placeholder.jpg"
#         # print(type(member.photo))
#         resp = blob.put(
#             pathname=file_name,
#             body=member.photo.file.read(),
#             options={"token": os.environ.get("BLOB_READ_WRITE_TOKEN")},
#         )
#         photo_uri = resp.get("url")
#     else:
#         photo_uri = "https://akmiccoer19irir6.public.blob.vercel-storage.com/uploaded_images/placeholder-LfUscThhRnJRb0vT6hqOrhgNptslJC.png"  # url to placeholder image

#     member.photo_uri = photo_uri
#     db_member = models.Member(**member.model_dump(exclude={"photo", "department_ids"}))
#     for department_id in member.department_ids:
#         department = (
#             db.query(models.Department)
#             .filter(models.Department.id == department_id)
#             .first()
#         )
#         if department:
#             db_member.departments.append(department)

#     db.add(db_member)
#     db.commit()
#     db.refresh(db_member)
#     return db_member


def guess_mime_type(url):
    return guess_type(url, strict=False)[0]


async def create_member(
    db: Session,
    # member: dict,
    member: schemas.MemberCreate,
    # department_ids: List[int],
    # photo: UploadFile = None,
):
    if member.photo:
        file_extension = member.photo.filename.split(".")[-1]
        file_name = f"uploaded_images/{member.name}.{file_extension}"
        # file_path = os.path.join(UPLOAD_DIR, file_name)
        #     with open(file_path, "wb") as file:
        #         file.write(member.photo.file.read())
        #     photo_uri = file_name
        # else:
        #     # If no photo is uploaded, use placeholder image
        #     photo_uri = "static/uploaded_photos/placeholder.jpg"
        # print(type(member.photo))
        # resp = blob.put(
        #     pathname=file_name,
        #     body=member.photo.file.read(),
        #     options={"token": os.environ.get("BLOB_READ_WRITE_TOKEN")},
        # )
        # photo_uri = resp.get("url")
        headers = {
            "access": "public",
            "authorization": f"Bearer {BLOB_READ_WRITE_TOKEN}",
            "x-api-version": API_VERSION,
            "x-content-type": guess_mime_type(file_name),
            "x-cache-control-max-age": str(DEFAULT_CACHE_AGE),
        }
        resp = requests.put(
            f"{VERCEL_API_URL}/{file_name}",
            data=member.photo.file.read(),
            headers=headers,
        )
        photo_uri = resp.json().get("url")
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
        file_extension = blog.photo.filename.split(".")[-1]
        file_name = f"{blog.title}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, file_name)
        with open(file_path, "wb") as file:
            file.write(blog.photo.file.read())
        photo_uri = file_name
    else:
        # If no photo is uploaded, use placeholder image
        photo_uri = "static/uploaded_photos/placeholder.jpg"
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
