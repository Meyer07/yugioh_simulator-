# Yu-Gi-Oh! Anime Duel Simulator

A desktop duel simulator built in Python + Pygame.

## Setup

```bash
pip install -r requirements.txt
python main.py
```

## Series & Rules

| Series        | LP   | Special Mechanic | Opponent              |
|---------------|------|------------------|-----------------------|
| Duel Monsters | 4000 | Classic only     | Seto Kaiba            |
| GX            | 4000 | Fusion focus     | Chazz Princeton       |
| 5D's          | 4000 | Synchro summon   | Jack Atlas            |
| ZEXAL         | 4000 | Xyz summon       | Shark Kastle          |
| ARC-V         | 4000 | Pendulum summon  | Declan Akaba          |

## Project Structure

```
yugioh_simulator/
├── main.py          # Entry point
├── requirements.txt
├── core/
│   ├── card.py      # Card data model
│   ├── rules.py     # Per-series rulesets
│   └── game.py      # Game state & turn logic
├── ui/
│   ├── menu.py      # Series selection screen
│   └── duel.py      # Duel field renderer
└── data/
    ├── cards.json   # Card database
    └── decks.json   # Anime starter decks
```

## What's Built

- [x] Series selection menu (all 5 anime)
- [x] Card data model (monsters, spells, traps, all summon types)
- [x] Per-series rules engine (LP, allowed summon types)
- [x] Game state (turns, phases, LP tracking)
- [x] Duel field UI (monster zones, spell zones, hand, log)
- [x] Basic summoning from hand
- [x] Draw phase + phase advancement

## Next Steps

- [ ] Battle phase & damage calculation
- [ ] Card effect system
- [ ] AI opponent
- [ ] Synchro/Xyz/Pendulum summon UI
- [ ] Card images from YGOPRO API