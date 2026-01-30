from agno.agent import Agent
from agno.models.google import Gemini
from agno.db.sqlite import SqliteDb
from app.services.knowledge import KnowledgeBaseService
from app.core.config import settings
import logging
import os

logger = logging.getLogger(__name__)

class ChatbotAgent:
    def __init__(self, session_id: str = "default"):
        self.knowledge_service = KnowledgeBaseService()
        self.session_id = session_id
        
        # Ensure data directory exists for the database
        os.makedirs("data", exist_ok=True)
        
        # Initialize SQLite Database
        self.db = SqliteDb(db_file="data/sessions.db")
        
        # Define strict instructions for RAG
        instructions = (
            "You are a highly precise assistant designed to answer questions based **exclusively** on the provided website context. "
            "Your goal is to be helpful but strictly grounded in the retrieved information. "
            "\n\n"
            "**Core Rules:**\n"
            "1. **Search First:** Always prioritize searching the knowledge base for the user's query.\n"
            "2. **Strict Grounding:** Answer *only* using facts explicitly present in the retrieved search results. "
            "Do NOT use your internal training data, general knowledge, or assumptions.\n"
            "3. **Negative Constraint (CRITICAL):** If the specific answer is not found in the context, "
            "you **MUST** return strictly the following sentence and nothing else: "
            "'The answer is not available on the provided website.'\n"
            "4. **Verification:** Before answering, ask yourself: 'Is this information explicitly stated in the context?' "
            "If the answer is 'No', use the negative constraint phrase.\n"
            "5. **No Hallucination:** Do not make up links, dates, or facts.\n"
            "6. **Context Awareness:** Use the conversation history to understand follow-up questions, but the answer source must still be the website content."
        )

        self.agent = Agent(
            model=Gemini(id="gemini-2.5-flash", api_key=settings.GOOGLE_API_KEY),
            knowledge=self.knowledge_service.knowledge_base,
            search_knowledge=True, # Enable RAG
            instructions=instructions,
            # Use 'db' parameter for SqliteDb storage
            db=self.db,
            num_history_sessions=5, # Limit history
            session_id=session_id,
            markdown=True
        )

    def ask(self, query: str) -> str:
        # Agent.print_response prints to stdout, use run() or response() to get object
        # usually .run() returns a RunResponse or similar. 
        # .get_response() might be the method.
        # Check Agno docs: agent.run(message) -> response.content usually.
        # Or agent.print_response(..., stream=False) returns None?
        # Use agent.run() for programmatic access.
        
        try:
            logger.info(f"Agent asking query: {query}")
            response = self.agent.run(query)
            logger.info("Agent received response")
            return response.content
        except Exception as e:
            logger.error(f"Error asking agent: {e}")
            raise e
