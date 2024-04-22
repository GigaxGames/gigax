import logging
import sys

from dotenv import load_dotenv
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.logger import logger as fastapi_logger

from step_NPC import get_input
from models import (
    Character,
    CharacterAction,
    Item,
    Location,
    ProtagonistCharacter,
)
from prompt import NPCPrompt

load_dotenv()

fastapi_logger.handlers = logging.getLogger("gunicorn.error").handlers
logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])

# FastAPI
app = FastAPI(root_path="/api")
origins = [
    "http://localhost",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


logger = logging.getLogger("uvicorn")
logging.basicConfig(level=logging.INFO)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    logging.error(f"{request}: {exc_str}")
    content = {"status_code": 10422, "message": exc_str, "data": None}
    return JSONResponse(
        content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


@app.post(
    "/step",
    response_description="Step the character",
    response_model=CharacterAction,
)
async def step(
    context: str,
    locations: list[Location],
    NPCs: list[Character],
    protagonist: ProtagonistCharacter,
    current_location: Location,
    items: list[Item],
    events: list[CharacterAction],
):
    # Format the prompt
    prompt = NPCPrompt(
        context=context,
        locations=locations,
        NPCs=NPCs,
        protagonist=protagonist,
        location=current_location,
        items=items,
        events=events,
    )

    # Get the NPC's input
    action = get_input(
        prompt,
        locations,
        NPCs,
        protagonist,
        items,
    )

    return action


@app.get("/health-check")
async def health_check():
    return {"status": "ok"}
