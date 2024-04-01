import os
from mimetypes import guess_type
from dotenv import load_dotenv
import requests
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, UploadFile
from . import models, schemas


load_dotenv(dotenv_path=".env.development.local")  # testing
# load_dotenv(dotenv_path=".env")  # production

BLOB_READ_WRITE_TOKEN = os.getenv("BLOB_READ_WRITE_TOKEN")
VERCEL_API_URL = "https://blob.vercel-storage.com"
API_VERSION = "4"
DEFAULT_CACHE_AGE = 365 * 24 * 60 * 60


# utility functions for some of the crud operations
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
        timeout=10,
    )
    return resp.json().get("url")


def delete_photo(url: str):
    headers = {
        "authorization": f"Bearer {BLOB_READ_WRITE_TOKEN}",
        "x-api-version": API_VERSION,
        "x-content-type": "application/json",
    }
    requests.delete(
        f"{VERCEL_API_URL}/delete",
        json={
            "urls": (
                [
                    url,
                ]
                if isinstance(url, str)
                else url
            )
        },
        headers=headers,
        timeout=10,
    )
    return None


# CRUD operations for Department
async def create_department(db: Session, department: schemas.DepartmentCreate):
    db_department = models.Department(**department.model_dump())
    db.add(db_department)
    db.commit()
    db.refresh(db_department)
    return db_department


async def get_department_by_id(db: Session, department_id: int):
    db_department = (
        db.query(models.Department)
        .filter(models.Department.id == department_id)
        .first()
    )
    if db_department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    return db_department


async def get_departments(db: Session, skip: int = 0, limit: int = 10):
    return (
        db.query(models.Department)
        .options(joinedload(models.Department.members))
        .offset(skip)
        .limit(limit)
        .all()
    )


async def update_department(department_id: int, name: str, db: Session):
    db_department = (
        db.query(models.Department)
        .filter(models.Department.id == department_id)
        .first()
    )
    if db_department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    db_department.name = name
    # db.add(db_department)
    db.commit()
    db.refresh(db_department)
    return db_department


async def delete_department(db: Session, department_id: int):
    print("*" * 10)
    print("starting the crud operation")
    db_department = (
        db.query(models.Department)
        .filter(models.Department.id == department_id)
        .first()
    )
    # print("*" * 10)
    # print(db_department)
    # print(type(db_department))
    # print("*" * 10)
    if db_department:
        db.delete(db_department)
        db.commit()
        return {"message": "Department deleted"}
    else:
        raise HTTPException(status_code=404, detail="Department not found")


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


async def get_members_by_role(db: Session, role: str, skip: int = 0, limit: int = 10):
    return (
        db.query(models.Member)
        .filter(models.Member.role == role)
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_member(db: Session, member_id: int, member: schemas.MemberCreate):
    db_member = db.query(models.Member).filter(models.Member.id == member_id).first()
    if db_member is None:
        raise HTTPException(status_code=404, detail="Member not found")

    if member.photo:
        photo_uri = photo_upload(
            file=member.photo,
            file_name=member.name,
            upload_folder="uploaded_images",
        )
        if (
            db_member.photo_uri
            != "https://akmiccoer19irir6.public.blob.vercel-storage.com/uploaded_images/placeholder-LfUscThhRnJRb0vT6hqOrhgNptslJC.png"
        ):
            delete_photo(db_member.photo_uri)  # deleting existing photo uri
    else:
        photo_uri = "https://akmiccoer19irir6.public.blob.vercel-storage.com/uploaded_images/placeholder-LfUscThhRnJRb0vT6hqOrhgNptslJC.png"  # url to placeholder image

    member.photo_uri = photo_uri
    # db_member = models.Member(**member
    for attr, value in member.model_dump().items():
        setattr(db_member, attr, value)

    db_member.departments = []
    for department_id in member.department_ids:
        department = (
            db.query(models.Department)
            .filter(models.Department.id == department_id)
            .first()
        )
        if department:
            db_member.departments.append(department)
            # may have to delete the departments then append

    # db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


async def delete_member(db: Session, member_id: int):
    db_member = db.query(models.Member).filter(models.Member.id == member_id).first()
    delete_photo(db_member.photo_uri)
    if db_member:
        db.delete(db_member)
        db.commit()
        return {"message": "Member deleted"}
    else:
        raise HTTPException(status_code=404, detail="Member not found")


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
        delete_photo(db_blog.cover_image_uri)
        db.delete(db_blog)
        db.commit()
        return {"message": "Blog deleted"}
    else:
        raise HTTPException(status_code=404, detail="Blog not found")
