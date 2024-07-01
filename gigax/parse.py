"""This module contains the logic to parse a command string into a CharacterAction object."""

import logging
import re
from typing import Union

from pydantic import BaseModel

from gigax.scene import (
    Item,
    Location,
    Character,
    ProtagonistCharacter,
    Skill,
)

logger = logging.getLogger("uvicorn")


class ActionParsingError(Exception):
    """Exception raised for errors in the action parsing."""

    pass


class CharacterAction(BaseModel):
    """CharacterAction class to represent a character action."""

    command: str
    protagonist: ProtagonistCharacter
    parameters: list[Union[str, int]]

    def __str__(self) -> str:
        """
        Print the action according to the training format: cmd_name param1 param2.
        e.g.: Alice: say Bob "Hello, how are you"
        """
        return f"{self.protagonist.name}: {self.command} {' '.join(map(str, self.parameters))}"

    @staticmethod
    def from_str(
        command_str: str,
        protagonist: ProtagonistCharacter,
        compiled_regex: re.Pattern,
    ) -> "CharacterAction":
        """
        Parse a command string into a CharacterAction object.
        """

        match = compiled_regex.match(command_str)
        if not match:
            raise ValueError("Invalid command format")

        if match.lastgroup is None:
            raise ValueError(
                f"Could not find a matching skill in command_str '{command_str}'"
            )

        # Extract the command_name while supporting multiple _ in lastgroup
        command = "_".join(match.lastgroup.split("_")[:-1])
        action = CharacterAction(
            command=command, protagonist=protagonist, parameters=[]
        )

        # Extract parameters based on their named groups
        for group_name, value in match.groupdict().items():
            if not value:
                continue

            param_type = group_name[
                len(f"{command}_") :
            ]  # Remove command prefix to get parameter type

            # Add parameters based on their type
            if param_type in ["character", "NPC", "item"]:
                # Assuming these are directly referred by name
                action.parameters.append(value)
            elif param_type == "amount":
                action.parameters.append(int(value))
            elif param_type == "content":
                # Remove quotation marks if present
                action.parameters.append(value.strip('"'))

        return action


def get_guided_regex(
    skills: list[Skill],
    authorized_characters: list[Character],
    authorized_locations: list[Location],
    authorized_items: list[Item],
) -> re.Pattern:
    """
    Generate a combined regex pattern for all the skills of the protagonist.
    """
    # Get names of al authorized characters, locations, and items
    characters_names = [char.name for char in authorized_characters]
    locations_names = [loc.name for loc in authorized_locations]
    items_names = [item.name for item in authorized_items]

    # Generate a combined regex pattern for all skills
    combined_regex_parts = [
        skill.to_regex(characters_names, locations_names, items_names)
        for skill in skills
    ]
    combined_regex = "|".join(combined_regex_parts)
    return re.compile(combined_regex, re.IGNORECASE)
