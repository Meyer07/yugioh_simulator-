import pygame
from core.game import GameState, Phase
from core.card import Card, CardType, CardPosition

# ── palette ───────────────────────────────────────────────────────────────────
BG=(10,8,22);   ZE=(25,20,45);  ZF=(35,28,65);  ZB=(70,55,120);  ZH=(90,75,155)
CB=(40,30,70);  TP=(230,225,255); TS=(150,140,190); GO=(220,185,80)
RE=(220,70,70); GR=(70,200,120);  LB=(20,15,40)
SPELL_COL=(30,60,45);   TRAP_COL=(60,30,45)
SPELL_BDR=(80,180,120); TRAP_BDR=(180,80,120)
POPUP_BG=(18,14,38);    POPUP_BD=(100,80,160)
BTN_NRM=(40,80,55);     BTN_SET=(60,40,80)
BTN_NRM_BD=(80,180,120); BTN_SET_BD=(160,100,200)
CTX_BG=(22,18,44);      CTX_BD=(90,70,150)
CTX_HOVER=(45,35,80)


class DuelScreen:
    def __init__(self, screen, gs: GameState):
        self.screen = screen
        self.gs     = gs
        self.W, self.H = screen.get_size()
        self.fl  = pygame.font.SysFont("Arial", 22, bold=True)
        self.fm  = pygame.font.SysFont("Arial", 16, bold=True)
        self.fs  = pygame.font.SysFont("Arial", 13)
        self.fxs = pygame.font.SysFont("Arial", 11)

        self.sel         = None   # selected hand card index
        self.tooltip     = None   # hovered hand card

        # Summon popup
        self.popup_card  = None
        self.popup_zone  = None
        self.popup_rect  = None
        self.btn_summon  = None
        self.btn_set_mon = None
        self.btn_cancel  = None

        # Right-click context menu
        self.ctx_card    = None   # card the menu is for
        self.ctx_owner   = None   # "player" or "opponent"
        self.ctx_rect    = None   # panel rect
        self.ctx_items   = []     # list of (label, action_fn, rect)

        self._layout()

        for _ in range(5):
            self.gs.player.draw_card()
            self.gs.opponent.draw_card()

        self.gs.log(f"Duel start! {self.gs.rules.display_name} rules.")
        self.gs.log(f"You vs. {self.gs.rules.opponent_name}")
        self.gs.log("Left-click cards to select/place.")
        self.gs.log("Right-click field cards for options.")

    # ── layout ────────────────────────────────────────────────────────────────
    def _layout(self):
        cw, ch = 88, 120
        gap = 10
        oy  = 80
        py  = self.H - 80 - ch
        self.omz = [pygame.Rect(180+i*(cw+gap), oy,      cw, ch) for i in range(5)]
        self.pmz = [pygame.Rect(180+i*(cw+gap), py,      cw, ch) for i in range(5)]
        self.osz = [pygame.Rect(180+i*(cw+gap), oy+ch+8, cw, 60) for i in range(5)]
        self.psz = [pygame.Rect(180+i*(cw+gap), py-68,   cw, 60) for i in range(5)]
        self.hand_area    = pygame.Rect(0,          self.H-75,    self.W-320, 75)
        self.log_area     = pygame.Rect(self.W-310, 0,            310, self.H-100)
        self.btn_adv      = pygame.Rect(self.W-310, self.H-95,    148, 40)
        self.btn_menu     = pygame.Rect(self.W-155, self.H-95,    148, 40)
        self.tooltip_rect = pygame.Rect(5,          self.H//2-90, 164, 180)

    # ── summon popup ──────────────────────────────────────────────────────────
    def _build_popup(self, zone_rect):
        pw, ph = 200, 130
        px = min(zone_rect.centerx - pw//2, self.W - pw - 10)
        px = max(px, 10)
        py = zone_rect.y - ph - 8
        if py < 10:
            py = zone_rect.bottom + 8
        self.popup_rect  = pygame.Rect(px, py, pw, ph)
        self.btn_summon  = pygame.Rect(px+10, py+36,  pw-20, 30)
        self.btn_set_mon = pygame.Rect(px+10, py+72,  pw-20, 30)
        self.btn_cancel  = pygame.Rect(px+10, py+108, pw-20, 18)

    def _close_popup(self):
        self.popup_card = self.popup_zone = self.popup_rect = None
        self.btn_summon = self.btn_set_mon = self.btn_cancel = None

    # ── context menu ──────────────────────────────────────────────────────────
    def _open_ctx(self, card: Card, owner: str, mx: int, my: int):
        """Build a right-click context menu for a field card."""
        self.ctx_card  = card
        self.ctx_owner = owner
        options = []

        if owner == "player":
            # Send to graveyard always available
            options.append(("Send to Graveyard",
                            lambda: self.gs.send_to_graveyard(card, "player")))

            if card.card_type == CardType.MONSTER:
                if not card.is_face_up:
                    # Face-down monster: offer flip
                    options.append(("Flip Face-Up (Flip Summon)",
                                    lambda: self.gs.flip_face_up(card)))
                else:
                    # Face-up monster: offer position change
                    pos_lbl = "Change to DEF" if card.position == CardPosition.ATTACK else "Change to ATK"
                    options.append((pos_lbl,
                                    lambda: self.gs.change_position(card)))

        # Panel geometry
        item_h = 28
        pw     = 210
        ph     = 10 + len(options) * item_h + 8
        px     = min(mx, self.W - pw - 4)
        py_    = min(my, self.H - ph - 4)

        self.ctx_rect  = pygame.Rect(px, py_, pw, ph)
        self.ctx_items = []
        for idx, (label, fn) in enumerate(options):
            r = pygame.Rect(px+4, py_+6+idx*item_h, pw-8, item_h-2)
            self.ctx_items.append((label, fn, r))

    def _close_ctx(self):
        self.ctx_card = self.ctx_owner = self.ctx_rect = None
        self.ctx_items = []

    # ── hand rects ────────────────────────────────────────────────────────────
    def _hand_rects(self):
        h = self.gs.player.hand
        if not h:
            return []
        cw = min(90, (self.hand_area.width-20) // max(len(h), 1))
        return [pygame.Rect(10+i*(cw+5), self.H-70, cw, 62) for i in range(len(h))]

    # ── slot renderer ─────────────────────────────────────────────────────────
    def _slot(self, rect, card, back=False, hl=False, spell_trap=False, greyed=False):
        if greyed:
            bg, border = (30,28,42), (55,50,75)
        elif hl:
            bg, border = ZH, GO
        elif card and spell_trap:
            bg     = SPELL_COL if card.card_type == CardType.SPELL else TRAP_COL
            border = SPELL_BDR if card.card_type == CardType.SPELL else TRAP_BDR
        elif card:
            bg, border = ZF, ZB
        else:
            bg, border = ZE, ZB

        pygame.draw.rect(self.screen, bg,     rect, border_radius=6)
        pygame.draw.rect(self.screen, border, rect, width=1, border_radius=6)

        if back:
            pygame.draw.rect(self.screen, CB, rect.inflate(-6,-6), border_radius=4)
            lbl = self.fxs.render("SET", True, TS)
            self.screen.blit(lbl, (rect.centerx-lbl.get_width()//2,
                                   rect.centery-lbl.get_height()//2))
        elif card and not greyed:
            self.screen.blit(self.fs.render(card.name[:12], True, TP), (rect.x+4, rect.y+6))
            if spell_trap:
                tl = self.fxs.render(card.card_type.value, True, border)
                self.screen.blit(tl, (rect.x+4, rect.y+22))
            else:
                pos_lbl = "ATK" if card.position == CardPosition.ATTACK else "DEF"
                pos_col = GR    if card.position == CardPosition.ATTACK else (100,150,220)
                self.screen.blit(self.fxs.render(pos_lbl, True, pos_col), (rect.x+4, rect.y+22))
                if card.atk is not None:
                    self.screen.blit(self.fs.render(str(card.atk), True, GR),
                                     (rect.x+4, rect.y+rect.height-20))
        elif greyed:
            dash = self.fxs.render("—", True, (70,65,90))
            self.screen.blit(dash, (rect.centerx-dash.get_width()//2,
                                    rect.centery-dash.get_height()//2))

    def _label(self, text, x, y, color=None):
        self.screen.blit(self.fxs.render(text, True, color or TS), (x, y))

    def _button(self, rect, label, bg, border, text_col=TP):
        pygame.draw.rect(self.screen, bg,     rect, border_radius=6)
        pygame.draw.rect(self.screen, border, rect, width=1, border_radius=6)
        s = self.fs.render(label, True, text_col)
        self.screen.blit(s, (rect.centerx-s.get_width()//2,
                              rect.centery-s.get_height()//2))

    # ── update ────────────────────────────────────────────────────────────────
    def update(self, events):
        mx, my = pygame.mouse.get_pos()
        self.tooltip = None

        if not self.popup_card and not self.ctx_card:
            for i, r in enumerate(self._hand_rects()):
                if r.collidepoint(mx, my) and i < len(self.gs.player.hand):
                    self.tooltip = self.gs.player.hand[i]

        for e in events:
            # ── right-click: open context menu on field cards ────────────────
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 3:
                self._close_popup()
                self._close_ctx()
                # Player monster zones
                for i, z in enumerate(self.pmz):
                    if z.collidepoint(mx, my) and self.gs.player.field_monsters[i]:
                        self._open_ctx(self.gs.player.field_monsters[i], "player", mx, my)
                        break
                # Player spell/trap zones
                for i, z in enumerate(self.psz):
                    if z.collidepoint(mx, my) and self.gs.player.field_spells[i]:
                        self._open_ctx(self.gs.player.field_spells[i], "player", mx, my)
                        break
                continue

            if e.type != pygame.MOUSEBUTTONDOWN or e.button != 1:
                continue

            # ── context menu click ───────────────────────────────────────────
            if self.ctx_card is not None:
                clicked_item = False
                for label, fn, r in self.ctx_items:
                    if r.collidepoint(mx, my):
                        fn()
                        clicked_item = True
                        break
                self._close_ctx()
                if clicked_item:
                    continue
                # click outside = just close
                continue

            # ── summon popup ─────────────────────────────────────────────────
            if self.popup_card is not None:
                if self.btn_summon.collidepoint(mx, my):
                    self.gs.normal_summon(self.popup_card, self.popup_zone)
                elif self.btn_set_mon.collidepoint(mx, my):
                    self.gs.set_monster(self.popup_card, self.popup_zone)
                self._close_popup()
                continue

            # ── nav buttons ──────────────────────────────────────────────────
            if self.btn_adv.collidepoint(mx, my):
                self.gs.advance_phase()
                if self.gs.current_phase == Phase.DRAW:
                    drawn = self.gs.player.draw_card()
                    if drawn:
                        self.gs.log(f"Drew: {drawn.name}")
                continue

            if self.btn_menu.collidepoint(mx, my):
                return "menu"

            # ── select hand card ─────────────────────────────────────────────
            clicked_hand = False
            for i, r in enumerate(self._hand_rects()):
                if r.collidepoint(mx, my):
                    self.sel = None if self.sel == i else i
                    clicked_hand = True
                    break
            if clicked_hand:
                continue

            # ── place selected card ──────────────────────────────────────────
            if self.sel is not None and self.sel < len(self.gs.player.hand):
                card = self.gs.player.hand[self.sel]

                if card.card_type == CardType.MONSTER:
                    for i, z in enumerate(self.pmz):
                        if z.collidepoint(mx, my) and self.gs.player.field_monsters[i] is None:
                            if self.gs.current_phase not in (Phase.MAIN1, Phase.MAIN2):
                                self.gs.log("Advance to Main Phase 1 before summoning.")
                            elif self.gs.player.has_normal_summoned:
                                self.gs.log("Already normal summoned this turn!")
                            else:
                                self.popup_card = card
                                self.popup_zone = i
                                self._build_popup(z)
                            self.sel = None
                            break

                elif card.card_type in (CardType.SPELL, CardType.TRAP):
                    for i, z in enumerate(self.psz):
                        if z.collidepoint(mx, my) and self.gs.player.field_spells[i] is None:
                            self.gs.player.field_spells[i] = card
                            self.gs.player.hand.remove(card)
                            if card.card_type == CardType.SPELL:
                                card.is_face_up = True
                                self.gs.log(f"Activated spell: {card.name}!")
                            else:
                                card.is_face_up = False
                                self.gs.log("Set a trap face-down.")
                            self.sel = None
                            break
            else:
                self.sel = None

        return None

    # ── draw ──────────────────────────────────────────────────────────────────
    def draw(self):
        self.screen.fill(BG)
        pygame.draw.line(self.screen, ZB, (170,0), (170,self.H), 1)

        can_summon = self.gs.can_normal_summon()

        # Zone labels
        self._label("Opponent monsters",     180, 63)
        self._label("Opponent spells/traps", 180, 80+120+8+62)
        self._label("Your spells/traps",     180, self.H-80-120-68-14)
        self._label("Your monsters",         180, self.H-80-120-14)

        # Opponent field
        for i, z in enumerate(self.omz):
            c = self.gs.opponent.field_monsters[i]
            self._slot(z, c, back=(c is not None))
        for i, z in enumerate(self.osz):
            c = self.gs.opponent.field_spells[i]
            self._slot(z, c, back=(c is not None), spell_trap=True)

        # Player field
        for i, z in enumerate(self.pmz):
            c = self.gs.player.field_monsters[i]
            if c and not c.is_face_up:
                self._slot(z, c, back=True)
            else:
                self._slot(z, c, greyed=(c is None and not can_summon))
        for i, z in enumerate(self.psz):
            c = self.gs.player.field_spells[i]
            if c and not c.is_face_up:
                self._slot(z, c, back=True, spell_trap=True)
            else:
                self._slot(z, c, spell_trap=True)

        # Life points
        self.screen.blit(self.fl.render(f"Your LP: {self.gs.player.lp:,}", True, GR),
                         (10, self.H-240))
        self.screen.blit(self.fl.render(
            f"{self.gs.opponent.name}: {self.gs.opponent.lp:,}", True, RE), (10, 20))

        # Phase + turn
        self.screen.blit(self.fm.render(self.gs.current_phase.value, True, GO), (10, self.H//2-10))
        self.screen.blit(self.fs.render(f"Turn {self.gs.turn_number}", True, TS), (10, self.H//2+20))

        # Summon indicator
        s_txt = "Summon available" if can_summon else "Summoned this turn"
        s_col = GR if can_summon else RE
        self.screen.blit(self.fxs.render(s_txt, True, s_col), (10, self.H//2+40))

        # Graveyard counts
        p_gy  = len(self.gs.player.graveyard)
        o_gy  = len(self.gs.opponent.graveyard)
        self.screen.blit(self.fxs.render(f"Your GY: {p_gy}", True, TS), (10, self.H//2+60))
        self.screen.blit(self.fxs.render(f"Opp GY:  {o_gy}", True, TS), (10, self.H//2+76))

        # Hand
        for i, (r, c) in enumerate(zip(self._hand_rects(), self.gs.player.hand)):
            is_st = c.card_type in (CardType.SPELL, CardType.TRAP)
            self._slot(r, c, hl=(i==self.sel), spell_trap=is_st)

        # Placement hint
        if self.sel is not None and self.sel < len(self.gs.player.hand):
            card = self.gs.player.hand[self.sel]
            hint = ("Click a monster zone — Summon/Set popup will appear"
                    if card.card_type == CardType.MONSTER
                    else "Click a spell/trap zone to place")
            self.screen.blit(self.fxs.render(hint, True, GO), (180, self.H-88))

        # Tooltip
        if self.tooltip:
            self._draw_tooltip(self.tooltip)

        # Summon popup
        if self.popup_card:
            self._draw_popup()

        # Context menu
        if self.ctx_card:
            self._draw_ctx()

        # Duel log
        pygame.draw.rect(self.screen, LB, self.log_area)
        self.screen.blit(self.fm.render("Duel Log", True, GO), (self.log_area.x+8, 8))
        vis = self.log_area.height//18-2
        for j, m in enumerate(self.gs.duel_log[-vis:]):
            self.screen.blit(self.fs.render(m[:44], True, TS),
                             (self.log_area.x+8, 34+j*18))

        # Nav buttons
        for btn, label in [(self.btn_adv,"Next Phase >"), (self.btn_menu,"< Menu")]:
            pygame.draw.rect(self.screen, (35,28,65), btn, border_radius=8)
            pygame.draw.rect(self.screen, ZB,          btn, width=1, border_radius=8)
            s = self.fm.render(label, True, TP)
            self.screen.blit(s, (btn.centerx-s.get_width()//2,
                                  btn.centery-s.get_height()//2))

    # ── sub-renderers ─────────────────────────────────────────────────────────
    def _draw_tooltip(self, card: Card):
        r = self.tooltip_rect
        pygame.draw.rect(self.screen, POPUP_BG, r, border_radius=8)
        pygame.draw.rect(self.screen, POPUP_BD, r, width=1, border_radius=8)
        tx, ty = r.x+6, r.y+6
        self.screen.blit(self.fm.render(card.name, True, TP),              (tx, ty)); ty += 20
        self.screen.blit(self.fxs.render(card.card_type.value, True, GO),  (tx, ty)); ty += 16
        if card.atk is not None:
            self.screen.blit(
                self.fxs.render(f"ATK {card.atk}  DEF {card.defense}", True, GR), (tx, ty))
            ty += 16
        if card.level:
            self.screen.blit(
                self.fxs.render(f"Level {card.level}  {card.race}", True, TS), (tx, ty))
            ty += 16
        words = card.description.split(); line, lines = [], []
        for w in words:
            line.append(w)
            if self.fxs.size(" ".join(line))[0] > r.width-12:
                lines.append(" ".join(line[:-1])); line = [w]
        if line: lines.append(" ".join(line))
        for l in lines[:5]:
            self.screen.blit(self.fxs.render(l, True, TS), (tx, ty)); ty += 14

    def _draw_popup(self):
        card = self.popup_card
        r    = self.popup_rect
        pygame.draw.rect(self.screen, POPUP_BG, r, border_radius=8)
        pygame.draw.rect(self.screen, POPUP_BD, r, width=1, border_radius=8)
        title = self.fs.render(f"Play {card.name[:16]}?", True, GO)
        self.screen.blit(title, (r.centerx-title.get_width()//2, r.y+8))
        self._button(self.btn_summon,  "Normal Summon (face-up ATK)", BTN_NRM, BTN_NRM_BD, GR)
        self._button(self.btn_set_mon, "Set (face-down DEF)",         BTN_SET, BTN_SET_BD, (180,140,220))
        cancel = self.fxs.render("Cancel", True, TS)
        self.screen.blit(cancel, (r.centerx-cancel.get_width()//2, self.btn_cancel.y))

    def _draw_ctx(self):
        mx, my = pygame.mouse.get_pos()
        r = self.ctx_rect
        pygame.draw.rect(self.screen, CTX_BG, r, border_radius=8)
        pygame.draw.rect(self.screen, CTX_BD, r, width=1, border_radius=8)
        # Card name header
        header = self.fxs.render(self.ctx_card.name[:24], True, GO)
        self.screen.blit(header, (r.x+6, r.y+2))
        # Menu items
        for label, fn, ir in self.ctx_items:
            hovered = ir.collidepoint(mx, my)
            if hovered:
                pygame.draw.rect(self.screen, CTX_HOVER, ir, border_radius=4)
            color = TP if hovered else TS
            s = self.fs.render(label, True, color)
            self.screen.blit(s, (ir.x+6, ir.centery-s.get_height()//2))