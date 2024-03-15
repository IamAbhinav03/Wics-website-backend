from sqlalchemy import Column, Integer, String, Boolean, Text, Table, ForeignKey

from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Define the association table for the many-to-many relationship between Members and Departments
department_member_association = Table(
    "department_member_association",
    Base.metadata,
    Column("department_id", Integer, ForeignKey("departments.id")),
    Column("member_id", Integer, ForeignKey("members.id")),
)


# SQLAlchemy models
class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    members = relationship(
        "Member", secondary=department_member_association, back_populates="departments"
    )


class Member(Base):
    __tablename__ = "members"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    photo_uri = Column(String)
    role = Column(String)
    active_member = Column(Boolean)
    departments = relationship(
        "Department", secondary=department_member_association, back_populates="members"
    )


class Blog(Base):
    """
    Blog model representing a blog post.
    """

    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(250))
    author = Column(String(50))
    cover_image_uri = Column(String)  # Store the image address
    body = Column(Text)
