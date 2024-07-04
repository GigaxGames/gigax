import outlines
from gigax.scene import (
    Character,
    Item,
    Location,
    ProtagonistCharacter,
)
from typing import Literal
from gigax.parse import CharacterAction
from jinja2 import Template


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


def llama_chat_template(
    message: list[dict[Literal["role", "content"], str]],
    bos_token: str,
    chat_template: str,
):
    tpl = Template(chat_template)
    return tpl.render(messages=message, bos_token=bos_token)
