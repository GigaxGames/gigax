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


class Location(BaseModel):
    name: str
    description: str

    def __str__(self):
        return f"{self.name}: {self.description}"


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
        authorized_characters: list[str],
        authorized_locations: list[str],
        authorized_items: list[str],
    ) -> str:
        """
        Generate a regex string for a skill command based on current context.
        """
        parts = [self.name]  # Start with the command name
        for param in self.parameter_types:
            if param == ParameterType.character:
                parts.append(
                    r"(" + "|".join(map(re.escape, authorized_characters)) + ")"  # type: ignore
                )
            elif param == ParameterType.location:
                parts.append(
                    r"(" + "|".join(map(re.escape, authorized_locations)) + ")"  # type: ignore
                )
            elif param == ParameterType.item:
                parts.append(r"(" + "|".join(map(re.escape, authorized_items)) + ")")  # type: ignore
            elif param == ParameterType.amount:
                parts.append(r"(\d+)")
            elif param == ParameterType.content:
                parts.append(r'("([^"]*)")')  # Match content within quotes

        return r"\s".join(parts)


class Character(BaseModel):
    """
    Describes a character in the game world, i.e. an adventurer or an NPC.
    """

    name: str
    description: str
    current_location: Location

    # Add a way to print the location (name: description)
    def __str__(self):
        return f"{self.name}: {self.description}"


class ProtagonistCharacter(Character):
    memories: list[str] = Field(..., description="Memories that the character has.")
    quests: list[str] = Field(..., description="Quests that the character is on.")
    skills: list[Skill] = Field(..., description="Skills that the character can use.")
    psychological_profile: str


class Item(BaseModel):
    name: str
    description: str

    def __str__(self):
        return f"{self.name}: {self.description}"


class CharacterAction(BaseModel):
    command: str
    protagonist: Character
    target: Optional[Character | Item | Location] = None
    content: Optional[str] = None
    amount: Optional[int] = None

    def __str__(self) -> str:
        """
        Print the action according to the training format: cmd_name param1 param2.
        e.g.: Alice: say Bob "Hello, how are you"
        """
        parts = [f"{self.protagonist.name}:", self.command]
        if self.target:
            parts.append(str(self.target.name))
        if self.content:
            parts.append(f'"{self.content}"')
        if self.amount:
            parts.append(str(self.amount))
        return " ".join(parts)


if __name__ == "__main__":
    # Context as given
    authorized_characters = ["‘Lucky’ Louie", "Bob le bricoleur", "Charlie"]
    authorized_locations = ["Forest", "Castle", "Town"]
    authorized_items = ["Sword", "Shield", "Potion"]

    # Define skills as provided
    skills = [
        Skill(
            name="say",
            parameter_types=[ParameterType.character, ParameterType.content],
            description="Say something.",
        ),
        Skill(
            name="move", parameter_types=[ParameterType.location], description="Move."
        ),
        Skill(name="grab", parameter_types=[ParameterType.item], description="Grab."),
        Skill(
            name="give_coins",
            parameter_types=[ParameterType.character, ParameterType.amount],
            description="Give coins.",
        ),
    ]

    # Test input and expected outputs
    test_commands = [
        'say Alice "Hello, how are you"',
        'say ‘Lucky’ Louie "Hello, how are you"',
        "move Forest",
        "grab Sword",
        "give_coins Bob le bricoleur 100",
        "say Bob",  # Should fail, incomplete
        "move Dungeon",  # Should fail, invalid location
        "grab Forest",  # Should fail, invalid item
        "give_coins ten",  # Should fail, invalid amount
        "give_coins",
    ]

    # Generate a combined regex pattern for all skills
    combined_regex_parts = [
        skill.to_regex(authorized_characters, authorized_locations, authorized_items)
        for skill in skills
    ]
    combined_regex = "|".join(combined_regex_parts)
    compiled_combined_regex = re.compile(combined_regex, re.IGNORECASE)

    # Perform tests with combined regex
    print(f"Compiled combined regex: {compiled_combined_regex}")
    print("Testing commands with combined skills regex:")
    for command in test_commands:
        matches = compiled_combined_regex.match(command)
        if matches:
            print(f"Valid command: {command}")
        else:
            print(f"Invalid command: {command}")
