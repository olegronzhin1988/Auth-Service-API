# main.py file, contains app instance and main function to run app
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import engine, modulel
from config import Settings

# Decorated lifespan function, activates database connection
# on app/server launch
@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Connected to {Settings.POSTGRES_DB}")
    yield
    print(f"Disconnected to {Settings.POSTGRES_DB}")

# Creating app
app = FastAPI(lifespan = lifespan,
              title = "Auth-Service API",
              description = "Autentification API, create users with roles and check their access",
              version = '1.0.0')

# Connecting routers


# Default wellcome root GET endpoint
@app.get("/")
async def root():
    return {"message":"API app is on, wellcome!"}


# App autostart with uvicorn server.
# Localhost and port are set for local PC work only.
# Reload is turned on for adaptive change/reload.
if __name__ == "__main__":
    uvicorn.run("main:app",
                host = "127.0.0.1",
                port = 8000,
                reload = True)