from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth as auth_router, users as users_router, contacts as contacts_router
from .config import APP_HOST

app = FastAPI(title="Contacts API")

# CORS (allow all for dev; tighten in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(contacts_router.router)

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Contacts API is running. See /docs for interactive API docs."}


# poetry run uvicorn contacts_api.main:app --reload
# docker-compose up --build - запуск з докер файлу
# docker-compose down --volumes - видалити всі дані
# cd contacts_api
# http://127.0.0.1:8000/docs - переходити після запуску сервера!!!