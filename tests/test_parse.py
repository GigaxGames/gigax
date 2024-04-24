from gigax.parse import CharacterAction, get_guided_regex
from tests.utils import create_scene


def test_parse():
    _, locations, NPCs, protagonist, items, _ = create_scene()

    test_command = 'attack John the Brave "Hello, how are you"'

    # Test the compiled regex
    compiled_combined_regex = get_guided_regex(
        protagonist.skills, NPCs, locations, items
    )
    assert compiled_combined_regex
    assert compiled_combined_regex.match(test_command)

    # Test the from_str method
    character_action = CharacterAction.from_str(
        test_command, protagonist, NPCs, locations, items, compiled_combined_regex
    )
    assert character_action
    assert character_action.command == "Attack"
    assert character_action.protagonist == protagonist
    assert character_action.parameters == [NPCs[0]]
