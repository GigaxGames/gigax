import logging
from pydantic import BaseModel


logger = logging.getLogger("uvicorn")


class Quest(BaseModel):
    name: str
    description: str
    entity: str

    def __str__(self):
        return f"{self.name}: {self.description}. Entity: {self.entity}"


class QuestCompleted(BaseModel):
    name: str
    completed: bool = False

    def __str__(self):
        status = "completed" if self.completed else "not completed"
        return f"Quest '{self.name}' is {status}."
