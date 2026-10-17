# Dungeon Master (Gemma 4)

A solo Dungeons & Dragons 5e text adventure where a **Gemma 4** Dungeon Master narrates the story, you act by **typing or drawing**, and a **real d20** decides how it goes.

Built for the **"Best Use of Gemma 4"** hackathon track (creativity category). Gemma 4 is used through the Gemini API.

## What it does

- **Create a hero**: pick a name, a class (Fighter, Wizard, Rogue, Cleric, Ranger, Barbarian, Bard), a setting (dark forest, ancient crypt, mountain pass, murky swamp, forgotten dungeon, ruined castle, or surprise me) and a difficulty (the highest creature challenge rating you will face).
- **A real SRD monster**: Python picks a creature that fits the setting and difficulty from the free D&D 5e SRD bestiary. The Dungeon Master has to use its exact stats. In scene 1 the creature is only hinted at (the model is not even told its name), and the Creature Card says *"Something lurks nearby..."*. From scene 2 the card shows its real stats and HP.
- **Draw your action (multimodal)**: upload or photograph a quick drawing of what you want to do, such as a shield to defend, an arrow to shoot, flames to cast a fire spell, or a door to flee. Gemma looks at the image, works out the action, and tells you what it saw. You can add a typed caption too.
- **Real dice**: each turn you submit your action, then click **Roll the d20**. You get one roll per turn, and the number is generated in Python, not by the model. The DM adds the matching ability modifier from your class sheet and compares the total to a difficulty class it chooses. A natural 1 always fails and a natural 20 always succeeds.
- **Character sheet and creature card**: a parchment-style panel pinned to the bottom-left shows your HP bar, the six ability modifiers and scores, and your inventory, with the creature card above it.
- **LitRPG narration**: second-person DM voice with bracketed system messages such as `[Ability Check: Stealth 14 vs DC 12 - Success]` and `[-6 HP]`. Every scene ends by asking what you do.
- **No scene limit**: the adventure ends when you or the creature reaches 0 HP.

## How a turn works

1. Type an action, or upload or photograph a drawing, then click **Submit action**.
2. Click **Roll the d20**. The die tumbles, and a natural 20 turns it gold while a natural 1 turns it red.
3. Gemma narrates the result using your roll, updates your stats, and adjusts the creature's HP.
4. Repeat until someone falls.

## Setup

Requirements: Python 3 and a Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey).

```bash
python -m venv venv
source venv/bin/activate
pip install gradio google-genai pillow requests    # or: pip install -r requirements.txt
python build_monsters.py                           # downloads monsters.json (once)
export GEMINI_API_KEY="your-key"
python app.py
```

Open http://127.0.0.1:7860 and hard-refresh (Ctrl+F5) after each restart.

Keep your API key in your shell environment only. Never paste it into code, screenshots or logs. If a key ever leaks, rotate it at the link above.

### Choosing the model

The default is `gemma-4-26b-a4b-it`. To try the larger one:

```bash
export GEMMA_MODEL="gemma-4-31b-it"
```

## Files

| File | Purpose |
| --- | --- |
| `app.py` | The Gradio app: UI, game logic, dice, prompts, model calls |
| `build_monsters.py` | Downloads the SRD monsters and saves a compact `monsters.json` |
| `monsters.json` | Generated bestiary (about 334 creatures) |
| `requirements.txt` | Python dependencies |

## Design notes

- **The model writes, Python keeps score.** Dice, creature choice, creature HP limits and the end-of-game check all live in Python, so the model can't quietly change the numbers.
- **Structured output.** Each reply is a JSON object (title, passage, system messages, stats, `monster_hp`, and an `action_summary` when you send a drawing). A tolerant parser handles code fences and falls back safely if the JSON is malformed.
- **Resilient calls.** Requests have a 150 second timeout and retry once on server errors or timeouts, with a clear error message if Google's side is busy.
- **Short memory.** Only the last two scenes are sent back to the model each turn, which keeps requests small.

## Known limitations

- **Latency.** A turn usually takes 40 to 70 seconds, and sometimes longer. Most of that time is the model reasoning before it writes, and that cannot be turned off for this model through the API. Server errors (500/504) from Google's side happen occasionally, and clicking the button again retries.
- **Drawings are interpreted, not guaranteed.** Simple, bold drawings work best. If the model misreads one, add a short typed caption.
- **SRD only.** Only creatures from the freely licensed SRD are available, not the full Monster Manual.
- **Pacing depends on the model.** The creature's HP only drops when the model decides your hits land, so a fight against a high-HP creature can run long. Easy or medium difficulty gives shorter games.

## Credits and licensing

Creature data comes from the 5e SRD via the community-maintained [5e-bits](https://github.com/5e-bits/5e-database) database and [dnd5eapi.co](https://www.dnd5eapi.co).

This work includes material from the System Reference Document 5.1 ("SRD 5.1") by Wizards of the Coast LLC, available at https://dnd.wizards.com/resources/systems-reference-document. The SRD 5.1 is licensed under the Creative Commons Attribution 4.0 International License, available at https://creativecommons.org/licenses/by/4.0/legalcode.
