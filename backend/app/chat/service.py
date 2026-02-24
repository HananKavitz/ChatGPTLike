"""Chat business logic"""
from typing import List, Optional, AsyncIterator
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func
import json
import os

from ..models import ChatSession, Message, User, UploadedFile, Visualization
from ..schemas import MessageCreate, SessionCreate, SessionUpdate
from .openai_client import format_messages_for_openai  # Keep for backward compatibility
from .providers.factory import LLMProviderFactory
from ..config import settings


class ChatService:
    """Service for chat operations"""

    def __init__(self, db: Session):
        self.db = db

    def _get_llm_provider(self, user: User):
        """Get the appropriate LLM provider based on user settings."""
        provider_name = getattr(user, 'llm_provider', 'openai')  # Default to openai

        if provider_name == 'openai':
            api_key = user.openai_api_key
            if not api_key:
                raise ValueError("OpenAI API key not provided")
        elif provider_name == 'anthropic':
            api_key = getattr(user, 'anthropic_api_key', None)
            if not api_key:
                raise ValueError("Anthropic API key not provided")
        elif provider_name == 'openrouter':
            api_key = getattr(user, 'openrouter_api_key', None)
            if not api_key:
                raise ValueError("OpenRouter API key not provided")
        else:
            raise ValueError(f"Unsupported LLM provider: {provider_name}")

        return LLMProviderFactory.create(provider_name, api_key)

    def _get_chart_generator_for_session(self, session_id: int):
        """Get a chart generator for the first uploaded Excel file in a session"""
        file = self.db.query(UploadedFile).filter(
            UploadedFile.session_id == session_id
        ).first()

        if not file:
            return None

        # Use the file_path from the database (it's already the full path)
        file_path = file.file_path

        import logging
        logging.info(f"Looking for file at: {file_path}")

        if not os.path.exists(file_path):
            logging.warning(f"File does not exist at path: {file_path}")
            # Try alternative path using UPLOAD_DIR
            alt_path = os.path.join(settings.UPLOAD_DIR, file.filename)
            logging.info(f"Trying alternative path: {alt_path}")
            if os.path.exists(alt_path):
                file_path = alt_path
            else:
                return None

        logging.info(f"File found, creating chart generator")
        from ..chart.chart_generator import ChartGenerator
        return ChartGenerator(file_path)

    def _create_visualization(self, message_id: int, chart_type: str, chart_config: dict) -> Visualization:
        """Create a visualization record"""
        viz = Visualization(
            message_id=message_id,
            chart_type=chart_type,
            chart_config=json.dumps(chart_config)
        )
        self.db.add(viz)
        self.db.commit()
        self.db.refresh(viz)
        return viz

    def _detect_and_create_chart(self, user_message: str, message_id: int, session_id: int) -> Optional[Visualization]:
        """
        Detect if user wants a chart and create visualization.

        Returns:
            Visualization object if chart was created, None otherwise
        """
        import logging
        logging.info(f"Detecting chart request for message: {user_message[:100]}")

        from ..chart.chart_generator import parse_chart_request

        chart_request = parse_chart_request(user_message)
        if not chart_request:
            logging.info("No chart request detected")
            return None

        logging.info(f"Chart request detected: {chart_request}")

        generator = self._get_chart_generator_for_session(session_id)
        if not generator:
            logging.warning("No chart generator created - no file or file not found")
            return None

        try:
            logging.info(f"Generating {chart_request['chart_type']} chart...")
            chart_config = generator.auto_generate_chart(
                chart_type=chart_request["chart_type"],
                label_column=chart_request.get("label_column"),
                value_column=chart_request.get("value_column")
            )
            logging.info(f"Chart config generated successfully")
            viz = self._create_visualization(message_id, chart_request["chart_type"], chart_config)
            logging.info(f"Visualization created with id: {viz.id}")
            return viz
        except ValueError as e:
            # This is a data-related error - let AI explain the issue
            logging.warning(f"Chart generation failed (data issue): {e}")
            # Don't return None - let the AI's text response explain the issue
            return None
        except Exception as e:
            import traceback
            logging.error(f"Failed to generate chart (unexpected error): {e}")
            logging.error(traceback.format_exc())
            return None

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

        return self.db.query(Message).options(
            selectinload(Message.visualizations)
        ).filter(
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
            Message.id <= user_message.id
        ).order_by(Message.created_at.asc()).all()

        # Format messages for OpenAI
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        # Get AI response - check if we have user object to use provider pattern
        user = self.db.query(User).filter(User.id == user_id).first()
        provider_name = getattr(user, 'llm_provider', 'openai')  # Default to openai

        if provider_name == 'openai' and api_key:
            # Use legacy OpenAI client for backward compatibility
            from .openai_client import OpenAIClient
            client = OpenAIClient(api_key)
            formatted_messages = format_messages_for_openai(history, file_context)
        else:
            # Use provider pattern
            provider = self._get_llm_provider(user)

            # Use provider-specific model
            if provider_name == 'anthropic':
                model = getattr(user, 'anthropic_model', 'claude-opus-4-6')
            elif provider_name == 'openrouter':
                model = getattr(user, 'openrouter_model', 'anthropic/claude-3.5-sonnet-20241022')
            else:
                model = user.openai_model

            # Format messages with system prompt
            system_prompt = None
            if file_context:
                system_prompt = "You are a helpful AI assistant."
                system_prompt += f"\n\nYou have access to the following data from uploaded files:\n{file_context}\n\n"
                system_prompt += "When asked about charts or visualizations:"
                system_prompt += "- Directly analyze the data and provide insights"
                system_prompt += "- Describe what the visualization would show"
                system_prompt += "- Explain patterns and trends you observe"
                system_prompt += "- DO NOT provide code, tutorials, or instructions on how to create charts"
                system_prompt += "- The system will automatically generate the actual chart visualization for you"
                system_prompt += "- Focus on interpreting the data, not explaining how to visualize it"
                system_prompt += "\n\nExample of how to respond:"
                system_prompt += "User: 'Create a pie chart showing sales by region'"
                system_prompt += "Response: 'Here's a pie chart showing sales distribution by region. The West region has the highest sales at 45%, followed by the East region at 30%. The North and South regions contribute 15% and 10% respectively. This suggests the Western market is our strongest performing area.'"

            formatted_messages = provider.format_messages(history, system_prompt)

        ai_content = ""
        if provider_name == 'openai' and api_key and 'client' in locals():
            # Use legacy OpenAI client
            async for chunk in client.chat_completion(
                messages=formatted_messages,
                model=model,
                stream=False  # We'll handle streaming at the router level
            ):
                ai_content += chunk
        else:
            # Use provider pattern
            result = await provider.chat_completion(
                messages=formatted_messages,
                model=model,
                stream=False
            )
            ai_content = result

        # Create assistant message
        assistant_message = Message(
            session_id=session_id,
            role="assistant",
            content=ai_content,
            is_edited=False
        )
        self.db.add(assistant_message)
        self.db.commit()
        self.db.refresh(assistant_message)

        # Detect and create chart visualization if requested
        chart_viz = self._detect_and_create_chart(
            message_data.content,
            assistant_message.id,
            session_id
        )
        if chart_viz:
            self.db.refresh(assistant_message)

        # Update session updated_at
        session.updated_at = func.now()
        self.db.commit()

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
            Message.id <= user_message.id
        ).order_by(Message.created_at.asc()).all()

        # Format messages for OpenAI
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        # Stream AI response - check if we have user object to use provider pattern
        user = self.db.query(User).filter(User.id == user_id).first()
        provider_name = getattr(user, 'llm_provider', 'openai')  # Default to openai

        if provider_name == 'openai' and api_key:
            # Use legacy OpenAI client for backward compatibility
            from .openai_client import OpenAIClient
            client = OpenAIClient(api_key)
            formatted_messages = format_messages_for_openai(history, file_context)
        else:
            # Use provider pattern
            provider = self._get_llm_provider(user)

            # Use provider-specific model
            if provider_name == 'anthropic':
                model = getattr(user, 'anthropic_model', 'claude-opus-4-6')
            elif provider_name == 'openrouter':
                model = getattr(user, 'openrouter_model', 'anthropic/claude-3.5-sonnet-20241022')
            else:
                model = user.openai_model

            # Format messages with system prompt
            system_prompt = None
            if file_context:
                system_prompt = "You are a helpful AI assistant."
                system_prompt += f"\n\nYou have access to the following data from uploaded files:\n{file_context}\n\n"
                system_prompt += "When asked about charts or visualizations:"
                system_prompt += "- Directly analyze the data and provide insights"
                system_prompt += "- Describe what the visualization would show"
                system_prompt += "- Explain patterns and trends you observe"
                system_prompt += "- DO NOT provide code, tutorials, or instructions on how to create charts"
                system_prompt += "- The system will automatically generate the actual chart visualization for you"
                system_prompt += "- Focus on interpreting the data, not explaining how to visualize it"
                system_prompt += "\n\nExample of how to respond:"
                system_prompt += "User: 'Create a pie chart showing sales by region'"
                system_prompt += "Response: 'Here's a pie chart showing sales distribution by region. The West region has the highest sales at 45%, followed by the East region at 30%. The North and South regions contribute 15% and 10% respectively. This suggests the Western market is our strongest performing area.'"

            formatted_messages = provider.format_messages(history, system_prompt)

        ai_content = ""
        if provider_name == 'openai' and api_key and 'client' in locals():
            # Use legacy OpenAI client
            async for chunk in client.chat_completion(
                messages=formatted_messages,
                model=model,
                stream=True
            ):
                ai_content += chunk
                yield chunk
        else:
            # Use provider pattern
            stream = await provider.chat_completion(
                messages=formatted_messages,
                model=model,
                stream=True
            )
            async for chunk in stream:
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
        self.db.commit()
        self.db.refresh(assistant_message)

        # Detect and create chart visualization if requested
        chart_viz = self._detect_and_create_chart(
            message_data.content,
            assistant_message.id,
            session_id
        )

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

        # Stream new AI response - check if we have user object to use provider pattern
        user = self.db.query(User).filter(User.id == user_id).first()
        provider_name = getattr(user, 'llm_provider', 'openai')  # Default to openai

        if provider_name == 'openai' and api_key:
            # Use legacy OpenAI client for backward compatibility
            from .openai_client import OpenAIClient
            client = OpenAIClient(api_key)
            formatted_messages = format_messages_for_openai(history, file_context)
        else:
            # Use provider pattern
            provider = self._get_llm_provider(user)

            # Use provider-specific model
            if provider_name == 'anthropic':
                model = getattr(user, 'anthropic_model', 'claude-opus-4-6')
            elif provider_name == 'openrouter':
                model = getattr(user, 'openrouter_model', 'anthropic/claude-3.5-sonnet-20241022')
            else:
                model = user.openai_model

            # Format messages with system prompt
            system_prompt = None
            if file_context:
                system_prompt = "You are a helpful AI assistant."
                system_prompt += f"\n\nYou have access to the following data from uploaded files:\n{file_context}\n\n"
                system_prompt += "When asked about charts or visualizations:"
                system_prompt += "- Directly analyze the data and provide insights"
                system_prompt += "- Describe what the visualization would show"
                system_prompt += "- Explain patterns and trends you observe"
                system_prompt += "- DO NOT provide code, tutorials, or instructions on how to create charts"
                system_prompt += "- The system will automatically generate the actual chart visualization for you"
                system_prompt += "- Focus on interpreting the data, not explaining how to visualize it"
                system_prompt += "\n\nExample of how to respond:"
                system_prompt += "User: 'Create a pie chart showing sales by region'"
                system_prompt += "Response: 'Here's a pie chart showing sales distribution by region. The West region has the highest sales at 45%, followed by the East region at 30%. The North and South regions contribute 15% and 10% respectively. This suggests the Western market is our strongest performing area.'"

            formatted_messages = provider.format_messages(history, system_prompt)

        ai_content = ""
        if provider_name == 'openai' and api_key and 'client' in locals():
            # Use legacy OpenAI client
            async for chunk in client.chat_completion(
                messages=formatted_messages,
                model=model,
                stream=True
            ):
                ai_content += chunk
                yield chunk
        else:
            # Use provider pattern
            stream = await provider.chat_completion(
                messages=formatted_messages,
                model=model,
                stream=True
            )
            async for chunk in stream:
                ai_content += chunk
                yield chunk

        # Update the message
        message.content = ai_content
        message.is_edited = True
        self.db.commit()
        self.db.refresh(message)

        # Detect and create chart visualization if requested (need to get user message)
        previous_user_msg = self.db.query(Message).filter(
            Message.session_id == session_id,
            Message.id < message_id,
            Message.role == "user"
        ).order_by(Message.id.desc()).first()

        if previous_user_msg:
            self._detect_and_create_chart(
                previous_user_msg.content,
                message.id,
                session_id
            )
        self.db.refresh(message)
