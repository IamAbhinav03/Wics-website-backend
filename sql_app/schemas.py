from typing import Optional, List
from pydantic import BaseModel, HttpUrl
from fastapi import UploadFile


# Pydantic models
class DepartmentBase(BaseModel):
    name: str


class DepartmentCreate(DepartmentBase):
    pass


class Department(DepartmentBase):
    id: int
    # members: List["Member"] = []

    class Config:
        form_attributes = True


class MemberBase(BaseModel):
    name: str
    role: Optional[str] = None
    photo: Optional[UploadFile] = None
    photo_uri: Optional[str] = None
    active_member: Optional[bool] = True


class MemberCreate(MemberBase):
    department_ids: List[int]
    pass


class Member(MemberBase):
    id: int
    departments: List[Department] = []

    class Config:
        form_attributes = True


from pydantic import BaseModel


class BlogBase(BaseModel):
    title: str
    author: str
    cover_image_uri: Optional[str] = None
    body: str


class BlogCreate(BlogBase):
    photo: Optional[UploadFile] = None
    pass


class Blog(BlogBase):
    id: int

    class Config:
        form_attributes = True
