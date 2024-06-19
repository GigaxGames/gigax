import os
import time
from llama_cpp import Llama
import pytest
from gigax.parse import CharacterAction
from gigax.scene import Character, Item, Location, ProtagonistCharacter
from transformers import AutoTokenizer, AutoModelForCausalLM
from gigax.step import NPCStepper
from outlines import models
from dotenv import load_dotenv

load_dotenv()


def test_stepper_local_llamacpp(
    context: str,
    locations: list[Location],
    NPCs: list[Character],
    protagonist: ProtagonistCharacter,
    items: list[Item],
    events: list[CharacterAction],
):
    llm = Llama.from_pretrained(
        repo_id="Gigax/NPC-LLM-3_8B-GGUF",
        filename="npc-llm-3_8B.gguf"
        # n_gpu_layers=-1, # Uncomment to use GPU acceleration
        # seed=1337, # Uncomment to set a specific seed
        # n_ctx=2048, # Uncomment to increase the context window
    )

    model = models.LlamaCpp(llm) 

    stepper = NPCStepper(model=model)

    start = time.time()
    action = stepper.get_action(
        context=context,
        locations=locations,
        NPCs=NPCs,
        protagonist=protagonist,
        items=items,
        events=events,
    )

    print(f"Query time: {time.time() - start}")
    assert str(action) == "Aldren: Attack John the Brave"


def test_stepper_local_transformers(
    context: str,
    locations: list[Location],
    NPCs: list[Character],
    protagonist: ProtagonistCharacter,
    items: list[Item],
    events: list[CharacterAction],
):
    llm = AutoModelForCausalLM.from_pretrained(
        "gigax/NPC-LLM-3_8B", output_attentions=True, trust_remote_code=True
    )
    tokenizer = AutoTokenizer.from_pretrained("gigax/NPC-LLM-3_8B")
    model = models.Transformers(llm, tokenizer)  # type: ignore
    # Get the NPC's input
    stepper = NPCStepper(model=model)

    action = stepper.get_action(
        context=context,
        locations=locations,
        NPCs=NPCs,
        protagonist=protagonist,
        items=items,
        events=events,
    )

    assert str(action) == "Aldren: Attack John the Brave"


def test_stepper_api(
    context: str,
    locations: list[Location],
    NPCs: list[Character],
    protagonist: ProtagonistCharacter,
    items: list[Item],
    events: list[CharacterAction],
):
    # Get the NPC's input
    with pytest.raises(ValueError):
        NPCStepper(model="mistral-7b-regex")

    stepper = NPCStepper(model="mistral_7b_regex", api_key=os.getenv("API_KEY"))

    action = await stepper.get_action(
        context=context,
        locations=locations,
        NPCs=NPCs,
        protagonist=protagonist,
        items=items,
        events=events,
    )

    assert str(action) == "Aldren: Attack John the Brave"
