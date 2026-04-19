from dataclasses import dataclass
from typing import List
from core.card import MonsterType

@dataclass
class SeriesRules:
    name: str
    display_name: str
    starting_lp: int
    allowed_summon_types: List[MonsterType]
    opponent_name: str
    opponent_deck: str
    flavor_text: str
    era_description: str

    def can_synchro_summon(self): return MonsterType.SYNCHRO in self.allowed_summon_types
    def can_xyz_summon(self):     return MonsterType.XYZ in self.allowed_summon_types
    def can_pendulum_summon(self):return MonsterType.PENDULUM in self.allowed_summon_types

SERIES_RULES = {
    "dm": SeriesRules("dm","Duel Monsters",8000,
        [MonsterType.NORMAL,MonsterType.EFFECT,MonsterType.FUSION,MonsterType.RITUAL],
        "Seto Kaiba","Blue-Eyes White Dragon",
        "Shadow Games. The monsters are real.","Classic rules."),
    "gx": SeriesRules("gx","GX",8000,
        [MonsterType.NORMAL,MonsterType.EFFECT,MonsterType.FUSION,MonsterType.RITUAL],
        "Chazz Princeton","Armed Dragon",
        "Duel Academy. Prove you belong.","Fusion-heavy era."),
    "5ds": SeriesRules("5ds","5D's",8000,
        [MonsterType.NORMAL,MonsterType.EFFECT,MonsterType.FUSION,MonsterType.RITUAL,MonsterType.SYNCHRO],
        "Jack Atlas","Red Dragon Archfiend",
        "Riding Duels. Synchro summon.","Synchro era."),
    "zexal": SeriesRules("zexal","ZEXAL",4000,
        [MonsterType.NORMAL,MonsterType.EFFECT,MonsterType.FUSION,MonsterType.RITUAL,MonsterType.SYNCHRO,MonsterType.XYZ],
        "Reginald 'Shark' Kastle","Shark / Water Xyz",
        "Heartland City. Collect the Numbers.","Xyz era. 4000 LP!"),
    "arc": SeriesRules("arc","ARC-V",8000,
        [MonsterType.NORMAL,MonsterType.EFFECT,MonsterType.FUSION,MonsterType.RITUAL,MonsterType.SYNCHRO,MonsterType.XYZ,MonsterType.PENDULUM],
        "Declan Akaba","D/D/D Pendulum",
        "Four dimensions. Pendulum everything.","Pendulum era."),
}

def get_rules(series_name: str) -> SeriesRules:
    if series_name not in SERIES_RULES:
        raise ValueError(f"Unknown series: {series_name}")
    return SERIES_RULES[series_name]