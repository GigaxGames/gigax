from enum import Enum
import re
from typing import Annotated
from pydantic import BaseModel, Field, StringConstraints


class ParameterType(str, Enum):
    character = "character"
    location = "location"
    item = "item"
    amount = "amount"
    content = "content"
    entity = "entity"
    quest = "quest"
    boolean = "boolean"
    other = "other"


class Object(BaseModel):
    name: Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]
    description: str

    def __str__(self):
        return f"{self.name}"

    def to_training_format(self) -> str:
        """
        Print the character according to the training format.
        """
        return f"{self.name}: {self.description}"


class Location(Object):
    """
    Describes a location in the game world, i.e. a town, a forest, etc.
    """

    pass


class Item(Object):
    """
    Describes an item in the game world, i.e. a sword, a potion, etc.
    """

    pass


class Character(Object):
    """
    Describes a character in the game world, i.e. an adventurer or an NPC.
    """

    current_location: Location


class Skill(BaseModel):
    """
    Model for a skill that can be performed by a character.
    e.g. "say <character> <content>", "move <location>", etc.
    """

    name: str = Field(..., description="Skill name")
    description: str = Field(..., description="Skill description")
    parameter_types: list[ParameterType] = (
        Field(  # This is a Union because Cubzh's Lua sends empty lists as empty dicts
            [], description="Allowed parameter types for the given skill"
        )
    )

    def to_training_format(self) -> str:
        """
        Print the action according to our training format: cmd_name <param_type1> <param_type2>
        e.g.: say <character> <content> : Say something.
        """
        return f"{self.name} {' '.join(self.parameter_types)} : {self.description}"

    def to_regex(
        self,
        character_names: list[str],
        location_names: list[str],
        item_names: list[str],
        quests_names: list[str] = [],
    ) -> str:
        parts = [re.escape(self.name)]
        for i, param in enumerate(self.parameter_types):
            # Each group name follows format: skillname_paramtype, without <>
            group_name = f"{self.name}_{param.value}_{i}"
            if param == ParameterType.character:
                parts.append(
                    f"(?P<{group_name}>{'|'.join(map(re.escape, character_names))})"
                )
            elif param == ParameterType.location:
                parts.append(
                    f"(?P<{group_name}>{'|'.join(map(re.escape, location_names))})"
                )
            elif param == ParameterType.item:
                parts.append(
                    f"(?P<{group_name}>{'|'.join(map(re.escape, item_names))})"
                )
            elif param == ParameterType.entity:
                parts.append(
                    f"(?P<{group_name}>{'|'.join(map(re.escape, character_names + location_names + item_names))})"
                )
            elif param == ParameterType.quest:
                parts.append(
                    f"(?P<{group_name}>{'|'.join(map(re.escape, quests_names))})"
                )
            elif param == ParameterType.boolean:
                parts.append(f"(?P<{group_name}>true|false)")
            elif param == ParameterType.amount:
                parts.append(f"(?P<{group_name}>\\d+)")
            elif param == ParameterType.content:
                parts.append(
                    f'(?P<{group_name}>"[^"]*")'
                )  # Match content within quotes
        return r"\s+".join(parts)


class ProtagonistCharacter(Character):
    memories: list[str] = Field(..., description="Memories that the character has.")
    quests: list[str] = Field(..., description="Quests that the character is on.")
    skills: list[Skill] = Field(..., description="Skills that the character can use.")


class NarratorCharacter(Object):
    """
    Describes a narrator character in the game world.
    """

    skills: list[Skill] = Field(..., description="Skills that the narrator can use.")
    quests: list[str] = Field(
        ...,
        description="Quests given by this narrator to the player, that are currently active.",
    )
    completed_quests: list[str] = Field(
        ...,
        description="Quests given by the narrator that the Player has completed.",
        alias="completedQuests",
    )
