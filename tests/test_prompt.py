from gigax.parse import CharacterAction
from gigax.prompt import NPCPrompt
from gigax.scene import Character, Item, Location, ProtagonistCharacter


def test_prompt(
    context: str,
    locations: list[Location],
    NPCs: list[Character],
    protagonist: ProtagonistCharacter,
    items: list[Item],
    events: list[CharacterAction],
):
    prompt = NPCPrompt(context, locations, NPCs, protagonist, items, events)
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
