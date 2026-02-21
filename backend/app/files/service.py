"""File handling logic"""
import os
import uuid
from typing import List, Optional
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from ..models import UploadedFile, ChatSession, User
from ..config import settings


class FileService:
    """Service for file operations"""

    def __init__(self, db: Session):
        self.db = db
        self.upload_dir = settings.UPLOAD_DIR

    def _ensure_upload_dir(self):
        """Ensure upload directory exists"""
        os.makedirs(self.upload_dir, exist_ok=True)

    def _get_file_extension(self, filename: str) -> str:
        """Get file extension"""
        return os.path.splitext(filename)[1].lower()

    async def upload_file(
        self,
        file: UploadFile,
        session_id: int,
        user_id: int
    ) -> UploadedFile:
        """Upload a file and save to database"""

        # Verify session belongs to user
        session = self.db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        ).first()

        if not session:
            raise ValueError("Session not found")

        # Validate file type
        extension = self._get_file_extension(file.filename)
        if extension not in settings.ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Invalid file type. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )

        # Read file content
        content = await file.read()

        # Validate file size
        if len(content) > settings.MAX_FILE_SIZE:
            raise ValueError(
                f"File too large. Maximum size: {settings.MAX_FILE_SIZE / (1024 * 1024)}MB"
            )

        # Ensure upload directory exists
        self._ensure_upload_dir()

        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}{extension}"
        file_path = os.path.join(self.upload_dir, unique_filename)

        # Save file
        with open(file_path, "wb") as f:
            f.write(content)

        # Determine MIME type
        mime_type = file.content_type or "application/octet-stream"

        # Create database record
        uploaded_file = UploadedFile(
            session_id=session_id,
            filename=unique_filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=len(content),
            mime_type=mime_type
        )

        self.db.add(uploaded_file)
        self.db.commit()
        self.db.refresh(uploaded_file)

        return uploaded_file

    def get_session_files(self, session_id: int, user_id: int) -> List[UploadedFile]:
        """Get all files for a session"""
        # Verify session belongs to user
        session = self.db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        ).first()

        if not session:
            return []

        return self.db.query(UploadedFile).filter(
            UploadedFile.session_id == session_id
        ).order_by(UploadedFile.uploaded_at.desc()).all()

    def delete_file(self, file_id: int, user_id: int) -> None:
        """Delete a file"""
        file = self.db.query(UploadedFile).filter(
            UploadedFile.id == file_id
        ).first()

        if not file:
            raise ValueError("File not found")

        # Verify session ownership
        session = self.db.query(ChatSession).filter(
            ChatSession.id == file.session_id,
            ChatSession.user_id == user_id
        ).first()

        if not session:
            raise ValueError("Session not found")

        # Delete physical file
        if os.path.exists(file.file_path):
            os.remove(file.file_path)

        # Delete database record
        self.db.delete(file)
        self.db.commit()

    def get_file(self, file_id: int, user_id: int) -> Optional[UploadedFile]:
        """Get a file by ID"""
        file = self.db.query(UploadedFile).filter(
            UploadedFile.id == file_id
        ).first()

        if not file:
            return None

        # Verify session ownership
        session = self.db.query(ChatSession).filter(
            ChatSession.id == file.session_id,
            ChatSession.user_id == user_id
        ).first()

        if not session:
            return None

        return file
