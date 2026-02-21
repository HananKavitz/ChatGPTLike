"""Chat business logic"""
from typing import List, Optional, AsyncIterator
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models import ChatSession, Message, User
from ..schemas import MessageCreate, SessionCreate, SessionUpdate
from .openai_client import OpenAIClient, format_messages_for_openai


class ChatService:
    """Service for chat operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_user_sessions(self, user_id: int) -> List[ChatSession]:
        """Get all sessions for a user"""
        sessions = self.db.query(ChatSession).filter(
            ChatSession.user_id == user_id
        ).order_by(ChatSession.updated_at.desc()).all()

        # Add message count to each session
        for session in sessions:
            session.message_count = self.db.query(Message).filter(
                Message.session_id == session.id
            ).count()

        return sessions

    def get_session(self, session_id: int, user_id: int) -> Optional[ChatSession]:
        """Get a specific session if it belongs to the user"""
        return self.db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        ).first()

    def create_session(self, user_id: int, session_data: SessionCreate) -> ChatSession:
        """Create a new chat session"""
        new_session = ChatSession(
            user_id=user_id,
            name=session_data.name
        )
        self.db.add(new_session)
        self.db.commit()
        self.db.refresh(new_session)
        return new_session

    def update_session(self, session: ChatSession, session_data: SessionUpdate) -> ChatSession:
        """Update a chat session"""
        session.name = session_data.name
        self.db.commit()
        self.db.refresh(session)
        return session

    def delete_session(self, session: ChatSession) -> None:
        """Delete a chat session (cascade will delete messages and files)"""
        self.db.delete(session)
        self.db.commit()

    def get_session_messages(self, session_id: int, user_id: int) -> List[Message]:
        """Get all messages for a session"""
        # Verify session belongs to user
        session = self.get_session(session_id, user_id)
        if not session:
            return []

        return self.db.query(Message).filter(
            Message.session_id == session_id
        ).order_by(Message.created_at.asc()).all()

    async def create_message(
        self,
        session_id: int,
        user_id: int,
        message_data: MessageCreate,
        api_key: str,
        model: str,
        file_context: str = ""
    ) -> Message:
        """Create a new message and get AI response"""

        # Verify session belongs to user
        session = self.get_session(session_id, user_id)
        if not session:
            raise ValueError("Session not found")

        # Create user message
        user_message = Message(
            session_id=session_id,
            role="user",
            content=message_data.content,
            is_edited=False
        )
        self.db.add(user_message)
        self.db.commit()
        self.db.refresh(user_message)

        # Get conversation history
        messages = self.db.query(Message).filter(
            Message.session_id == session_id,
            Message.id < user_message.id
        ).order_by(Message.created_at.asc()).all()

        # Format messages for OpenAI
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        # Get AI response
        client = OpenAIClient(api_key)
        formatted_messages = format_messages_for_openai(history, file_context)

        ai_content = ""
        async for chunk in client.chat_completion(
            messages=formatted_messages,
            model=model,
            stream=False  # We'll handle streaming at the router level
        ):
            ai_content += chunk

        # Create assistant message
        assistant_message = Message(
            session_id=session_id,
            role="assistant",
            content=ai_content,
            is_edited=False
        )
        self.db.add(assistant_message)

        # Update session updated_at
        session.updated_at = func.now()

        self.db.commit()
        self.db.refresh(assistant_message)

        return assistant_message

    async def stream_message(
        self,
        session_id: int,
        user_id: int,
        message_data: MessageCreate,
        api_key: str,
        model: str,
        file_context: str = ""
    ) -> AsyncIterator[str]:
        """Stream AI response for a new message"""

        # Verify session belongs to user
        session = self.get_session(session_id, user_id)
        if not session:
            raise ValueError("Session not found")

        # Create user message
        user_message = Message(
            session_id=session_id,
            role="user",
            content=message_data.content,
            is_edited=False
        )
        self.db.add(user_message)
        self.db.commit()
        self.db.refresh(user_message)

        # Get conversation history
        messages = self.db.query(Message).filter(
            Message.session_id == session_id,
            Message.id < user_message.id
        ).order_by(Message.created_at.asc()).all()

        # Format messages for OpenAI
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        # Stream AI response
        client = OpenAIClient(api_key)
        formatted_messages = format_messages_for_openai(history, file_context)

        ai_content = ""
        async for chunk in client.chat_completion(
            messages=formatted_messages,
            model=model,
            stream=True
        ):
            ai_content += chunk
            yield chunk

        # Save assistant message after streaming completes
        assistant_message = Message(
            session_id=session_id,
            role="assistant",
            content=ai_content,
            is_edited=False
        )
        self.db.add(assistant_message)

        # Update session updated_at
        session.updated_at = func.now()

        self.db.commit()
        self.db.refresh(assistant_message)

    def update_message(self, message: Message, new_content: str) -> Message:
        """Update a message (edit)"""
        message.content = new_content
        message.is_edited = True
        self.db.commit()
        self.db.refresh(message)
        return message

    async def regenerate_message(
        self,
        session_id: int,
        message_id: int,
        user_id: int,
        api_key: str,
        model: str,
        file_context: str = ""
    ) -> AsyncIterator[str]:
        """Regenerate an AI message"""

        # Get the session and verify ownership
        session = self.get_session(session_id, user_id)
        if not session:
            raise ValueError("Session not found")

        # Get the message to regenerate (should be an assistant message)
        message = self.db.query(Message).filter(
            Message.id == message_id,
            Message.session_id == session_id
        ).first()

        if not message or message.role != "assistant":
            raise ValueError("Message not found or is not an assistant message")

        # Get messages before this one
        messages = self.db.query(Message).filter(
            Message.session_id == session_id,
            Message.id < message_id
        ).order_by(Message.created_at.asc()).all()

        # Format messages for OpenAI
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        # Stream new AI response
        client = OpenAIClient(api_key)
        formatted_messages = format_messages_for_openai(history, file_context)

        ai_content = ""
        async for chunk in client.chat_completion(
            messages=formatted_messages,
            model=model,
            stream=True
        ):
            ai_content += chunk
            yield chunk

        # Update the message
        message.content = ai_content
        message.is_edited = True
        self.db.commit()
        self.db.refresh(message)
