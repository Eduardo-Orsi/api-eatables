import os
from typing import Optional
from datetime import date, time

from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from pydantic import ValidationError

from ..models.file import File
from ..models.relationship_event import RelationshipEvent
from ..schema.relationship_event_schema import RelationshipEventForm
from ..integration.wordpress import WordPress


WP_API_URL = os.getenv("WP_API_URL")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")

class RelationshipController:

    @staticmethod
    async def add_relationship_event(db: Session, couple_name: str, relationship_beginning_date: date,
                               relationship_beginning_hour: time, message: str, files: Optional[list[UploadFile]]):

        try:
            relationship_event_schema = RelationshipEventForm(
                couple_name=couple_name,
                relationship_beginning_date=relationship_beginning_date,
                relationship_beginning_hour=relationship_beginning_hour,
                message=message
            )
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=e.errors())

        relationship_event = RelationshipEvent(
            couple_name=relationship_event_schema.couple_name,
            relationship_beginning_date=relationship_event_schema.relationship_beginning_date,
            relationship_beginning_hour=relationship_event_schema.relationship_beginning_hour,
            message=relationship_event_schema.message
        )
        db.add(relationship_event)
        db.commit()

        wp_site = WordPress(WP_USERNAME, WP_APP_PASSWORD, WP_API_URL)
        for file in files:
            uploaded_file = await wp_site.upload_file(file)
            file_record = File(
                relationship_event_id=relationship_event.id,
                filename=uploaded_file.title.rendered,
                content_type=uploaded_file.mime_type,
                url=uploaded_file.source_url.unicode_string(),
                wordpress_id=uploaded_file.id
            )
            db.add(file_record)
        db.commit()

        return {"message": "Relationship event created successfully"}
