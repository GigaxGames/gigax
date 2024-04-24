<div align="center" style="margin-bottom: 1em;">


<img src="./docs/assets/images/gigax_logo_black.png" alt="Gigax Logo" width=200></img>


**Add LLM-powered NPCs in your game, at runtime 👟** 


[![Gigax Twitter][dottxt-twitter-badge]][Twitter]
[![Discord][discord-badge]][Discord]


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
- [x] 🔓 Structured generation with [Outlines 〰️](https://github.com/outlines-dev/outlines/tree/main) means the output format is always respected.
- [ ] 📜 Runtime quest generation to make NPCs autonomous, and create dynamic narration 
➡ *Available through our API*
- [ ] 😶‍🌫️ Memory creation, storage and retrieval with a Vector store
➡ *Available through our API*


Outlines 〰 has new releases and features coming every week. Make sure to ⭐ star and 👀 watch this repository, follow [@dottxtai][twitter] to stay up to date!

## Gigax company

<div align="center">
<img src="./docs/assets/images/dottxt.png" alt="Outlines Logo" width=100></img>
</div>

We started a company to keep pushing the boundaries of structured generation. Learn more about [.txt](https://twitter.com/dottxtai), and  [give our .json API a try](https://h1xbpbfsf0w.typeform.com/to/ZgBCvJHF) if you need a hosted solution ✨

## Structured generation

The first step towards reliability of systems that include large language models
is to ensure that there is a well-defined interface between their output and
user-defined code. **Outlines** provides ways to control the generation of
language models to make their output more predictable.

### Multiple choices

You can reduce the completion to a choice between multiple possibilities:

``` python
import outlines

model = outlines.models.transformers("mistralai/Mistral-7B-Instruct-v0.2")

prompt = """You are a sentiment-labelling assistant.
Is the following review positive or negative?

Review: This restaurant is just awesome!
"""

generator = outlines.generate.choice(model, ["Positive", "Negative"])
answer = generator(prompt)
```

### Type constraint

You can instruct the model to only return integers or floats:


``` python
import outlines

model = outlines.models.transformers("WizardLM/WizardMath-7B-V1.1")

prompt = "<s>result of 9 + 9 = 18</s><s>result of 1 + 2 = "
answer = outlines.generate.format(model, int)(prompt)
print(answer)
# 3

prompt = "sqrt(2)="
generator = outlines.generate.format(model, float)
answer = generator(prompt, max_tokens=10)
print(answer)
# 1.41421356
```

### Efficient regex-structured generation

Outlines also comes with fast regex-structured generation. In fact, the `choice` and
`format` functions above all use regex-structured generation under the
hood:

``` python
import outlines

model = outlines.models.transformers("mistralai/Mistral-7B-Instruct-v0.2")

prompt = "What is the IP address of the Google DNS servers? "

generator = outlines.generate.text(model)
unstructured = generator(prompt, max_tokens=30)

generator = outlines.generate.regex(
    model,
    r"((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)",
)
structured = generator(prompt, max_tokens=30)

print(unstructured)
# What is the IP address of the Google DNS servers?
#
# Passive DNS servers are at DNS servers that are private.
# In other words, both IP servers are private. The database
# does not contain Chelsea Manning

print(structured)
# What is the IP address of the Google DNS servers?
# 2.2.6.1
```

Unlike other libraries, regex-structured generation in Outlines is almost as fast
as non-structured generation.

### Efficient JSON generation following a Pydantic model

Outlines 〰 allows to guide the generation process so the output is *guaranteed* to follow a [JSON schema](https://json-schema.org/) or [Pydantic model](https://docs.pydantic.dev/latest/):

```python
from enum import Enum
from pydantic import BaseModel, constr

import outlines
import torch


class Weapon(str, Enum):
    sword = "sword"
    axe = "axe"
    mace = "mace"
    spear = "spear"
    bow = "bow"
    crossbow = "crossbow"


class Armor(str, Enum):
    leather = "leather"
    chainmail = "chainmail"
    plate = "plate"


class Character(BaseModel):
    name: constr(max_length=10)
    age: int
    armor: Armor
    weapon: Weapon
    strength: int


model = outlines.models.transformers("mistralai/Mistral-7B-Instruct-v0.2")

# Construct structured sequence generator
generator = outlines.generate.json(model, Character)

# Draw a sample
rng = torch.Generator(device="cuda")
rng.manual_seed(789001)

character = generator("Give me a character description", rng=rng)

print(repr(character))
# Character(name='Anderson', age=28, armor=<Armor.chainmail: 'chainmail'>, weapon=<Weapon.sword: 'sword'>, strength=8)

character = generator("Give me an interesting character description", rng=rng)

print(repr(character))
# Character(name='Vivian Thr', age=44, armor=<Armor.plate: 'plate'>, weapon=<Weapon.crossbow: 'crossbow'>, strength=125)
```

The method works with union types, optional types, arrays, nested schemas, etc. Some field constraints are [not supported yet](https://github.com/outlines-dev/outlines/issues/215), but everything else should work.