from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult
from app.configs.celery import celery

router = APIRouter(prefix="/api/v1")

@router.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    try:
        task_result = AsyncResult(task_id, app=celery)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid task_id")

    # If Redis lost the result or task never existed
    if task_result.state == "PENDING" and task_result.result is None:
        return {
            "task_id": task_id,
            "status": "PENDING",
            "result": None,
            "message": "Task not started or invalid task_id",
        }

    # If the task failed, don't send full traceback to the client
    if task_result.state == "FAILURE":
        return {
            "task_id": task_id,
            "status": "FAILURE",
            "result": None,
            "error": str(task_result.result)[:300],  # sanitize long tracebacks
        }

    # Task success or running states
    safe_result = (
        task_result.result
        if isinstance(
            task_result.result, (dict, list, str, int, float, bool, type(None))
        )
        else str(task_result.result)
    )

    return {"task_id": task_id, "status": task_result.state, "result": safe_result}
