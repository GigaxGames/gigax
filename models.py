from enum import Enum
import re
from typing import Optional, Union
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
    pass


class Item(Object):
    pass


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
    ):
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
        regex = r"\s+".join(parts)
        return regex


class Character(Object):
    """
    Describes a character in the game world, i.e. an adventurer or an NPC.
    """

    current_location: Location


class ProtagonistCharacter(Character):
    memories: list[str] = Field(..., description="Memories that the character has.")
    quests: list[str] = Field(..., description="Quests that the character is on.")
    skills: list[Skill] = Field(..., description="Skills that the character can use.")
    psychological_profile: str

    def get_combined_regex(
        self,
        authorized_characters: list[Character],
        authorized_locations: list[Location],
        authorized_items: list[Item],
    ) -> re.Pattern:
        """
        Generate a combined regex pattern for all skills.
        """
        # Get names of al authorized characters, locations, and items
        characters_names = [char.name for char in authorized_characters]
        locations_names = [loc.name for loc in authorized_locations]
        items_names = [item.name for item in authorized_items]

        # Generate a combined regex pattern for all skills
        combined_regex_parts = [
            skill.to_regex(characters_names, locations_names, items_names)
            for skill in self.skills
        ]
        combined_regex = "|".join(combined_regex_parts)
        return re.compile(combined_regex, re.IGNORECASE)


class CharacterAction(BaseModel):
    command: str
    protagonist: Character
    parameters: list[Union[str, int, Object]]

    def __str__(self) -> str:
        """
        Print the action according to the training format: cmd_name param1 param2.
        e.g.: Alice: say Bob "Hello, how are you"
        """
        return f"{self.protagonist.name}: {self.command} {' '.join(map(str, self.parameters))}"
