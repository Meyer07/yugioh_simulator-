import json,os,random
from enum import Enum
from typing import List, Optional
from core.card import Card, CardType, MonsterType, CardPosition
from core.rules import SeriesRules, get_rules

class Phase(Enum):
    DRAW="Draw Phase"
    STANDBY="Standby Phase"
    MAIN1="Main Phase 1"
    BATTLE="Battle Phase"
    MAIN2="Main Phase 2"
    END="End Phase"

class Player():
    def __init__(self,name,starting_lp):
        self.name=name
        self.lp=starting_lp
        self.hand: List[Card] = []
        self.deck: List[Card] = []
        self.graveyard: List[Card] = []
        self.field_monsters: List[Optional[Card]] = [None]*5
        self.field_spells:   List[Optional[Card]] = [None]*5
        self.extra_deck: List[Card] = []
        self.has_normal_summoned=False

    def draw_card(self):
        if not self.deck:
            return None
        card=self.deck.pop(0)
        self.hand.append(card)
        return card
    
    def take_damage(self,amount):
        self.lp=max(0,self.lp-amount)
    
    def gain_life(self,amount):
        self.lp+=amount
    
    def monster_zone_available(self):
        return any(s is None for s in self.field_monsters)
    
    def place_monster(self,card,zone_index,position:CardPosition=CardPosition.ATTACK,face_up=True):
        self.field_monsters[zone_index]=card
        card.is_face_up = face_up
        card.position   = position
        if card in self.hand:
            self.hand.remove(card)
        
    def send_graveyard(self,card):
        self.graveyard.append(card)
        for i,s in enumerate(self.field_monsters):
            if s==card:
                self.field_monsters[i]=None
                return 
        for i,s in enumerate(self.field_st):
            if s==card:
                self.field_spells[i]=None
                return
        
    def shuffle_deck(self):
        random.shuffle(self.deck)
    
class GameState:

    def __init__(self,series:str):
        self.rules: SeriesRules = get_rules(series)
        self.series = series
        self.player   = Player("You", self.rules.starting_lp)
        self.opponent = Player(self.rules.opponent_name, self.rules.starting_lp)
        self.turn_number   = 1
        self.current_phase = Phase.DRAW
        self.active_player = self.player
        self.duel_log: List[str] = []
        self.winner: Optional[str] = None
        self._load_decks()
        self.player.shuffle_deck()
        self.opponent.shuffle_deck()
    
    def _card_from_dict(self,d):
        ct = CardType(d.get("card_type","Monster"))
        mt = MonsterType(d["monster_type"]) if d.get("monster_type") else None
        return Card (id=d["id"],name=d["name"],card_type=ct,description=d.get("description",""),atk=d.get("atk"),defense=d.get("def"),level=d.get("level"),
            attribute=d.get("attribute"),monster_type=mt,race=d.get("race"),
            is_tuner=d.get("is_tuner",False),pendulum_scale=d.get("pendulum_scale"),
            pendulum_effect=d.get("pendulum_effect"),series=d.get("series",[]))
    
    def _load_decks(self):
        base = os.path.dirname(__file__)
        cp = os.path.join(base,"..","data","cards.json")
        dp = os.path.join(base,"..","data","decks.json")
        try:
            with open(cp) as f: cards_data = json.load(f)
            with open(dp) as f: decks = json.load(f)
        except FileNotFoundError:
            self.log("Warning: data files not found."); return
        lookup = {c["id"]: self._card_from_dict(c) for c in cards_data}
        pd = decks.get(self.series,{})
        self.player.deck   = [lookup[i] for i in pd.get("player",[])   if i in lookup]
        self.opponent.deck = [lookup[i] for i in pd.get("opponent",[]) if i in lookup]
    
    def can_normal_summon(self)->bool:
        return(
            self.active_player==self.player
            and not self.player.has_normal_summoned
            and self.current_phase in (Phase.MAIN1,Phase.MAIN2)
            )
    
    def normal_summon(self,card:Card,zone_index:int)->bool:
        if not self.can_normal_summon():
            self.log("You have already normal summoned this turn")
            return False
        tributes=card.tributes_required()
        monsters_on_field=sum(1 for m in self.player.field_monsters if m is not None)
        if monsters_on_field<tributes:
            self.log(f"{card.name} needs {tributes} tribute(s) - not enough tributes")
            return False
        self.player.place_monster(card,zone_index,face_up=True,position=CardPosition.ATTACK)
        self.player.has_normal_summoned=True
        self.log(f"{card.name} has been normal summoned!")
        return True
        
    
    def set_monster(self,card:Card,zone_index:int)->bool:
        if not self.can_normal_summon:
            self.log("You have already normal summoned this turn")
            return False
        tributes = card.tributes_required()
        monsters_on_field = sum(1 for m in self.player.field_monsters if m is not None)
        if monsters_on_field < tributes:
            self.log(f"{card.name} needs {tributes} tribute(s) to set!")
            return False
        self.player.place_monster(card, zone_index, face_up=False, position=CardPosition.DEFENSE)
        self.player.has_normal_summoned = True
        self.log(f"Set a monster face-down in DEF position.")
        return True
        

    def log(self, msg):
        self.duel_log.append(msg)
    
    def advance_phase(self):
        phases = list(Phase)
        idx = phases.index(self.current_phase)
        if idx < len(phases)-1:
            self.current_phase = phases[idx+1]
        else:
            self._end_turn()
 
    def _end_turn(self):
        self.active_player.has_normal_summoned = False
        self.active_player = self.opponent if self.active_player == self.player else self.player
        self.turn_number += 1
        self.current_phase = Phase.DRAW
        self.log(f"--- Turn {self.turn_number}: {self.active_player.name} ---")
 
    def check_win_condition(self):
        if self.player.lp   <= 0: self.winner = self.opponent.name
        elif self.opponent.lp <= 0: self.winner = self.player.name
        return self.winner

            




