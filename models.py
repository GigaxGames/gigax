from enum import Enum
import json
import re
import time
from typing import Optional, Union
from lark import Lark, UnexpectedToken
from pydantic import BaseModel, Field


class ParameterType(str, Enum):
    character = "character"
    location = "location"
    item = "item"
    amount = "amount"
    content = "content"
    other = "other"


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
        Dump the object as a json dict that follows our training format:
        {
            "command": "grab",
            "parameters": [
                "item"
                ],
            "description": "Grab an item."
        }
        """
        cmd = {
            "command": self.name,
            "parameters": [p.value for p in self.parameter_types],
            "description": self.description,
        }
        return json.dumps(cmd)

    def to_grammar_rule(self) -> str:
        """
        Convert the skill to a grammar rule suitable for EBNF, handling multiple parameters.
        """
        parts = []
        for param in self.parameter_types:
            if param == ParameterType.character:
                parts.append("character")
            elif param == ParameterType.location:
                parts.append("location")
            elif param == ParameterType.item:
                parts.append("item")
            elif param == ParameterType.amount:
                parts.append("NUMBER")
            elif param == ParameterType.content:
                parts.append("(STRING | WS)*")

        # Construct rule with parameters separated by whitespace
        params = " ".join(parts)
        return f'"{self.name}" {params}'

    def to_regex(self, context):
        """
        Generate a regex string for a skill command based on current context.
        """
        parts = [self.name]  # Start with the command name
        for param in self.parameter_types:
            if param == "character":
                parts.append(
                    r"(" + "|".join(map(re.escape, context["characters"])) + ")"
                )
            elif param == "location":
                parts.append(
                    r"(" + "|".join(map(re.escape, context["locations"])) + ")"
                )
            elif param == "item":
                parts.append(r"(" + "|".join(map(re.escape, context["items"])) + ")")
            elif param == "amount":
                parts.append(r"(\d+)")
            elif param == "content":
                parts.append(
                    r'("([^"]*)")'  # Match content within quotes, without escaped quotes handling
                )

        # Merge and add forward slash as last character
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
    target: Optional[Character | Item | Location]
    content: Optional[str]

    def __str__(self) -> str:
        # Jsonify the object, but only print target.name and protagonist.name if they exist
        ret = {
            "type": self.command,
            "protagonist": self.protagonist.name,
        }
        if self.target:
            ret["target"] = self.target.name
        if self.content:
            ret["content"] = self.content
        return json.dumps(ret)


if __name__ == "__main__":
    # Context as given
    context = {
        "characters": ["Alice", "Bob", "Charlie"],
        "locations": ["Forest", "Castle", "Town"],
        "items": ["Sword", "Shield", "Potion"],
        "amounts": ["10", "20", "100"],
    }

    # Base grammar template
    base_grammar = """
%import common.WS
%ignore WS
%import common.ESCAPED_STRING -> STRING
%import common.INT -> NUMBER

start: command
command: {}

{}

character: {}
location: {}
item: {}
amount: NUMBER
content: STRING
    """

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
            parameter_types=[ParameterType.amount],
            description="Give coins.",
        ),
    ]

    # Dynamic construction of parts of the grammar
    skill_names = "\n | ".join([f"{skill.name}_command" for skill in skills])
    command_rules = "\n".join(
        [f"{skill.name}_command: {skill.to_grammar_rule()}" for skill in skills]
    )
    character_rules = " | ".join([f'"{char}"' for char in context["characters"]])
    location_rules = " | ".join([f'"{loc}"' for loc in context["locations"]])
    item_rules = " | ".join([f'"{item}"' for item in context["items"]])

    full_grammar = base_grammar.format(
        skill_names, command_rules, character_rules, location_rules, item_rules
    )

    # print("Grammar:")
    # print(full_grammar)
    # start_time = time.time()
    # parser = Lark(full_grammar, start="start", parser="lalr")
    # print(f"Grammar compiled in {time.time() - start_time} seconds.")

    # Test input and expected outputs
    test_commands = [
        'say Alice "Hello, how are you"',
        "move Forest",
        "grab Sword",
        'say Alice "I love you" Bob "It\'s nice to see you again',
        "give_coins 100",
        "say Bob",  # Should fail, incomplete
        "move Dungeon",  # Should fail, invalid location
        "grab Forest",  # Should fail, invalid item
        "give_coins ten",  # Should fail, invalid amount
    ]

    # # Run test cases
    # for command in test_commands:
    #     try:
    #         result = parser.parse(command)
    #         print(f"Command '{command}' parsed successfully: {result}")
    #     except UnexpectedToken as e:
    #         print(
    #             f"Error parsing command '{command}': Unexpected token {e.token}. Expected one of: {e.expected}"
    #         )
    #     except Exception as e:
    #         print(f"Error parsing command '{command}': {e}")
    # exit()

    # Generate a combined regex pattern for all skills
    combined_regex_parts = [skill.to_regex(context) for skill in skills]
    combined_regex = "|".join(combined_regex_parts)
    print(f"Combined regex pattern: {combined_regex}")
    start_time = time.time()
    compiled_combined_regex = re.compile(combined_regex, re.IGNORECASE)
    print(f"Regex compiled in {time.time() - start_time} seconds.")
    # Perform tests with combined regex
    print("Testing commands with combined skills regex:")
    for command in test_commands:
        matches = compiled_combined_regex.match(command)
        if matches:
            print(f"Valid command: {command}")
        else:
            print(f"Invalid command: {command}")
    # exit()
    # Initialize the Outlines model and generator with the modified grammar
    from outlines import models, generate
    from llama_cpp import Llama

    llm = models.llamacpp(
        repo_id="TheBloke/stablelm-zephyr-3b-GGUF",
        filename="stablelm-zephyr-3b.Q4_K_M.gguf",
        chat_format="chatml",
        n_gpu_layers=-1,
    )

    generator = generate.regex(llm, combined_regex)

    # Generate a command based on a prompt or dynamically
    sequence = generator(
        """
    You are an NPC in a video game. You can use the following commands:
    - say <character> <content>
    - move <location>
    - grab <item>
    - give_coins <amount>

    Characters around you: Alice, Bob, Charlie
    Locations around you: Forest, Castle, Town
    Items around you: Sword, Shield, Potion
    Current amount of coins: 100
                     
    Say "I love you" to Bob:
    """
    )
    print(sequence)
