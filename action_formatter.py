from enum import Enum
import json
import logging
import time
import traceback
from typing import Union
from pydantic import ValidationError, create_model

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


def generate_typed_skill_model(
    character: ProtagonistCharacter,
    valid_characters: list[Character],
    valid_locations: list[Location],
    valid_items: list[Item],
):
    """
    Dynamically generates a Pydantic model for the given character's skills.
    Used for constraining the output of the LLM using following schema:
    {'action': {'command': 'give_coin', 'parameters': {'character': 'asdfa4', 'amount': 4}}}
    Could not get rid of "action" key - alternative is a OneOf key which failed in our tests.
    """
    skills = []
    formatted_characters = [char.name.lower() for char in valid_characters]
    formatted_locations = [loc.name.lower() for loc in valid_locations]
    formatted_items = [it.name.lower() for it in valid_items]

    for skill in character.skills:

        # Dynamically create the enums for the parameter's authorized values
        parameters = {}
        for p in skill.parameter_types:
            if p == ParameterType.character:
                character_enum = create_dynamic_enum("character", formatted_characters)
                parameters["character"] = (character_enum, ...)
            elif p == ParameterType.location:
                location_enum = create_dynamic_enum("location", formatted_locations)
                parameters["location"] = (location_enum, ...)
            elif p == ParameterType.item:
                item_enum = create_dynamic_enum("item", formatted_items)
                parameters["item"] = (item_enum, ...)
            elif p == ParameterType.amount:
                parameters["amount"] = (int, ...)
            elif p == ParameterType.content:
                parameters["content"] = (str, ...)

        # Dynamically create the parameters class
        params_class = create_model("parameters", **parameters)

        # Create the command enum
        command_enum = (create_dynamic_enum("command", [skill.name]), ...)

        # Fuse the enums and create the skill model
        skills.append(
            create_model(
                skill.name, command=command_enum, parameters=(params_class, ...)
            )
        )

    # Dynamically create a Union of the action types
    union_of_actions = Union[tuple(skills)]  # type: ignore
    return create_model("Actions", action=(union_of_actions, ...))


def parse_action(
    character: ProtagonistCharacter,
    raw_action_json: str,
    valid_characters: list[Character],
    valid_locations: list[Location],
    valid_items: list[Item],
) -> CharacterAction:
    start_time = time.time()
    # Generate the dynamic Pydantic model for actions
    ActionsModel = generate_typed_skill_model(
        character, valid_characters, valid_locations, valid_items
    )

    try:
        # Parse and validate the action using the generated Pydantic model
        action_json = json.loads(raw_action_json)
        action_parsed = ActionsModel(**action_json)

        # Access the command and parameters; ignoring type errors for simplicity
        command = action_parsed.action.command.value  # type: ignore

        if command not in [s.name for s in character.skills]:
            raise ValueError("Invalid command")

        target = None
        content = None

        # Cast parameters to dict for easier access
        for (
            param_type,
            param_value,
        ) in action_parsed.action.parameters.dict().items():  # type: ignore
            if param_type == ParameterType.character.value:
                param_value = param_value.value
                # Find the character_id based on the character name, using valid_characters
                target = next(
                    char
                    for char in valid_characters
                    if char.name.lower() == param_value.lower()
                )
            elif param_type == ParameterType.location.value:
                param_value = param_value.value
                # Find the location_id based on the location name, using valid_locations
                target = next(
                    loc
                    for loc in valid_locations
                    if loc.name.lower() == param_value.lower()
                )
            elif param_type == ParameterType.item.value:
                param_value = param_value.value
                # Find the item_id based on the item name, using valid_items
                target = next(
                    it for it in valid_items if it.name.lower() == param_value.lower()
                )
            elif (
                param_type == ParameterType.amount.value
                or param_type == ParameterType.content.value
            ):
                content = param_value
            elif param_type == ParameterType.item.value:
                # Items and other parameter types are not implemented yet, we raise:
                raise NotImplementedError("Item parameter type is not implemented")

        print(f"Action parsing time: {time.time() - start_time}")
        return CharacterAction(
            protagonist=character,
            command=command.upper(),
            target=target,
            content=content,
        )

    except ValidationError:
        # Handle validation errors
        raise ActionParsingError(f"Invalid action format: {traceback.format_exc()}")


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
                name="Attack",
                description="Deliver a powerful blow",
                parameter_types=[ParameterType.character],
            )
        ],
        psychological_profile="Determined and compassionate",
    )
    items = [Item(name="Sword", description="A sharp blade")]
    events = [
        CharacterAction(
            command="Say",
            protagonist=protagonist,
            target=items[0],
            content="What a fine sword!",
        )
    ]

    print(
        parse_action(
            protagonist,
            '{"action": {"command": "Attack", "parameters": {"character": "John the Brave"}}}',
            NPCs,
            locations,
            items,
        )
    )
