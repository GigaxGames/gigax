from enum import Enum
import logging
import re

from models import CharacterAction, Item, Skill
from models import Location
from models import ProtagonistCharacter, Character
from models import ParameterType

logger = logging.getLogger("uvicorn")


class ActionParsingError(Exception):
    pass


def create_dynamic_enum(name: str, options: list[str]) -> Enum:
    """Dynamically creates an Enum based on the given name and options."""
    enum_name = name.capitalize()
    return Enum(
        enum_name,
        {option.upper().replace(" ", "_"): option for option in options},
    )


def parse_action(
    command_str: str,
    protagonist: Character,
    valid_characters: list[Character],
    valid_locations: list[Location],
    valid_items: list[Item],
    compiled_regex: re.Pattern,
) -> CharacterAction:
    match = compiled_regex.match(command_str)
    if not match:
        raise ValueError("Invalid command format")

    if match.lastgroup is None:
        raise ValueError(
            f"Could not find a matching skill in command_str {command_str}"
        )

    command = match.lastgroup.split("_")[0]  # Extract command name
    action = CharacterAction(command=command, protagonist=protagonist, parameters=[])

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


if __name__ == "__main__":
    # Example usage of the function
    context = "A vast open world full of mystery and adventure."
    locations = [Location(name="Old Town", description="A quiet and peaceful town.")]
    NPCs = [
        Character(
            name="John the Brave",
            description="A fearless warrior",
            current_location=locations[0],
        )
    ]
    protagonist = ProtagonistCharacter(
        name="Aldren",
        description="Brave and curious",
        current_location=locations[0],
        memories=["Saved the village", "Lost a friend"],
        quests=["Find the ancient artifact", "Defeat the evil warlock"],
        skills=[
            Skill(
                name="attack",
                description="Deliver a powerful blow",
                parameter_types=[ParameterType.character],
            ),
            Skill(
                name="say",
                description="Speak to a character",
                parameter_types=[
                    ParameterType.character,
                    ParameterType.content,
                ],
            ),
        ],
        psychological_profile="Determined and compassionate",
    )
    items = [Item(name="Sword", description="A sharp blade")]
    events = [
        CharacterAction(
            command="Attack",
            protagonist=protagonist,
            parameters=[
                "John the Brave",
            ],
        )
    ]

    # Assuming 'compiled_combined_regex' is already defined as per previous discussion
    test_command = 'say John the Brave "Hello, how are you"'
    compiled_combined_regex = protagonist.get_combined_regex(NPCs, locations, items)
    try:
        print(
            parse_action(
                test_command,
                protagonist,
                NPCs,
                locations,
                items,
                compiled_combined_regex,
            )
        )
    except ValueError as e:
        print(e)
