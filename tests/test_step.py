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


@pytest.mark.asyncio
async def test_stepper_local_llamacpp(
    context: str,
    locations: list[Location],
    NPCs: list[Character],
    protagonist: ProtagonistCharacter,
    items: list[Item],
    events: list[CharacterAction],
):
    llm = Llama(
        model_path="./models/Phi-3-mini-4k-instruct-q4.gguf",  # path to GGUF file
        n_ctx=4096,  # The max sequence length to use - note that longer sequence lengths require much more resources
        n_threads=8,  # The number of CPU threads to use, tailor to your system and the resulting performance
        n_gpu_layers=35,  # The number of layers to offload to GPU, if you have GPU acceleration available. Set to 0 if no GPU acceleration is available on your system.
    )

    model = models.LlamaCpp(llm)  # type: ignore

    stepper = NPCStepper(model=model)

    start = time.time()
    action = await stepper.get_action(
        context=context,
        locations=locations,
        NPCs=NPCs,
        protagonist=protagonist,
        items=items,
        events=events,
    )

    print(f"Query time: {time.time() - start}")
    assert str(action) == "Aldren: Attack John the Brave"


@pytest.mark.asyncio
async def test_stepper_local_transformers(
    context: str,
    locations: list[Location],
    NPCs: list[Character],
    protagonist: ProtagonistCharacter,
    items: list[Item],
    events: list[CharacterAction],
):
    llm = AutoModelForCausalLM.from_pretrained(
        "TinyLlama/TinyLlama-1.1B-Chat-v1.0", output_attentions=True
    )
    tokenizer = AutoTokenizer.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
    model = models.Transformers(llm, tokenizer)  # type: ignore
    # Get the NPC's input
    stepper = NPCStepper(model=model)

    action = await stepper.get_action(
        context=context,
        locations=locations,
        NPCs=NPCs,
        protagonist=protagonist,
        items=items,
        events=events,
    )

    assert str(action) == "Aldren: Attack John the Brave"


@pytest.mark.asyncio
async def test_stepper_api(
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
