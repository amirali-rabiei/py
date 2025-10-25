from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from enum import Enum
from typing import Annotated

# ----- Database -----
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

# ----- Enums -----
class blog_lan(str, Enum):
    english = "english"
    arabic = "arabic"
    persion = "persion"

# ----- Models -----
class Blog(SQLModel, table=True):
    blog_id: int | None = Field(default=None, primary_key=True)
    title: str = Field(default="no title", index=True)
    content: str = "default content"
    publisher: str = "admin"
    img: str | None = None
    created_at: str | None = None
    language: str

# ----- App -----
app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def index():
    return {'data': "index"}

@app.get("/api/blogs")
def all_blog(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100
) -> list[Blog]:
    return session.exec(select(Blog).offset(offset).limit(limit)).all()

@app.get("/api/blogs/{blog_id}")
def show_with_id(session: SessionDep, blog_id: int) -> Blog:
    get_blog = session.get(Blog, blog_id)
    if not get_blog:
        raise HTTPException(status_code=404, detail=f"blog not found with id: {blog_id}")
    return get_blog

@app.post('/api/blog')
def create_blog(blog: Blog, session: SessionDep) -> Blog:
    session.add(blog)
    session.commit()
    session.refresh(blog)
    return {'data': blog}

@app.delete("/api/blogs/{blog_id}")
def delete_blog(session: SessionDep, blog_id: int):
    get_blog = session.get(Blog, blog_id)
    if not get_blog:
        raise HTTPException(status_code=404, detail=f"blog not found with id: {blog_id}")
    session.delete(get_blog)
    session.commit()
    return {"ok": True}

