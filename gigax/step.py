import time
import logging
import traceback

from openai import AsyncOpenAI
from gigax.prompt import NPCPrompt
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


class NPCStepper:
    def __init__(
        self,
        model: str | models.LogitsGenerator,
        api_key: str | None = None,
        api_url: str = "https://gig.ax/llm/v1",
    ):
        self.model = model
        self.api_key = api_key
        self.api_url = api_url

        if isinstance(model, str) and not self.api_key:
            raise ValueError("You must provide an API key to use our API.")

    async def generate_api(
        self,
        model: str,
        prompt: str,
        guided_regex: str,
        temperature: float = 0.8,
    ) -> str:
        client = AsyncOpenAI(base_url=self.api_url, api_key=self.api_key)

        # Time the query
        start = time.time()

        messages = [
            {
                "role": "user",
                "content": prompt,
            },
        ]

        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=100,
            temperature=temperature,
            extra_body=dict(guided_regex=guided_regex),
        )

        # Log the query time
        print(f"Query time: {time.time() - start}")

        # Return the NPC's response
        return response.choices[0].message.content  # type: ignore

    async def generate_local(
        self,
        prompt: str,
        model: models.LogitsGenerator,
        guided_regex: str,
    ) -> str:
        if not isinstance(model, (models.LlamaCpp, models.Transformers)):  # type: ignore
            raise NotImplementedError(
                "Only LlamaCpp and Transformers models are supported in local mode for now."
            )

        # Time the query
        start = time.time()

        generator = regex(model, guided_regex)
        if isinstance(model, models.LlamaCpp):  # type: ignore
            # Llama-cpp-python has a convenient create_chat_completion() method that guesses the chat prompt
            # But outlines does not support it for generation, so we do this ugly hack instead
            chat_prompt = f"<|user|>\n{prompt}<|end|>\n<|assistant|>"
        elif isinstance(model, models.Transformers):  # type: ignore
            messages = [
                {"role": "user", "content": f"{prompt}"},
            ]
            chat_prompt = model.tokenizer.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
            if not isinstance(chat_prompt, str):
                raise ValueError(
                    f"Expected a string, but received type {type(chat_prompt)} with value {chat_prompt}"
                )

        res = generator(chat_prompt)
        if not isinstance(res, str):
            raise ValueError(
                f"Expected a string, but received type {type(res)} with value {res}"
            )

        logger.info(f"Query time: {time.time() - start}")
        return res

    async def get_action(
        self,
        context: str,
        locations: list[Location],
        NPCs: list[Character],
        protagonist: ProtagonistCharacter,
        items: list[Item],
        events: list[CharacterAction],
    ) -> CharacterAction:
        """
        Prompt the NPC for an input.
        """

        prompt = NPCPrompt(
            context=context,
            locations=locations,
            NPCs=NPCs,
            protagonist=protagonist,
            items=items,
            events=events,
        )

        logger.info(
            f"Prompting NPC {protagonist.name} with the following prompt: {prompt}"
        )
        guided_regex = get_guided_regex(protagonist.skills, NPCs, locations, items)

        # Generate the response
        if isinstance(self.model, models.LogitsGenerator):  # type: ignore
            res = await self.generate_local(
                prompt,
                self.model,
                guided_regex.pattern,
            )
        else:
            res = await self.generate_api(
                self.model,
                prompt,
                guided_regex.pattern,
            )

        try:
            # Parse response
            parsed_action = CharacterAction.from_str(
                res, protagonist, NPCs, locations, items, guided_regex
            )
        except Exception:
            logger.error(f"Error while parsing the action: {traceback.format_exc()}")

        logger.info(f"NPC {protagonist.name} responded with: {parsed_action}")
        return parsed_action
