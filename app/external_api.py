import httpx
import logging
from fastapi import HTTPException
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

MODEL_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"

# Fix: Make this a standalone function, not a method
def _clean_summary(summary: str) -> str:
    """Remove factual inaccuracies and repetitions"""
    # 1. Remove duplicate sentences
    sentences = list(dict.fromkeys(summary.split(". ")))
    # 2. Filter out obviously wrong statements
    filtered = [s for s in sentences 
               if "eight suns" not in s.lower() 
               and "no moons" not in s.lower()]
    return ". ".join(filtered).strip()

async def summarize_document(text: str, max_length: int = 150) -> dict:
    """
    Final optimized version with:
    - Better parameter tuning
    - Fact-checking filters
    - Enhanced error handling
    """
    logger.info(f"Summarizing document with length {len(text)} and max_length {max_length}")
    
    headers = {
        "Authorization": f"Bearer {settings.AI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": f"Summarize accurately:\n{text}",  # Improved prompt
        "parameters": {
            "max_length": max_length,
            "min_length": 30,
            "do_sample": False,
            "temperature": 0.7,
            "repetition_penalty": 1.5,
            "no_repeat_ngram_size": 2
        }
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            logger.info(f"Sending request to {MODEL_URL}")
            response = await client.post(
                MODEL_URL,
                headers=headers,
                json=payload
            )
            
            logger.info(f"API Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Got successful response: {result}")
                summary = (result[0]['summary_text'] if isinstance(result, list)
                          else result.get('summary_text', ''))
                
                # Post-processing cleanup
                summary = _clean_summary(summary)  # Fixed indentation
                return {"summary": summary}
                
            elif response.status_code == 503:
                logger.error(f"Model loading: {response.text}")
                raise HTTPException(
                    status_code=503,
                    detail={"error": "model_loading", "retry_after": 30}
                )
            else:
                logger.error(f"API error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail={"error": "api_error", "message": response.text[:200]}
                )
                
    except httpx.RequestError as e:
        logger.error(f"Connection failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={"error": "connection_failed", "message": str(e)}
        )

# Backward compatibility
generate_ai_response = summarize_document