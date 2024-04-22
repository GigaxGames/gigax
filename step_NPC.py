import json
import logging
import os
import time
import traceback

from openai import AsyncOpenAI
from llama_cpp import Llama

from action_formatter import generate_typed_skill_model, parse_action
from models import (
    Character,
    CharacterAction,
    Item,
    Location,
    ProtagonistCharacter,
)

logger = logging.getLogger("uvicorn")


async def generate_openai(
    messages: list,
    temperature: float = 0.8,
    model: str = "mistral_7b",
    actions_schema: str | None = None,
) -> str:

    client = AsyncOpenAI(base_url=os.getenv("OPENAI_API_BASE"))

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
        extra_body=dict(guided_json=actions_schema),
    )

    # Log the query time
    logger.info(f"Query time: {time.time() - start}")

    # Return the NPC's response
    return response.choices[0].message.content  # type: ignore


def generate_local(
    messages: list,
) -> str:
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
    print(res)
    exit()
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
    model = generate_typed_skill_model(protagonist, NPCs, locations, items)
    actions_schema = json.dumps(model.model_json_schema(), indent=2)

    # Generate the response
    res = await generate_openai(messages, actions_schema=actions_schema)

    # Parse it:
    try:
        parsed_action = parse_action(protagonist, res, NPCs, locations, items)
    except Exception:
        logger.error(f"Error while parsing the action: {traceback.format_exc()}")

    logger.info(f"NPC {protagonist.name} responded with: {res}")
    return parsed_action


if __name__ == "__main__":
    generate_local(["Hello"])
