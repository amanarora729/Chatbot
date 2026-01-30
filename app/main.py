from fastapi import FastAPI, HTTPException
from app.models.schemas import CrawlRequest, CrawlResponse, ChatRequest, ChatResponse
from app.services.crawler import CrawlerService
from app.services.knowledge import KnowledgeBaseService
from app.agents.chatbot import ChatbotAgent
from typing import Dict
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Website RAG Chatbot")

# In-memory storage for active agents to maintain session state (Short-term memory)
# Key: session_id, Value: ChatbotAgent instance
active_agents: Dict[str, ChatbotAgent] = {}

crawler_service = CrawlerService()
# Initialize KnowledgeBaseService once to ensure DB setup
knowledge_service = KnowledgeBaseService()

@app.post("/crawl", response_model=CrawlResponse)
async def crawl_website(request: CrawlRequest):
    url = str(request.url)
    logger.info(f"Received crawl request for: {url}")
    try:
        # 1. Crawl and Clean
        chunks = crawler_service.process_url(url)
        
        # 2. Insert into Knowledge Base
        logger.info("Inserting chunks into Knowledge Base")
        knowledge_service.insert_chunks(chunks)
        
        return CrawlResponse(
            message=f"Successfully crawled and indexed {url}",
            chunks_count=len(chunks)
        )
    except ValueError as e:
        # User Errors: 404 (Not Found), 415 (Unsupported Type), Empty Content
        logger.warning(f"Crawl validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except ConnectionError as e:
        # Connectivity Errors: DNS, Timeout, Refused
        logger.error(f"Crawl connection error: {e}")
        raise HTTPException(status_code=400, detail=str(e)) # 400 because user likely provided a bad URL
    except Exception as e:
        # Internal Errors
        logger.error(f"Unexpected crawl error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected internal error occurred.")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    session_id = request.session_id
    logger.info(f"Chat request for session {session_id}: {request.query}")
    
    # Retrieve or create agent for this session
    if session_id not in active_agents:
        logger.info(f"Creating new agent for session {session_id}")
        active_agents[session_id] = ChatbotAgent(session_id=session_id)
    
    agent = active_agents[session_id]
    
    try:
        # Get answer
        answer = agent.ask(request.query)
        return ChatResponse(answer=str(answer))
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ok"}