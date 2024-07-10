import outlines
from gigax.scene import (
    Character,
    Item,
    Location,
    NarratorCharacter,
    ProtagonistCharacter,
    Skill,
)
from typing import Literal
from gigax.parse import CharacterAction
from jinja2 import Template


def llama_chat_template(
    message: list[dict[Literal["role", "content"], str]],
    bos_token: str,
    chat_template: str,
):
    tpl = Template(chat_template)
    return tpl.render(messages=message, bos_token=bos_token)


@outlines.prompt
def NPCPromptBase(
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
    - LAST EVENTS:
    {% for event in events %}
    {{ event }}
    {% endfor %}
    {{ protagonist.name }}:
    """


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


@outlines.prompt
def NarratorPrompt(
    context: str,
    locations: list[Location],
    NPCs: list[Character],
    protagonist: ProtagonistCharacter,
    narrator: NarratorCharacter,
    skills: list[Skill],
    items: list[Item],
    events: list[CharacterAction],
):
    """
    You're the game master in a roleplaying game.
    The setting: {{context}}
    NPCs: {{ NPCs | map(attribute='name') | join(', ') }}
    Locations: {{ locations | map(attribute='name') | join(', ') }}
    Current location: {{ protagonist.current_location.name }}: {{ protagonist.current_location.description }}.
    Items in location: {{ items | map(attribute='name') | join(', ') }}
    Current Narrator: {{narrator.name}}
    {{protagonist.name}}'s pending quest from {{narrator.name}}: {{protagonist.quests}}
    {{narrator.description}}
    Act as {{narrator.name}}, using one of the following skills:
    {% for skill in skills %}
    {{ skill.to_training_format() }}
    {% endfor %}
    Latest events:
    {% for event in events %}
    {{ event }}
    {% endfor %}
    {{narrator.name}}:
    """


@outlines.prompt
def NarratorPromptQuestGenerate(
    protagonist: ProtagonistCharacter,
    narrator_name: str,
    skills: list[Skill],
):
    """
    {{protagonist.name}} has no currently pending quests. You will now determine whether a new quest should be generated, considering {{narrator_name}}'s utterance above.
    Did the narrator suggest a new quest for {{protagonist.name}}? If yes, generate a corresponding quest using this command:
    {% for skill in skills %}
    {{ skill.to_training_format() }}
    {% endfor %}
    """


@outlines.prompt
def NarratorPromptQuestComplete(
    protagonist: ProtagonistCharacter,
    narrator_name: str,
    skills: list[Skill],
):
    """
    You will now determine whether the quest has been completed, considering {{narrator_name}}'s utterance above.
    Remember, {{protagonist.name}}'s quest was: {{protagonist.quests}}.
    Is the quest completed? Answer using this command:
    {% for skill in skills %}
    {{ skill.to_training_format() }}
    {% endfor %}
    """
