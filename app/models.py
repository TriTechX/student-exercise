"""
Database models for the application.

This module defines the SQLAlchemy models for the app.
Currently, we have a single model:

- Register: Represents a collection or register in the system.

Notes for Students:
- Each class represents a table in the database.
- Each attribute of the class represents a column in the table.
- SQLAlchemy's ORM maps Python classes to database tables so we can
  work with Python objects instead of raw SQL.
"""

import uuid
from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, UniqueConstraint, DateTime, func, String
import datetime

# PostgreSQL UUID type for database columns
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import db

# TYPE_CHECKING is used to avoid circular import problems when
# using type hints in Python. It allows hints to be checked only
# during static analysis, not at runtime.
if TYPE_CHECKING:
    from flask_sqlalchemy.model import Model
else:
    # Use db.Model as the base class for our models
    Model = db.Model


class Register(Model):
    """
    Represents a Register record in the database.

    Attributes
    ----------
    id : uuid.UUID
        Primary key for the Register. Automatically generated using uuid4.
    name : str
        A human-readable name for the register.
        Must be unique and cannot be null. Indexed for faster lookups.

    Notes for Students
    -----------------
    - `mapped_column` defines a column in the database table.
    - `UUID(as_uuid=True)` ensures the database column stores a UUID
      and SQLAlchemy converts it to a Python `uuid.UUID` object.
    - `primary_key=True` makes this column the table's primary key.
    - `default=uuid.uuid4` automatically generates a new UUID when
      a Register is created.
    - `nullable=False` ensures this field must always have a value.
    - `unique=True` prevents two registers from having the same name.
    - `index=True` creates a database index on this column to make
      queries faster.
    """

    # Primary key column using UUID
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),  # Store as UUID in PostgreSQL
        primary_key=True,  # Primary key
        default=uuid.uuid4,  # Auto-generate a UUID
    )

    # Name column for the register
    name: Mapped[str] = mapped_column(
        String(),
        nullable=False,  # Cannot be empty
        unique=True,  # Each register name must be unique
        index=True,  # Database index for faster search
    )

    price: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
        unique=False,
        index=True
    )

    last_updated: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    entries: Mapped[List["Entry"]] = relationship(
        "Entry",
        back_populates="register",
        order_by="Entry.name",
    )

    author: Mapped[str] = mapped_column(
        default="Unknown",
        nullable=False,
        unique=False,
        index=True
    )


class Entry(Model):
    """
    Represents an Entry record in the database.

    Attributes
    ----------
    id : uuid.UUID
        Primary key for the Entry. Automatically generated using uuid4.
    name : str
        A human-readable name for the entry.
        Must be unique for a given register and cannot be null. Indexed for faster lookups.
    """

    # Primary key column using UUID
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),  # Store as UUID in PostgreSQL
        primary_key=True,  # Primary key
        default=uuid.uuid4,  # Auto-generate a UUID
    )

    # Name column for the entry
    name: Mapped[str] = mapped_column(
        nullable=False,  # Cannot be empty
        unique=False,  # Entry names are not globally unique, but should be unique on a given register
        index=True,  # Database index for faster search
    )

    author: Mapped[str] = mapped_column(
        nullable=False,
        default="Unknown"
    )

    # Foreign keys
    register_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("register.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    # Relationships
    register: Mapped["Register"] = relationship("Register", back_populates="entries")

    __table_args__ = (UniqueConstraint("name", "register_id", name="_entry_name_register_uc"),)


class Users(Model):
    """
    A simple Users table containing a unique UID for each user with
    plain text indexed usernames and hashed argon2 passwords. The
    hash is stored as a string and computed on the server.
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid = True),
        primary_key = True,
        default = uuid.uuid4
    )

    username: Mapped[str] = mapped_column(
        nullable = False,
        unique = True,
        index = True
    )

    password: Mapped[str] = mapped_column(
        nullable = False,
        unique = False,
        index = True
    )

    is_mod: Mapped[bool] = mapped_column(
        nullable=True,
        default=False
    )