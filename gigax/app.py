import logging
import os
import uvicorn
import sys

from dotenv import load_dotenv
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.logger import logger as fastapi_logger
from pydantic import BaseModel

from gigax.parse import CharacterAction, ProtagonistCharacter
from gigax.scene import (
    Character,
    Item,
    Location,
)
from gigax.step import NPCStepper

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


class CharacterActionRequest(BaseModel):
    context: str
    locations: list[Location]
    NPCs: list[Character]
    protagonist: ProtagonistCharacter
    items: list[Item]
    events: list[CharacterAction]


@app.post(
    "/step",
    response_description="Step the character",
    response_model=CharacterAction,
)
async def step(
    request: CharacterActionRequest,
) -> CharacterAction:
    # Format the prompt
    stepper = NPCStepper(model="llama_3_regex", api_key=os.getenv("API_KEY"))

    action = await stepper.get_action(
        context=request.context,
        locations=request.locations,
        NPCs=request.NPCs,
        protagonist=request.protagonist,
        items=request.items,
        events=request.events,
    )
    if action is None:
        raise ValueError("No action returned from the model")

    return action


@app.get("/health-check")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("__main__:app", host="0.0.0.0", port=5678, reload=True, workers=5)
