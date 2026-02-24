"""Chat endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import json

from ..database import get_db
from ..models import User, Message, ChatSession
from ..schemas import (
    SessionCreate, SessionUpdate, SessionResponse, SessionDetail,
    MessageCreate, MessageUpdate, MessageResponse, VisualizationResponse
)
from ..dependencies import get_current_user
from .service import ChatService

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.get("/sessions", response_model=List[SessionResponse])
def get_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all chat sessions for current user"""
    service = ChatService(db)
    sessions = service.get_user_sessions(current_user.id)
    return sessions


@router.post("/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    session_data: SessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new chat session"""
    service = ChatService(db)
    session = service.create_session(current_user.id, session_data)
    return session


@router.get("/sessions/{session_id}", response_model=SessionDetail)
def get_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a chat session with all messages"""
    service = ChatService(db)
    session = service.get_session(session_id, current_user.id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    session.messages = service.get_session_messages(session_id, current_user.id)
    return session


@router.put("/sessions/{session_id}", response_model=SessionResponse)
def update_session(
    session_id: int,
    session_data: SessionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a chat session name"""
    service = ChatService(db)
    session = service.get_session(session_id, current_user.id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return service.update_session(session, session_data)


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a chat session and all associated data"""
    service = ChatService(db)
    session = service.get_session(session_id, current_user.id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    service.delete_session(session)


@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponse])
def get_messages(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all messages in a session"""
    service = ChatService(db)
    session = service.get_session(session_id, current_user.id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return service.get_session_messages(session_id, current_user.id)


async def message_generator(message_stream):
    """Generator for SSE streaming"""
    try:
        import logging
        logging.info("Starting message stream")
        async for chunk in message_stream:
            yield f"data: {json.dumps({'content': chunk, 'done': False})}\n\n"
        yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"
        logging.info("Message stream completed successfully")
    except Exception as e:
        import logging
        logging.error(f"Error in message stream: {type(e).__name__}: {e}")
        yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"


@router.post("/sessions/{session_id}/messages", response_class=StreamingResponse)
async def send_message(
    session_id: int,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message and get streaming AI response"""
    # Check if user has API key for their selected provider
    if not current_user.has_api_key:
        provider = getattr(current_user, 'llm_provider', 'openai')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{provider.capitalize()} API key not set. Please add it in settings."
        )

    service = ChatService(db)
    file_context = ""  # TODO: Add file context when file upload is implemented

    # Get uploaded files for session to provide context
    from ..models import UploadedFile
    files = db.query(UploadedFile).filter(
        UploadedFile.session_id == session_id
    ).all()

    if files:
        import pandas as pd
        import os
        from ..config import settings
        import logging

        file_info = []
        for file in files:
            # Use the file_path from database (it's already the full path)
            file_path = file.file_path
            logging.info(f"Reading file for context: {file_path}")

            if os.path.exists(file_path):
                try:
                    df = pd.read_excel(file_path, nrows=5)  # Preview first 5 rows
                    file_info.append(
                        f"File: {file.original_filename}\n"
                        f"Columns: {', '.join(df.columns.tolist())}\n"
                        f"Preview:\n{df.to_string(index=False)}\n"
                        f"Total rows: {len(pd.read_excel(file_path))}"
                    )
                    logging.info(f"File context generated successfully for {file.original_filename}")
                except Exception as e:
                    logging.error(f"Error reading file for context: {e}")
                    file_info.append(f"File: {file.original_filename}")
            else:
                logging.warning(f"File not found at path: {file_path}")
                # Try alternative path
                alt_path = os.path.join(settings.UPLOAD_DIR, file.filename)
                if os.path.exists(alt_path):
                    try:
                        df = pd.read_excel(alt_path, nrows=5)
                        file_info.append(
                            f"File: {file.original_filename}\n"
                            f"Columns: {', '.join(df.columns.tolist())}\n"
                            f"Preview:\n{df.to_string(index=False)}\n"
                            f"Total rows: {len(pd.read_excel(alt_path))}"
                        )
                    except Exception:
                        file_info.append(f"File: {file.original_filename}")

        if file_info:
            file_context = "\n\n".join(file_info)
            logging.info(f"File context generated for {len(files)} file(s)")

    if message_data.stream:
        message_stream = service.stream_message(
            session_id=session_id,
            user_id=current_user.id,
            message_data=message_data,
            api_key=current_user.openai_api_key,
            model=current_user.openai_model,
            file_context=file_context
        )
        return StreamingResponse(
            message_generator(message_stream),
            media_type="text/event-stream"
        )
    else:
        assistant_message = await service.create_message(
            session_id=session_id,
            user_id=current_user.id,
            message_data=message_data,
            api_key=current_user.openai_api_key,
            model=current_user.openai_model,
            file_context=file_context
        )
        return assistant_message


@router.put("/messages/{message_id}", response_model=MessageResponse)
def update_message(
    message_id: int,
    message_data: MessageUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a message content"""
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )

    # Verify session ownership
    session = db.query(ChatSession).filter(
        ChatSession.id == message.session_id,
        ChatSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    service = ChatService(db)
    return service.update_message(message, message_data.content)


@router.post("/messages/{message_id}/regenerate", response_class=StreamingResponse)
async def regenerate_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Regenerate an AI message"""
    if not current_user.has_api_key:
        provider = getattr(current_user, 'llm_provider', 'openai')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{provider.capitalize()} API key not set. Please add it in settings."
        )

    service = ChatService(db)

    # Get the message and session_id
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )

    file_context = ""  # TODO: Add file context

    message_stream = service.regenerate_message(
        session_id=message.session_id,
        message_id=message_id,
        user_id=current_user.id,
        api_key=current_user.openai_api_key,
        model=current_user.openai_model,
        file_context=file_context
    )

    return StreamingResponse(
        message_generator(message_stream),
        media_type="text/event-stream"
    )
