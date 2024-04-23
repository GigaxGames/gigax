import logging
import os
import time
import traceback

from openai import AsyncOpenAI
from llama_cpp import Llama

from action_formatter import (
    parse_action,
)
from models import (
    Character,
    CharacterAction,
    Item,
    Location,
    ProtagonistCharacter,
)
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("uvicorn")


async def generate_openai(
    messages: list,
    temperature: float = 0.8,
    model: str = "mistral_7b_regex",
    guided_regex: str | None = None,
) -> str:

    client = AsyncOpenAI(
        base_url=os.getenv("OPENAI_API_BASE"), api_key=os.getenv("OPENAI_API_KEY")
    )

    # Time the query
    start = time.time()

    messages = [
        {
            "role": "user",
            "content": messages[0]["content"],
        },
    ]

    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=100,
        temperature=temperature,
        top_p=0.95,
        extra_body=dict(guided_regex=guided_regex),
    )

    # Log the query time
    print(f"Query time: {time.time() - start}")

    # Return the NPC's response
    return response.choices[0].message.content  # type: ignore


def generate_local(
    messages: list,
):
    llm = Llama(
        model_path="./models/stablelm-zephyr-3b.Q4_K_M.gguf",
        chat_format="chatml",
        n_gpu_layers=1,
    )  # Set chat_format according to the model you are using
    res = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": "You are a story writing assistant."},
            {"role": "user", "content": "Write a story about llamas."},
        ],
        max_tokens=30,
    )


async def get_input(
    prompt: str,
    locations: list[Location],
    NPCs: list[Character],
    protagonist: ProtagonistCharacter,
    items: list[Item],
) -> CharacterAction:
    """
    Prompt the NPC for an input.
    """

    messages = [{"role": "user", "content": f"{prompt}"}]

    logger.info(f"Prompting NPC {protagonist.name} with the following prompt: {prompt}")
    guided_regex = protagonist.get_combined_regex(NPCs, locations, items)

    # Generate the response
    res = await generate_openai(messages, guided_regex=guided_regex.pattern)

    try:
        # Parse response
        parsed_action = parse_action(
            res, protagonist, NPCs, locations, items, guided_regex
        )
    except Exception:
        logger.error(f"Error while parsing the action: {traceback.format_exc()}")

    logger.info(f"NPC {protagonist.name} responded with: {parsed_action}")
    return parsed_action
