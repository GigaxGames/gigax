import outlines
from models import (
    Character,
    CharacterAction,
    Item,
    Location,
    ParameterType,
    ProtagonistCharacter,
    Skill,
)


@outlines.prompt
def NPCPrompt(
    context: str,
    locations: list[Location],
    NPCs: list[Character],
    protagonist: ProtagonistCharacter,
    items: list[Item],
    events: list[CharacterAction],
):
    """
    - WORLD KNOWLEDGE: {{ context }}
    - KNOWN LOCATIONS: {{ locations | map(attribute='name') | join(', ') }}
    - NPCS: {{ NPCs | map(attribute='name') | join(', ') }}
    - CURRENT LOCATION: {{ protagonist.current_location.name }}: {{ protagonist.current_location.description }}
    - CURRENT LOCATION ITEMS: {{ items | map(attribute='name') | join(', ') }}
    - LAST EVENTS:
    {% for event in events %}
    {{ event }}
    {% endfor %}

    - PROTAGONIST NAME: {{ protagonist.name }}
    - PROTAGONIST PSYCHOLOGICAL PROFILE: {{ protagonist.description }}
    - PROTAGONIST MEMORIES:
    {% for memory in protagonist.memories %}
    {{ memory }}
    {% endfor %}
    - PROTAGONIST PENDING QUESTS:
    {% for quest in protagonist.quests %}
    {{ quest }}
    {% endfor %}
    - PROTAGONIST ALLOWED ACTIONS:
    {% for action in protagonist.skills %}
    {{ action.to_training_format() }}
    {% endfor %}

    {{ protagonist.name }}:
    """


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
            parameters=[items[0], "What a fine sword!"],
        )
    ]

    print(NPCPrompt(context, locations, NPCs, protagonist, items, events))
