"""
Script Name : schemas.py
Description : Pydantic schemas for data validation.
Author      : @tonybnya
"""

from pydantic import BaseModel, Field


class TranslationRequestSchema(BaseModel):
    """Schema for the translation request coming from the frontend."""

    text: str = Field(..., description="The text to be translated.")
    languages: str = Field(..., description="Comma-separated list of target languages.")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Hello, world!",
                "languages": "english, french, german, russian, spanish"
            }
        }
