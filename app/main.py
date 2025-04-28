import uuid
import asyncio
from fastapi import FastAPI, BackgroundTasks, Depends, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.models import Task
from app.tasks import generate_embedding_task
from app.database import get_db


class TaskRequest(BaseModel):
    text: str


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def get_html():
    with open("app/static/index.html", "r") as f:
        return f.read()


@app.post("/start-task/")
async def start_task(request: TaskRequest,
                     background_tasks: BackgroundTasks,
                     db: Session = Depends(get_db)):
    task_id = str(uuid.uuid4())
    new_task = Task(id=task_id, status='pending', result=None)
    db.add(new_task)
    db.commit()
    background_tasks.add_task(generate_embedding_task, db, task_id,
                              request.text)
    return {"task_id": task_id}


@app.get("/check-task/{task_id}")
async def check_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        return {"status": task.status, "result": task.result}
    return {"error": "Task not found"}


@app.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket,
                             task_id: str,
                             db: Session = Depends(get_db)):
    await websocket.accept()
    while True:
        task = db.query(Task).filter(Task.id == task_id).first()
        if task and task.status in ['done', 'failed']:
            await websocket.send_json({
                "status": task.status,
                "result": task.result
            })
            break
        await websocket.send_json({"status": "processing"})
        await asyncio.sleep(1)
