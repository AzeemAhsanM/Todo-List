from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import models
from ..database.db import SessionLocal
from .auth import get_current_active_user
from pydantic import BaseModel

# Setup
router = APIRouter(
    prefix="/todos",
    tags=["Todos"]
)


# Pydantic Models
class TodoCreate(BaseModel):
    title: str
    description: str | None = None


class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


class TodoOut(BaseModel):
    id: int
    title: str
    description: str | None
    completed: bool
    owner_id: int

    class Config:
        from_attributes = True


#Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#Helper Function
def get_todo_for_user(db: Session, todo_id: int, user_id: int):

    #Helper to retrieve a specific todo for the current user..

    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    if todo.owner_id != user_id:
        # Raise 404 instead of 403 to avoid revealing the existence of the resource
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return todo


# --- Endpoints ---
@router.post("/", response_model=TodoOut, status_code=status.HTTP_201_CREATED)
def create_todo(
        todo: TodoCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_active_user)
):

    #Create a new todo item for the currently authenticated user.
    db_todo = models.Todo(**todo.model_dump(), owner_id=current_user.id)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo


@router.get("/", response_model=List[TodoOut])
def read_user_todos(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_active_user)
):

    #Retrieve all todo items for the currently authenticated user.
    return db.query(models.Todo).filter(models.Todo.owner_id == current_user.id).all()


@router.put("/{todo_id}", response_model=TodoOut)
def update_todo(
        todo_id: int,
        todo_update: TodoUpdate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_active_user)
):


    #Update a specific todo item for the current user.

    db_todo = get_todo_for_user(db, todo_id, current_user.id)

    update_data = todo_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_todo, key, value)

    db.commit()
    db.refresh(db_todo)
    return db_todo


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
        todo_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_active_user)
):

    #Delete a specific todo item for the current user. 🗑️

    db_todo = get_todo_for_user(db, todo_id, current_user.id)

    db.delete(db_todo)
    db.commit()

    # No response body is sent for 204 status code
    return None
