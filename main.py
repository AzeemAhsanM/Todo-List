from fastapi import FastAPI
from app.database import models
from app.database.db import engine
from app.routes import auth, todo

# This command creates the database tables based on your models
# It will not delete or modify existing tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Todo List API with Auth",
    description="A simple API for managing user-specific todo lists.",
    version="1.0.0"
)

# Include the routers from the routes directory
# All routes from auth.py will be prefixed with /api
# All routes from todos.py will be prefixed with /api
app.include_router(auth.router, prefix="/api")
app.include_router(todo.router, prefix="/api")

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Todo List API!"}
