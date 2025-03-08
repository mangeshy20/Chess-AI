import threading

from PygameUIKit.button import ButtonText, ButtonPngIcon
from PygameUIKit import Group

from ai import Bot, PlayerType
from board_ui import Board, get_x_y_w_h, pygame
from constants import *
from logic import Logic, PieceColor, State, Square, Move

img_flip_board = pygame.image.load("assets/flip.png")
img_flip_board = pygame.transform.scale(img_flip_board, (35, 35))

BG_COLOR = (22, 21, 18)

BTN_COLOR_NEWGAME = (114, 137, 218)
TEXT_BUTTON_COLOR = (191, 193, 197)

from pygame import Color


class Game:
    def __init__(self, win, fen):
        self.win = win
        self.logic = Logic(fen=fen)
        self.board = Board()
        self.board.update(self.logic)

        self.current_piece_legal_moves = []
        self.game_on = True
        self.window_on = True

        self.players = {PieceColor.WHITE: PlayerType.HUMAN,
                        PieceColor.BLACK: PlayerType.BOT}

        self.bot_is_thinking = False
        self.returnlist = [None]
        self.thread = None

        # Buttons
        font_btn = pygame.font.SysFont("None", 40)
        self.btn_new_game = ButtonText("New Game", self.new_game, BTN_COLOR_NEWGAME,
                                       font_color=Color("white"), border_radius=5, font=font_btn)
        self.btn_flip_board = ButtonPngIcon(img_flip_board, self.flip_board)
        self.btn_bot_playing = ButtonText("Your turn", lambda: 1, Color(38, 36, 33),
                                          font_color=Color("white"), border_radius=5, font=font_btn)
        self.easy_objects = Group(self.btn_new_game, self.btn_flip_board, self.btn_bot_playing)

    def run(self):
        clock = pygame.time.Clock()
        while self.window_on:
            clock.tick(60)
            self.events()
            self.bot_events()
            self.draw()

    def events(self):
        events = pygame.event.get()
        for event in events:
            self.easy_objects.handle_event(event)

            if event.type == pygame.QUIT:
                self.window_on = False
            if not self.game_on:
                continue
            turn = self.logic.turn
            if self.players[turn] == PlayerType.HUMAN:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = event.pos
                    if self.board.clicked(pos):
                        if self.logic.turn != self.logic.get_piece(Square(*self.board.clicked_piece_coord)).color:
                            continue
                        self.current_piece_legal_moves = self.logic.get_legal_moves_piece(
                            Square(*self.board.clicked_piece_coord))
                    else:
                        self.current_piece_legal_moves = []

                if self.board.dragging:
                    if event.type == pygame.MOUSEMOTION:
                        pos = pygame.mouse.get_pos()
                        self.board.drag(pos)

                    if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                        pos = event.pos
                        dest_coord = self.board.drop(pos)
                        move = Move(Square(*self.board.clicked_piece_coord), Square(*dest_coord))
                        if move in self.current_piece_legal_moves:
                            self.play(move)
                        self.current_piece_legal_moves = []

    def play(self, move):
        self.logic.real_move(move)
        self.board.update(self.logic)
        self.check_end()

    def bot_events(self):
        if not self.game_on:
            return
        turn = self.logic.turn
        if self.players[turn] == PlayerType.BOT:
            if not self.bot_is_thinking:
                self.bot_is_thinking = True
                # Start the thinking thread
                p = Bot()
                self.thread = threading.Thread(target=p.play, args=(self.logic, self.returnlist))
                self.thread.start()
            else:
                # Check if the move was found
                if self.returnlist[0]:
                    eval_and_move = self.returnlist[0]
                    self.bot_is_thinking = False
                    e, move = eval_and_move
                    print(f"Eval found : {e}")
                    self.play(move)
                    self.returnlist = [None]

    def check_end(self):
        if self.logic.state != State.GAMEON:
            self.game_on = False
            if self.logic.state == State.CHECKMATE:
                color = self.logic.turn
                self.btn_bot_playing.change_text(f"Checkmate, {color.value} wins!")
            elif self.logic.state == State.STALEMATE:
                self.btn_bot_playing.change_text("Stalemate!")
            elif self.logic.state == State.DRAW:
                self.btn_bot_playing.change_text("Draw!")

    def draw(self):
        x, y, w, h = get_x_y_w_h()
        self.win.fill(BG_COLOR)
        self.board.draw(self.win, self.current_piece_legal_moves, x, y, w, h)

        W, H = self.win.get_size()
        self.btn_new_game.draw(self.win, x // 2 - self.btn_new_game.rect.w // 2, H // 2 - self.btn_new_game.rect.h // 2)
        self.btn_flip_board.draw(self.win, x + w - self.btn_flip_board.rect.w, y + h + 10)

        if self.thread and self.thread.is_alive():
            self.btn_bot_playing.change_text("Bot is thinking...")
        else:
            self.btn_bot_playing.change_text("Your turn")
        self.btn_bot_playing.draw(self.win, x // 2 - self.btn_bot_playing.rect.w // 2,
                                  H // 2 - self.btn_bot_playing.rect.h // 2 - 200)

        pygame.display.flip()

    def new_game(self):
        self.bot_is_thinking = False
        self.logic = Logic(STARTINGPOSFEN)
        self.board.update(self.logic)
        self.game_on = True
        self.current_piece_legal_moves = []

    def select(self, pos):
        self.board.select(pos)

    def flip_board(self):
        self.board.flip_board()
