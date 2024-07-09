import re
import time
import logging
import traceback
from typing import Callable
from openai import AsyncOpenAI
from gigax.prompt import (
    NPCPrompt,
    NarratorPrompt,
    NarratorPromptQuestGenerate,
    NarratorPromptQuestComplete,
    llama_chat_template,
)

from gigax.scene import (
    Character,
    Item,
    Location,
    NarratorCharacter,
    Skill,
)
from dotenv import load_dotenv
from outlines import models
from outlines.generate import regex  # type: ignore
from gigax.parse import (
    CharacterAction,
    NarratorUpdate,
    ProtagonistCharacter,
    get_guided_regex,
)

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

        if not isinstance(model, str) and not isinstance(model, (models.LlamaCpp, models.Transformers)):  # type: ignore
            raise NotImplementedError(
                "Only LlamaCpp and Transformers models are supported in local mode for now."
            )

    async def _generate(
        self, prompt: str | list[dict[str, str]], guided_regex: str
    ) -> str:
        # Return the appropriate generation function
        if isinstance(self.model, models.LogitsGenerator):  # type: ignore
            return self.generate_local(self.model, prompt, guided_regex)
        else:
            return await self.generate_api(self.model, prompt, guided_regex)

    async def generate_api(
        self,
        model: str,
        prompt: str | list[dict[str, str]],
        guided_regex: str,
        temperature: float = 0.8,
    ) -> str:
        client = AsyncOpenAI(base_url=self.api_url, api_key=self.api_key)

        # Time the query
        start = time.time()

        if isinstance(prompt, list):
            messages = prompt
        else:
            messages = [
                {
                    "role": "user",
                    "content": prompt,
                },
            ]

        response = await client.chat.completions.create(
            model=model,
            messages=messages,  # type: ignore
            max_tokens=100,
            temperature=temperature,
            extra_body=dict(guided_regex=guided_regex),
        )

        # Log the query time
        print(f"Query time: {time.time() - start}")

        # Return the NPC's response
        return response.choices[0].message.content  # type: ignore

    def generate_local(
        self,
        model: models.LogitsGenerator,
        prompt: str | list[dict[str, str]],
        guided_regex: str,
    ) -> str:
        # Time the query
        start = time.time()

        generator = regex(model, guided_regex)

        if isinstance(prompt, list):
            messages = prompt
        else:
            messages = [
                {"role": "user", "content": prompt},
            ]
        if isinstance(model, models.LlamaCpp):  # type: ignore

            # Llama-cpp-python has a convenient create_chat_completion() method that guesses the chat prompt
            # But outlines does not support it for generation, so we do this ugly hack instead
            bos_token = model.model._model.token_get_text(
                int(model.model.metadata["tokenizer.ggml.bos_token_id"])
            )
            chat_prompt = llama_chat_template(
                messages, bos_token, model.model.metadata["tokenizer.chat_template"]  # type: ignore
            )

        elif isinstance(model, models.Transformers):  # type: ignore
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
    ) -> CharacterAction | None:
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
        res = await self._generate(prompt, guided_regex.pattern)

        try:
            # Parse response
            parsed_action = CharacterAction.from_str(res, protagonist, guided_regex)
            logger.info(f"NPC {protagonist.name} responded with: {parsed_action}")
            return parsed_action
        except Exception:
            logger.error(f"Error while parsing the action: {traceback.format_exc()}")

    async def get_narrator_update(
        self,
        context: str,
        locations: list[Location],
        NPCs: list[Character],
        protagonist: ProtagonistCharacter,
        narrator: NarratorCharacter,
        items: list[Item],
        events: list[CharacterAction],
    ) -> NarratorUpdate | None:
        """
        Prompt the NPC for an input.
        """

        # UTTERANCE
        prompt = NarratorPrompt(
            context=context,
            locations=locations,
            NPCs=NPCs,
            protagonist=protagonist,
            narrator=narrator,
            items=items,
            events=events,
        )
        logger.info(f"Prompting {narrator.name} for utterance: {prompt}")
        guided_regex = re.compile(".*")
        utterance = await self._generate(prompt, guided_regex.pattern)
        update = NarratorUpdate(utterance=utterance)
        logger.info(f"{narrator.name} answered with: {utterance}")

        # QUESTS
        quest_prompter: Callable[[ProtagonistCharacter, str, list[Skill]], str]
        if protagonist.quests:
            logger.info(
                f"Protagonist has quests: {protagonist.quests}. Launching quest completion prompt."
            )
            quest_prompter = NarratorPromptQuestComplete
        elif not protagonist.quests:
            logger.info("Protagonist has no quests. Launching quest generation prompt.")
            quest_prompter = NarratorPromptQuestGenerate

        quest_prompt = quest_prompter(
            protagonist=protagonist,
            narrator_name=narrator.name,
            skills=narrator.skills,
        )
        logger.info(f"Narrator prompt:{quest_prompt}")

        messages = [
            {
                "role": "user",
                "content": prompt,
            },
            {
                "role": "assistant",
                "content": utterance,
            },
            {
                "role": "user",
                "content": quest_prompt,
            },
        ]
        guided_regex = get_guided_regex(
            narrator.skills, NPCs, locations, items, protagonist.quests
        )
        quests = await self._generate(messages, guided_regex.pattern)
        try:
            # Parse response
            parsed_action = CharacterAction.from_str(quests, protagonist, guided_regex)
            logger.info(f"NPC {protagonist.name} responded with: {parsed_action}")
            update.actions.append(parsed_action)
        except Exception:
            logger.error(f"Error while parsing the action: {traceback.format_exc()}")

        logger.info(f"Narrator responded with: {update}")
        return update
