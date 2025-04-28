from sqlalchemy.orm import Session
from app.models import Task
from app.qdrant_client import qdrant_client
from langchain_huggingface import HuggingFaceEmbeddings

embed_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

async def generate_embedding_task(db: Session, task_id: str, text: str):
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = 'processing'
            db.commit()

        vector = embed_model.embed_query(text)

        qdrant_client.upsert(
            collection_name="embeddings_collection",
            points=[{
                "id": task_id,
                "vector": vector,
                "payload": {"text": text}
            }]
        )

        task.status = 'done'
        task.result = "Success"
        db.commit()

    except Exception as e:
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = 'failed'
            task.result = str(e)
            db.commit()
