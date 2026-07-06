import os
import sys
import json
import asyncio
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Add parent directory to sys.path to resolve orchestrator and agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from google.adk.runners import InMemoryRunner
from google.genai import types
from orchestrator.agent import orchestrator_agent
from security import approval
from tools import get_tasks, get_calendar_events, get_task_reminders
from rag.ingest import ingest

app = FastAPI(title="Atlas Chief of Staff Web Interface")

# Mount static files
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

# REST endpoints for dashboard sidebar data
@app.get("/api/tasks")
def read_tasks():
    try:
        return json.loads(get_tasks())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/calendar")
def read_calendar():
    try:
        return json.loads(get_calendar_events())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reminders")
def read_reminders():
    try:
        return json.loads(get_task_reminders())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    # Save the file temporarily
    temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "demo_data")
    os.makedirs(temp_dir, exist_ok=True)
    
    file_path = os.path.join(temp_dir, file.filename)
    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        # Run RAG ingestion
        result = ingest(file_path)
        if result.startswith("Error"):
            raise HTTPException(status_code=500, detail=result)
        return {"status": "success", "detail": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket Endpoint for streaming chat and active approval gates
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    
    runner = InMemoryRunner(agent=orchestrator_agent, app_name="atlas-chief-of-staff")
    user_id = "student_1"
    
    try:
        session = await runner.session_service.create_session(
            app_name="atlas-chief-of-staff",
            user_id=user_id
        )
        session_id = session.id
    except AttributeError:
        session_id = "session_1"
        
    approval_event = None
    approval_response_value = False
    
    async def ws_approval_hook(action_desc: str) -> bool:
        nonlocal approval_event, approval_response_value
        approval_event = asyncio.Event()
        # Send approval request packet to client
        await websocket.send_json({
            "type": "approval_request",
            "description": action_desc
        })
        # Wait for client to approve/deny via WebSocket
        await approval_event.wait()
        return approval_response_value

    # Register our async approval gate handler
    approval.async_approval_hook = ws_approval_hook
    
    try:
        while True:
            data = await websocket.receive_json()
            
            # 1. Handle user typing responses to approval requests
            if data.get("type") == "approval_response":
                approval_response_value = data.get("approved", False)
                if approval_event:
                    approval_event.set()
                continue
            
            # 2. Handle user messages
            if data.get("type") == "message":
                query = data.get("text", "").strip()
                if not query:
                    continue
                
                user_message = types.Content(
                    parts=[types.Part(text=query)],
                    role="user"
                )
                
                try:
                    async for event in runner.run_async(
                        user_id=user_id,
                        session_id=session_id,
                        new_message=user_message
                    ):
                        if getattr(event, "content", None) and event.content.parts:
                            for part in event.content.parts:
                                if part.text:
                                    await websocket.send_json({
                                        "type": "token",
                                        "text": part.text
                                    })
                    # Signal completion of stream
                    await websocket.send_json({"type": "done"})
                except Exception as e:
                    err_msg = str(e)
                    err_msg_lower = err_msg.lower()
                    if "quota" in err_msg_lower or "limit" in err_msg_lower or "429" in err_msg_lower or "exhausted" in err_msg_lower:
                        clean = "API quota exceeded or rate limited. Please try again in a few minutes."
                    elif "connection" in err_msg_lower or "timeout" in err_msg_lower or "aborted" in err_msg_lower:
                        clean = "Connection aborted or network timeout. Please check your connection."
                    else:
                        clean = err_msg.split('\n')[0].strip()
                    await websocket.send_json({
                        "type": "error",
                        "text": clean
                    })
    except WebSocketDisconnect:
        pass
    finally:
        # Deregister approval hook
        approval.async_approval_hook = None

app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web.server:app", host="127.0.0.1", port=8000, reload=True)
