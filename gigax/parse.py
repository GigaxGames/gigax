import logging
import re
from typing import Union

from pydantic import BaseModel

from gigax.scene import (
    Item,
    Object,
    Location,
    Character,
    ProtagonistCharacter,
    Skill,
)

logger = logging.getLogger("uvicorn")


class ActionParsingError(Exception):
    pass


class CharacterAction(BaseModel):
    command: str
    protagonist: ProtagonistCharacter
    parameters: list[Union[str, int, Object]]

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
        valid_characters: list[Character],
        valid_locations: list[Location],
        valid_items: list[Item],
        compiled_regex: re.Pattern,
    ) -> "CharacterAction":
        match = compiled_regex.match(command_str)
        if not match:
            raise ValueError("Invalid command format")

        if match.lastgroup is None:
            raise ValueError(
                f"Could not find a matching skill in command_str '{command_str}'"
            )

        command = match.lastgroup.split("_")[0]  # Extract command name
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
            if param_type == "character":
                # Assuming characters are directly referred by name
                action.parameters.append(
                    next(char for char in valid_characters if char.name == value),
                )
            elif param_type == "location":
                action.parameters.append(
                    next(loc for loc in valid_locations if loc.name == value),
                )
            elif param_type == "item":
                action.parameters.append(
                    next(item for item in valid_items if item.name == value)
                )
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
