from fastapi import FastAPI
from registration import router as reg_router
# from tasks import router as task_router

app = FastAPI()

app.include_router(reg_router)
# app.include_router(task_router)