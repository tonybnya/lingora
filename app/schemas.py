"""
Script Name : schemas.py
Description : Pydantic schemas for data validation.
Author      : @tonybnya
"""

from pydantic import BaseModel, Field


class TranslationRequestSchema(BaseModel):
    """Schema for the translation request coming from the frontend."""

    text: str = Field(..., description="The text to be translated.")
    language: str = Field(..., description="Target language.")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Hello, world!",
                "language": "french",
            }
        }
