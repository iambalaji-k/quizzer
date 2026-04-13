"""Common schema types."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ORMBase(BaseModel):
    """Base schema with SQLAlchemy ORM compatibility."""

    model_config = ConfigDict(from_attributes=True)

