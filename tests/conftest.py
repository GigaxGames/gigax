import pytest
from gigax.scene import Character, Item, Location, ParameterType
from gigax.parse import CharacterAction, ProtagonistCharacter, Skill


@pytest.fixture()
def context():
    # Example usage of the function
    return "A vast open world full of mystery and adventure."


@pytest.fixture()
def locations():
    return [Location(name="Old Town", description="A quiet and peaceful town.")]


@pytest.fixture()
def current_location(locations):
    return locations[0]


@pytest.fixture()
def NPCs(current_location):
    return [
        Character(
            name="John the Brave",
            description="A fearless warrior",
            current_location=current_location,
        )
    ]


@pytest.fixture()
def protagonist(current_location):
    return ProtagonistCharacter(
        name="Aldren",
        description="Brave and curious",
        current_location=current_location,
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


@pytest.fixture()
def items():
    return [Item(name="Sword", description="A sharp blade")]


@pytest.fixture()
def events(protagonist, items):
    return [
        CharacterAction(
            command="Say",
            protagonist=protagonist,
            parameters=[items[0], "What a fine sword!"],
        )
    ]
