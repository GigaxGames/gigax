from gigax.scene import Character, Item, Location, ParameterType
from gigax.parse import CharacterAction, ProtagonistCharacter, Skill


def create_scene():
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
            parameters=[items[0], "What a fine sword!"],
        )
    ]
    return context, locations, NPCs, protagonist, items, events
