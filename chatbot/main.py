from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers.indexing import indexing
from api.routers.chatbot import chatbot

app = FastAPI(title="Chatbot API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(indexing)
app.include_router(chatbot)