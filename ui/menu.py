import pygame
from core.rules import SERIES_RULES

BG=(15,12,30); CARD=(30,25,55); HOVER=(45,38,80); BORDER=(80,65,140)
PRI=(230,225,255); SEC=(160,150,200); ACCENT=(180,150,255); GOLD=(220,185,80)

class MenuScreen:
    def __init__(self, screen):
        self.screen = screen
        self.W, self.H = screen.get_size()
        self.f_title = pygame.font.SysFont("Georgia",42,bold=True)
        self.f_sub   = pygame.font.SysFont("Arial",18)
        self.f_card  = pygame.font.SysFont("Arial",20,bold=True)
        self.f_small = pygame.font.SysFont("Arial",14)
        self.series  = list(SERIES_RULES.values())
        self.hovered = None
        self.rects   = []
        self._layout()

    def _layout(self):
        n=len(self.series); cw,ch=210,180; gap=20
        total=n*cw+(n-1)*gap
        sx=(self.W-total)//2; y=self.H//2-40
        self.rects=[pygame.Rect(sx+i*(cw+gap),y,cw,ch) for i in range(n)]

    def update(self, events):
        mx,my=pygame.mouse.get_pos(); self.hovered=None
        for i,r in enumerate(self.rects):
            if r.collidepoint(mx,my): self.hovered=i
        for e in events:
            if e.type==pygame.MOUSEBUTTONDOWN and e.button==1 and self.hovered is not None:
                return self.series[self.hovered].name
        return None

    def draw(self):
        self.screen.fill(BG)
        t=self.f_title.render("Yu-Gi-Oh! Anime Duel Simulator",True,GOLD)
        self.screen.blit(t,(self.W//2-t.get_width()//2,80))
        s=self.f_sub.render("Choose your anime series to begin dueling",True,SEC)
        self.screen.blit(s,(self.W//2-s.get_width()//2,140))
        for i,(r,sr) in enumerate(zip(self.rects,self.series)):
            c=HOVER if i==self.hovered else CARD
            b=GOLD  if i==self.hovered else BORDER
            pygame.draw.rect(self.screen,c,r,border_radius=12)
            pygame.draw.rect(self.screen,b,r,width=2,border_radius=12)
            n=self.f_card.render(sr.display_name,True,PRI)
            self.screen.blit(n,(r.centerx-n.get_width()//2,r.y+18))
            lp=self.f_small.render(f"LP: {sr.starting_lp:,}",True,ACCENT)
            self.screen.blit(lp,(r.centerx-lp.get_width()//2,r.y+52))
            op=self.f_small.render(f"vs. {sr.opponent_name[:20]}",True,SEC)
            self.screen.blit(op,(r.centerx-op.get_width()//2,r.y+74))
            words=sr.flavor_text.split(); lines=[]; line=[]
            for w in words:
                line.append(w)
                if self.f_small.size(" ".join(line))[0]>r.width-20:
                    lines.append(" ".join(line[:-1])); line=[w]
            if line: lines.append(" ".join(line))
            for j,l in enumerate(lines[:3]):
                surf=self.f_small.render(l,True,SEC)
                self.screen.blit(surf,(r.centerx-surf.get_width()//2,r.y+108+j*18))