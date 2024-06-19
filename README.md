<div align="center" style="margin-bottom: 1em;">


<img src="./docs/assets/images/gigax_logo_black.png" alt="Gigax Logo" width=200></img>

[![Twitter][twitter-badge]][twitter]
[![Discord][discord-badge]][discord]


**👟 Runtime, LLM-powered NPCs** 



https://github.com/GigaxGames/gigax/assets/33256624/6dc65347-7d55-45a3-90c1-d2f39941b1a0


______________________________________________________________________


</div>

``` bash
pip install gigax
```


## Features

- [x] 🕹️ NPCs that `<speak>`, `<jump>`, `<attack>` and perform any other action you've defined
- [x] ⚡ <1 second GPU inference on most machines
- [x] [🤗 Open-weights models available](https://huggingface.co/Gigax), fined-tuned from: Llama-3, Phi-3, Mistral, etc.
- [x] 🔒 Structured generation with [Outlines 〰️](https://github.com/outlines-dev/outlines/tree/main) means the output format is always respected
- [ ] 🗄️ *Coming soon:* Local server mode, with language-agnostic API
- [ ] 📜 ***[Available on API](https://tally.so/r/w7d2Rz)***: Runtime quest generation, for players and NPCs
- [ ] 😶‍🌫️ ***[Available on API](https://tally.so/r/w7d2Rz)***: Memory creation, storage and retrieval with a Vector DB


Gigax has new releases and features on the way. Make sure to ⭐ star and 👀 watch this repository!


## Usage

### Model instantiation


* We provide various models on the [🤗 Huggingface hub](https://huggingface.co/Gigax):
    * [NPC-LLM-7B](https://huggingface.co/Gigax/NPC-LLM-7B) (our Mistral-7B fine-tune)
    * [NPC-LLM-3_8B](https://huggingface.co/Gigax/NPC-LLM-3_8B) (our Phi-3 fine-tune)
    * [NPC-LLM-3_8B-128k](https://huggingface.co/Gigax/NPC-LLM-3_8B-128k) (our Phi-3 128k context length fine-tune)

* All these models are also available in [gguf](https://huggingface.co/docs/hub/en/gguf) format to run them on CPU using [llama_cpp](https://llama-cpp-python.readthedocs.io/en/latest/)
    * [NPC-LLM-7B-GGUF](https://huggingface.co/Gigax/NPC-LLM-7B-GGUF)
    * [NPC-LLM-3_8B-GGUF](https://huggingface.co/Gigax/NPC-LLM-3_8B-GGUF)
    * [NPC-LLM-3_8B-128k-GGUF](https://huggingface.co/Gigax/NPC-LLM-3_8B-128k-GGUF)


* Start by instantiating one of them using outlines:
```py
from outlines import models
from gigax.step import NPCStepper
from transformers import AutoTokenizer, AutoModelForCausalLM

# Download model from the Hub
llm = Llama.from_pretrained(
    repo_id="Gigax/NPC-LLM-3_8B-GGUF",
    filename="npc-llm-3_8B.gguf"
    # n_gpu_layers=-1, # Uncomment to use GPU acceleration
    # n_ctx=2048, # Uncomment to increase the context window
)

model = models.LlamaCpp(llm) 

# Instantiate a stepper: handles prompting + output parsing
stepper = NPCStepper(model=model)
```


### Stepping an NPC


* From there, stepping an NPC is a one-liner:
```py
action = await stepper.get_action(
    context=context,
    locations=locations,
    NPCs=NPCs,
    protagonist=protagonist,
    items=items,
    events=events,
)
```


* We provide classes to instantiate `Locations`, `NPCs`, etc. :
```py
from gigax.parse import CharacterAction
from gigax.scene import (
    Character,
    Item,
    Location,
    ProtagonistCharacter,
    Skill,
    ParameterType,
)
# Use sample data
context = "Medieval world"
current_location = Location(name="Old Town", description="A quiet and peaceful town.")
locations = [current_location] # you can add more locations to the scene
NPCs = [
    Character(
    name="John the Brave",
    description="A fearless warrior",
    current_location=current_location,
    )
]
protagonist = ProtagonistCharacter(
    name="Aldren",
    description="Brave and curious",
    current_location=current_location,
    memories=["Saved the village", "Lost a friend"],
    quests=["Find the ancient artifact", "Defeat the evil warlock"],
    skills=[
        Skill(
            name="Attack",
            description="Deliver a powerful blow",
            parameter_types=[ParameterType.character],
        )
    ],
    psychological_profile="Determined and compassionate",
)
items = [Item(name="Sword", description="A sharp blade")]
events = [
    CharacterAction(
        command="Say",
        protagonist=protagonist,
        parameters=[items[0], "What a fine sword!"],
    )
]
```


## API

Contact us to  [give our NPC API a try](https://tally.so/r/w7d2Rz) - we'll take care of model serving, NPC memory, and more!


[discord]: https://discord.gg/rRBSueTKXg
[discord-badge]: https://img.shields.io/discord/1090190447906934825?color=81A1C1&logo=discord&logoColor=white&style=flat-square
[twitter-badge]: https://img.shields.io/twitter/follow/GigaxGames?style=social
[twitter]: https://twitter.com/GigaxGames
