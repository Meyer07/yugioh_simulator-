import pygame
import sys
from ui.menu import MenuScreen
from ui.duel import DuelScreen
from core.game import GameState

SCREEN_WIDTH=1280
SCREEN_HEIGHT=720
FPS=60

TITLE="Yu-Gi-Oh! Anime Duel Simulator"


def main():
    pygame.init()
    pygame.display.set_caption(TITLE)
    screen=pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
    clock=pygame.time.Clock()



    #current app state
    current_screen="menu"
    game_state=None

    menu=MenuScreen(screen)
    duel=None

    while True:
        events=pygame.event.get()
        
        for event in events:
            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
            

        if current_screen=="menu":
            selected_series=menu.update(events)
            menu.draw()
            if selected_series:
                game_state = GameState(series=selected_series)
                duel = DuelScreen(screen, game_state)
                current_screen = "duel"
        elif current_screen=="duel":
            result=duel.update(events)
            duel.draw()
            if result == "menu":
                current_screen = "menu"
                menu = MenuScreen(screen)


        pygame.display.flip()
        clock.tick(FPS)

if __name__=="__main__":
    main()
