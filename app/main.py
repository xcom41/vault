from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.auth.router import router as auth_router
from app.graphql.schema import graphql_app

app = FastAPI(title="Vault")
app.include_router(auth_router)
app.mount("/graphql", graphql_app)
app.mount("/admin", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="admin")