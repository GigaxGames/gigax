from gigax.prompt import NPCPrompt
from tests.utils import create_scene


def test_prompt():
    prompt = NPCPrompt(*create_scene())
    assert prompt

    test_prompt = """- WORLD KNOWLEDGE: A vast open world full of mystery and adventure.
- KNOWN LOCATIONS: Old Town
- NPCS: John the Brave
- CURRENT LOCATION: Old Town: A quiet and peaceful town.
- CURRENT LOCATION ITEMS: Sword
- LAST EVENTS:
Aldren: Say Sword What a fine sword!

- PROTAGONIST NAME: Aldren
- PROTAGONIST PSYCHOLOGICAL PROFILE: Brave and curious
- PROTAGONIST MEMORIES:
Saved the village
Lost a friend
- PROTAGONIST PENDING QUESTS:
Find the ancient artifact
Defeat the evil warlock
- PROTAGONIST ALLOWED ACTIONS:
Attack <character> : Deliver a powerful blow

Aldren:"""

    assert prompt == test_prompt, f"{prompt} != {test_prompt}"
