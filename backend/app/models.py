"""SQLAlchemy database models"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    openai_api_key = Column(Text, nullable=True)
    openai_model = Column(String(50), nullable=False, default="gpt-4")

    # Multi-provider fields
    llm_provider = Column(String(20), nullable=False, default="openai")  # 'openai', 'anthropic', or 'openrouter'
    anthropic_api_key = Column(Text, nullable=True)
    anthropic_model = Column(String(50), nullable=True, default="claude-opus-4-6")
    openrouter_api_key = Column(Text, nullable=True)
    openrouter_model = Column(String(100), nullable=True, default="anthropic/claude-3.5-sonnet-20241022")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")

    @property
    def has_api_key(self) -> bool:
        """Check if user has an API key set for the selected provider"""
        if self.llm_provider == "openai":
            return bool(self.openai_api_key and self.openai_api_key.strip())
        elif self.llm_provider == "anthropic":
            return bool(self.anthropic_api_key and self.anthropic_api_key.strip())
        elif self.llm_provider == "openrouter":
            return bool(self.openrouter_api_key and self.openrouter_api_key.strip())
        return False


class ChatSession(Base):
    """Chat session model"""
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    files = relationship("UploadedFile", back_populates="session", cascade="all, delete-orphan")


class Message(Base):
    """Message model"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(10), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    is_edited = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    session = relationship("ChatSession", back_populates="messages")
    visualizations = relationship("Visualization", back_populates="message", cascade="all, delete-orphan")


class UploadedFile(Base):
    """Uploaded file model"""
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    file_size = Column(BigInteger, nullable=True)
    mime_type = Column(String(100), nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    session = relationship("ChatSession", back_populates="files")


class Visualization(Base):
    """Visualization model"""
    __tablename__ = "visualizations"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True)
    chart_type = Column(String(20), nullable=False)  # 'pie', 'bar', 'line', 'scatter'
    chart_config = Column(Text, nullable=False)  # JSON stored as text
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    message = relationship("Message", back_populates="visualizations")

    @property
    def chart_config_dict(self) -> dict:
        """Return chart_config as a parsed dictionary"""
        if isinstance(self.chart_config, dict):
            return self.chart_config
        try:
            import json
            return json.loads(self.chart_config) if self.chart_config else {}
        except (json.JSONDecodeError, TypeError):
            return {}
