from enum import Enum
import re
from typing import Union
from pydantic import BaseModel, Field


class ParameterType(str, Enum):
    character = "<character>"
    location = "<location>"
    item = "<item>"
    amount = "<amount>"
    content = "<content>"
    other = "<other>"


class Object(BaseModel):
    name: str
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
    parameter_types: Union[list[ParameterType], dict] = (
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
    ) -> str:
        parts = [re.escape(self.name)]
        for param in self.parameter_types:
            # Each group name follows format: skillname_paramtype, without <>
            group_name = f"{self.name}_{param.value[1:-1]}"
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
    psychological_profile: str
