import pygame
from core.game import GameState, Phase
from core.card import Card, CardType

BG=(10,8,22); ZE=(25,20,45); ZF=(35,28,65); ZB=(70,55,120); ZH=(90,75,155)
CB=(40,30,70); TP=(230,225,255); TS=(150,140,190); GO=(220,185,80)
RE=(220,70,70); GR=(70,200,120); BL=(100,160,255); LB=(20,15,40)

class DuelScreen:
    def __init__(self, screen, gs: GameState):
        self.screen=screen; self.gs=gs
        self.W,self.H=screen.get_size()
        self.fl=pygame.font.SysFont("Arial",22,bold=True)
        self.fm=pygame.font.SysFont("Arial",16,bold=True)
        self.fs=pygame.font.SysFont("Arial",13)
        self.sel=None
        self._layout()
        for _ in range(5):
            self.gs.player.draw_card()
            self.gs.opponent.draw_card()
        self.gs.log(f"Duel start! {self.gs.rules.display_name} rules.")
        self.gs.log(f"You vs. {self.gs.rules.opponent_name}")

    def _layout(self):
        cw,ch=88,120; gap=10
        oy=80; py=self.H-80-ch
        self.omz=[pygame.Rect(180+i*(cw+gap),oy,cw,ch) for i in range(5)]
        self.pmz=[pygame.Rect(180+i*(cw+gap),py,cw,ch) for i in range(5)]
        self.osz=[pygame.Rect(180+i*(cw+gap),oy+ch+8,cw,60) for i in range(5)]
        self.psz=[pygame.Rect(180+i*(cw+gap),py-68,cw,60) for i in range(5)]
        self.hand_area=pygame.Rect(0,self.H-75,self.W-320,75)
        self.log_area =pygame.Rect(self.W-310,0,310,self.H-100)
        self.btn_adv  =pygame.Rect(self.W-310,self.H-95,148,40)
        self.btn_menu =pygame.Rect(self.W-155,self.H-95,148,40)

    def _hand_rects(self):
        h=self.gs.player.hand
        if not h: return []
        cw=min(90,(self.hand_area.width-20)//max(len(h),1))
        return [pygame.Rect(10+i*(cw+5),self.H-70,cw,62) for i in range(len(h))]

    def _slot(self,rect,card,back=False,hl=False):
        c=ZH if hl else (ZF if card else ZE)
        b=GO if hl else ZB
        pygame.draw.rect(self.screen,c,rect,border_radius=6)
        pygame.draw.rect(self.screen,b,rect,width=1,border_radius=6)
        if card and not back:
            self.screen.blit(self.fs.render(card.name[:12],True,TP),(rect.x+4,rect.y+6))
            if card.atk is not None:
                self.screen.blit(self.fs.render(str(card.atk),True,GR),(rect.x+4,rect.y+rect.height-20))
        elif back:
            pygame.draw.rect(self.screen,CB,rect.inflate(-6,-6),border_radius=4)

    def update(self, events):
        mx,my=pygame.mouse.get_pos()
        for e in events:
            if e.type==pygame.MOUSEBUTTONDOWN and e.button==1:
                if self.btn_adv.collidepoint(mx,my):
                    self.gs.advance_phase()
                    if self.gs.current_phase==Phase.DRAW:
                        d=self.gs.player.draw_card()
                        if d: self.gs.log(f"Drew: {d.name}")
                if self.btn_menu.collidepoint(mx,my): return "menu"
                for i,r in enumerate(self._hand_rects()):
                    if r.collidepoint(mx,my): self.sel=i
                if self.sel is not None and self.sel<len(self.gs.player.hand):
                    card=self.gs.player.hand[self.sel]
                    for i,z in enumerate(self.pmz):
                        if z.collidepoint(mx,my) and self.gs.player.field_monsters[i] is None:
                            if card.card_type==CardType.MONSTER:
                                self.gs.player.place_monster(card,i)
                                self.gs.log(f"Summoned {card.name}!"); self.sel=None
        return None

    def draw(self):
        self.screen.fill(BG)
        pygame.draw.line(self.screen,ZB,(170,0),(170,self.H),1)
        for i,z in enumerate(self.omz): self._slot(z,self.gs.opponent.field_monsters[i],back=True)
        for z in self.osz: self._slot(z,None)
        for i,z in enumerate(self.pmz): self._slot(z,self.gs.player.field_monsters[i])
        for z in self.psz: self._slot(z,None)
        self.screen.blit(self.fl.render(f"Your LP: {self.gs.player.lp:,}",True,GR),(10,self.H-240))
        self.screen.blit(self.fl.render(f"{self.gs.opponent.name}: {self.gs.opponent.lp:,}",True,RE),(10,20))
        self.screen.blit(self.fm.render(self.gs.current_phase.value,True,GO),(10,self.H//2-10))
        self.screen.blit(self.fs.render(f"Turn {self.gs.turn_number}",True,TS),(10,self.H//2+20))
        for i,(r,c) in enumerate(zip(self._hand_rects(),self.gs.player.hand)):
            self._slot(r,c,hl=(i==self.sel))
        pygame.draw.rect(self.screen,LB,self.log_area)
        self.screen.blit(self.fm.render("Duel Log",True,GO),(self.log_area.x+8,8))
        vis=self.log_area.height//18-2
        for j,m in enumerate(self.gs.duel_log[-vis:]):
            self.screen.blit(self.fs.render(m[:44],True,TS),(self.log_area.x+8,34+j*18))
        for btn,label in [(self.btn_adv,"Next Phase >"),(self.btn_menu,"< Menu")]:
            pygame.draw.rect(self.screen,ZF,btn,border_radius=8)
            pygame.draw.rect(self.screen,ZB,btn,width=1,border_radius=8)
            s=self.fm.render(label,True,TP)
            self.screen.blit(s,(btn.centerx-s.get_width()//2,btn.centery-s.get_height()//2))