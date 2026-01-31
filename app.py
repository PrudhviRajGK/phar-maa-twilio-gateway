"""
PHAR-MAA Twilio Gateway Service
Minimal webhook forwarder deployed on Render

WHY THIS EXISTS:
- Twilio requires a public webhook URL
- This service contains ZERO business logic
- All AI/DB/embeddings stay local (secure)
- Acts as a secure message forwarder only

SECURITY:
- No OpenAI keys
- No database credentials
- No sensitive logic
- Minimal attack surface

ARCHITECTURE:
[ Twilio ] → [ Render Gateway ] → [ Local Backend ] → [ Agents/AI/DB ]
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
import httpx
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Local backend URL (exposed via ngrok/Cloudflare Tunnel)
LOCAL_BACKEND_URL = os.getenv("LOCAL_BACKEND_URL")

if not LOCAL_BACKEND_URL:
    logger.warning("LOCAL_BACKEND_URL not set - gateway will not forward messages")

app = FastAPI(
    title="PHAR-MAA Twilio Gateway",
    description="Minimal webhook forwarder for Twilio messages",
    version="1.0.0"
)


@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "service": "PHAR-MAA Twilio Gateway",
        "status": "running",
        "backend_configured": LOCAL_BACKEND_URL is not None
    }


@app.get("/health")
def health():
    """Health check for Render"""
    return {"status": "healthy"}


@app.post("/twilio/whatsapp")
async def whatsapp_webhook(request: Request):
    """
    WhatsApp webhook forwarder
    
    IMPORTANT: This contains ZERO business logic
    - Receives Twilio webhook
    - Forwards to local backend
    - Returns acknowledgment
    
    All processing happens in local backend
    """
    try:
        # Parse Twilio form data
        form_data = await request.form()
        
        # Extract fields
        sender = form_data.get("From", "")
        body = form_data.get("Body", "")
        media_url = form_data.get("MediaUrl0")
        
        logger.info(f"WhatsApp message from {sender}")
        
        # Validate required fields
        if not sender:
            raise HTTPException(status_code=400, detail="Missing sender")
        
        # Prepare payload for local backend
        payload = {
            "sender": sender,
            "content": body or "",
            "channel": "whatsapp",
            "media_url": media_url
        }
        
        # Forward to local backend
        if LOCAL_BACKEND_URL:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{LOCAL_BACKEND_URL}/api/messages/ingest",
                    json=payload
                )
                
                logger.info(f"Forwarded to backend: {response.status_code}")
                
                # Get response from backend
                if response.status_code == 200:
                    backend_data = response.json()
                    reply_message = backend_data.get("response", "")
                    
                    # Return TwiML response
                    if reply_message:
                        return PlainTextResponse(
                            content=f'<?xml version="1.0" encoding="UTF-8"?>'
                                    f'<Response><Message>{reply_message}</Message></Response>',
                            media_type="application/xml"
                        )
        
        # Acknowledge receipt
        return PlainTextResponse(
            content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
            media_type="application/xml"
        )
    
    except Exception as e:
        logger.error(f"WhatsApp webhook error: {e}")
        # Return empty TwiML to avoid Twilio retries
        return PlainTextResponse(
            content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
            media_type="application/xml"
        )


@app.post("/twilio/sms")
async def sms_webhook(request: Request):
    """
    SMS webhook forwarder
    
    IMPORTANT: This contains ZERO business logic
    - Receives Twilio webhook
    - Forwards to local backend
    - Returns acknowledgment
    
    All processing happens in local backend
    """
    try:
        # Parse Twilio form data
        form_data = await request.form()
        
        # Extract fields
        sender = form_data.get("From", "")
        body = form_data.get("Body", "")
        
        logger.info(f"SMS message from {sender}")
        
        # Validate required fields
        if not sender:
            raise HTTPException(status_code=400, detail="Missing sender")
        
        # Prepare payload for local backend
        payload = {
            "sender": sender,
            "content": body or "",
            "channel": "sms"
        }
        
        # Forward to local backend
        if LOCAL_BACKEND_URL:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{LOCAL_BACKEND_URL}/api/messages/ingest",
                    json=payload
                )
                
                logger.info(f"Forwarded to backend: {response.status_code}")
                
                # Get response from backend
                if response.status_code == 200:
                    backend_data = response.json()
                    reply_message = backend_data.get("response", "")
                    
                    # Return TwiML response
                    if reply_message:
                        return PlainTextResponse(
                            content=f'<?xml version="1.0" encoding="UTF-8"?>'
                                    f'<Response><Message>{reply_message}</Message></Response>',
                            media_type="application/xml"
                        )
        
        # Acknowledge receipt
        return PlainTextResponse(
            content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
            media_type="application/xml"
        )
    
    except Exception as e:
        logger.error(f"SMS webhook error: {e}")
        # Return empty TwiML to avoid Twilio retries
        return PlainTextResponse(
            content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
            media_type="application/xml"
        )
