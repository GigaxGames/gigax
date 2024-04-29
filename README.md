<div align="center" style="margin-bottom: 1em;">


<img src="./docs/assets/images/gigax_logo_black.png" alt="Gigax Logo" width=200></img>


**Add LLM-powered NPCs in your game, at runtime 👟** 


______________________________________________________________________


</div>


``` bash
pip install gigax
```

First time here? Go to our [setup guide](https://outlines-dev.github.io/outlines/welcome)

## Features

- [x] 🕹️ NPCs that `<speak>`, `<jump>`, `<attack>` and perform any other action you've defined
- [x] ⚡ <1 second CPU inference on most machines, faster on GPU
- [x] [🤗 Open-weights models available](https://huggingface.co/Gigax), fined-tuned from: Llama-3, Phi-3, Mistral, etc.
- [x] 🔒 Structured generation with [Outlines 〰️](https://github.com/outlines-dev/outlines/tree/main) means the output format is always respected.
- [ ] 📜 Runtime quest generation to make NPCs autonomous, and create dynamic narration 
➡ *Available through our API*
- [ ] 😶‍🌫️ Memory creation, storage and retrieval with a Vector store
➡ *Available through our API*


Gigax has new releases and features on the way. Make sure to ⭐ star and 👀 watch this repository!

## Usage

* Instantiating the model using outlines:
```py
from outlines import models
from gigax.step import NPCStepper

# Download model from the Hub
model_name = "Gigax/NPC-LLM-7B"
llm = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Our stepper takes in a Outlines model to enable guided generation
# This forces the model to follow our output format
model = models.Transformers(llm, tokenizer)

# Instantiate a stepper: handles prompting + output parsing
stepper = NPCStepper(model=model)
```

* Calling the model on your game's data:

```py
from gigax.parse import CharacterAction
from gigax.scene import (
    Character,
    Item,
    Location,
    ProtagonistCharacter,
    ProtagonistCharacter,
    Skill,
    ParameterType,
)
# Use sample data
current_location = Location(name="Old Town", description="A quiet and peaceful town.")
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

action = stepper.get_action(
    context=context,
    locations=locations,
    NPCs=NPCs,
    protagonist=protagonist,
    items=items,
    events=events,
)
```

## API

Contact us to  [give our NPC API a try](https://tally.so/r/w7d2Rz) - we'll take care of model serving, NPC memory, and more!

