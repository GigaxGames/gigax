import os
import time
import logging
import traceback

from openai import AsyncOpenAI
from gigax.scene import (
    Character,
    Item,
    Location,
)
from dotenv import load_dotenv
from outlines import models
from outlines.generate import regex  # type: ignore
from gigax.parse import CharacterAction, ProtagonistCharacter, get_guided_regex

load_dotenv()

logger = logging.getLogger("uvicorn")


MODEL_NAME = os.getenv("MODEL_NAME")


async def generate_api(
    messages: list,
    model: str,
    api_key: str,
    api_url: str,
    guided_regex: str,
    temperature: float = 0.8,
) -> str:
    client = AsyncOpenAI(base_url=api_url, api_key=api_url)

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


async def generate_local(
    messages: list,
    model: models.LogitsGenerator,
    guided_regex: str,
    temperature: float = 0.8,
) -> str:
    if not isinstance(model, models.Transformers):
        # We only know how to apply chat templates to Transformers models
        raise NotImplementedError("Only Transformers models are supported for now")

    # Time the query
    start = time.time()

    messages = [
        {
            "role": "user",
            "content": messages[0]["content"],
        },
    ]

    prompt = model.tokenizer.apply_chat_template(  # type: ignore
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    generator = regex(model, guided_regex)

    res = generator(prompt)
    if not isinstance(res, str):
        raise ValueError(
            f"Expected a string, but received type {type(res)} with value {res}"
        )

    logger.info(f"Query time: {time.time() - start}")
    return res


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
    guided_regex = get_guided_regex(protagonist.skills, NPCs, locations, items)

    # Generate the response
    res = await generate_openai(messages, guided_regex=guided_regex.pattern)

    try:
        # Parse response
        parsed_action = CharacterAction.from_str(
            res, protagonist, NPCs, locations, items, guided_regex
        )
    except Exception:
        logger.error(f"Error while parsing the action: {traceback.format_exc()}")

    logger.info(f"NPC {protagonist.name} responded with: {parsed_action}")
    return parsed_action
