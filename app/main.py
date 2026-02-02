from fastapi import FastAPI
from app.routes import account, counselor, group, alias

app = FastAPI(title="Counseling Service API")

app.include_router(account.router)
app.include_router(counselor.router)
app.include_router(group.router)
app.include_router(alias.router)
