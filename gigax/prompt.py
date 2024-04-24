import outlines
from gigax.scene import (
    Character,
    Item,
    Location,
    ProtagonistCharacter,
)
from gigax.parse import CharacterAction


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
    {% for skill in protagonist.skills %}
    {{ skill.to_training_format() }}
    {% endfor %}

    {{ protagonist.name }}:
    """
