from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class CardType(Enum):
    MONSTER="Monster Card"
    SPELL="Spell Card"
    TRAP="Trap Card"


class MonsterType(Enum):
    NORMAL="Normal Monster"
    EFFECT="Effect Monster"
    FUSION="Fusion Monster"
    SYNCHRO="Synchro Monster"
    XYZ="XYZ Monster"
    PENDULUM="Pendulum Monster"

class CardPosition(Enum):
    ATTACK="ATK"
    DEFENSE="DEF"
    FACE_DOWN="Set" 


@dataclass
class Card:
    id:int
    name: str
    card_type: CardType
    description: str
    atk: Optional[int] = None
    defense: Optional[int] = None
    level: Optional[int] = None
    attribute: Optional[str] = None
    monster_type: Optional[MonsterType] = None
    race: Optional[str] = None
    is_tuner: bool = False
    pendulum_scale: Optional[int] = None
    pendulum_effect: Optional[str] = None
    series: list = field(default_factory=list)
    position: CardPosition = CardPosition.ATTACK
    is_face_up: bool = True
    xyz_materials: list = field(default_factory=list)

    def __str__(self):
        if self.card_type==CardType.MONSTER:
            return f"{self.name} (Lv{self.level} {self.race} | ATK:{self.atk} DEF:{self.defense})"
        return f"{self.name}, ({self.card_type.value})"
    
    def tributes_required(self) -> int:
        if self.level is None or self.level <= 4:
            return 0
        elif self.level <= 6:
            return 1
        return 2
    

