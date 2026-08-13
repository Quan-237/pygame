"""围棋双人对战"""

import sys
import pygame
import pygame.gfxdraw
from pygame.locals import *
from board import GoBoard, Point, BLACK, WHITE, EMPTY

# 棋盘与界面尺寸
SIZE = 30
LINE_POINTS = 19
OUTER_WIDTH = 20
BORDER_WIDTH = 4
INSIDE_WIDTH = 4
BORDER_LENGTH = SIZE * (LINE_POINTS - 1) + INSIDE_WIDTH * 2 + BORDER_WIDTH
START_X = START_Y = OUTER_WIDTH + BORDER_WIDTH // 2 + INSIDE_WIDTH
BOARD_SIZE = SIZE * (LINE_POINTS - 1) + OUTER_WIDTH * 2 + BORDER_WIDTH + INSIDE_WIDTH * 2
INFO_WIDTH = 220
SCREEN_WIDTH = BOARD_SIZE + INFO_WIDTH
SCREEN_HEIGHT = BOARD_SIZE

STONE_RADIUS = SIZE // 2 - 3
BOARD_COLOR = (0xE3, 0x92, 0x65)
BLACK_COLOR = (45, 45, 45)
WHITE_COLOR = (235, 235, 235)
TEXT_COLOR = (30, 30, 30)
ACCENT_COLOR = (30, 90, 170)
MARK_COLOR = (220, 40, 40)

INFO_X = BOARD_SIZE + 16


def print_text(screen, font, x, y, text, color=TEXT_COLOR):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


def stone_name(color):
    return '黑棋' if color == BLACK else '白棋'


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('围棋')

    font = pygame.font.SysFont('SimHei', 24)
    title_font = pygame.font.SysFont('SimHei', 32)
    result_font = pygame.font.SysFont('SimHei', 48)

    board = GoBoard(LINE_POINTS)
    message = ''

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_RETURN:
                    board.reset()
                    message = ''
                elif event.key == K_p:
                    if not board.is_game_over():
                        board.pass_turn()
                        if board.is_game_over():
                            black_score, white_score = board.score()
                            if black_score > white_score:
                                message = f'黑胜 {black_score:.1f} : {white_score:.1f}'
                            elif white_score > black_score:
                                message = f'白胜 {white_score:.1f} : {black_score:.1f}'
                            else:
                                message = f'和棋 {black_score:.1f} : {white_score:.1f}'
            elif event.type == MOUSEBUTTONDOWN and not board.is_game_over():
                if pygame.mouse.get_pressed()[0]:
                    click_point = get_click_point(pygame.mouse.get_pos())
                    if click_point and board.play(click_point):
                        message = ''

        draw_board(screen)
        draw_stones(screen, board)
        draw_last_move(screen, board)
        draw_info(screen, font, title_font, board, message)

        if message:
            text = result_font.render(message, True, MARK_COLOR)
            rect = text.get_rect(center=(BOARD_SIZE // 2, BOARD_SIZE // 2))
            screen.blit(text, rect)

        pygame.display.flip()


def draw_board(screen):
    screen.fill(BOARD_COLOR)
    pygame.draw.rect(
        screen, (0, 0, 0),
        (OUTER_WIDTH, OUTER_WIDTH, BORDER_LENGTH, BORDER_LENGTH),
        BORDER_WIDTH
    )

    for i in range(LINE_POINTS):
        pygame.draw.line(
            screen, (0, 0, 0),
            (START_X, START_Y + SIZE * i),
            (START_X + SIZE * (LINE_POINTS - 1), START_Y + SIZE * i),
            1
        )
        pygame.draw.line(
            screen, (0, 0, 0),
            (START_X + SIZE * i, START_Y),
            (START_X + SIZE * i, START_Y + SIZE * (LINE_POINTS - 1)),
            1
        )

    # 星位与天元
    for i in (3, 9, 15):
        for j in (3, 9, 15):
            radius = 5 if i == j == 9 else 3
            cx = START_X + SIZE * i
            cy = START_Y + SIZE * j
            pygame.gfxdraw.filled_circle(screen, cx, cy, radius, (0, 0, 0))


def draw_stones(screen, board):
    for y in range(board.size):
        for x in range(board.size):
            color = board.grid[y][x]
            if color == BLACK:
                draw_stone(screen, Point(x, y), BLACK_COLOR)
            elif color == WHITE:
                draw_stone(screen, Point(x, y), WHITE_COLOR)


def draw_stone(screen, point, color):
    cx = START_X + SIZE * point.X
    cy = START_Y + SIZE * point.Y
    pygame.gfxdraw.filled_circle(screen, cx, cy, STONE_RADIUS, color)
    pygame.gfxdraw.aacircle(screen, cx, cy, STONE_RADIUS, color)


def draw_last_move(screen, board):
    if board.last_move is None:
        return
    cx = START_X + SIZE * board.last_move.X
    cy = START_Y + SIZE * board.last_move.Y
    pygame.gfxdraw.aacircle(screen, cx, cy, 4, MARK_COLOR)


def draw_info(screen, font, title_font, board, message):
    print_text(screen, title_font, INFO_X, 24, '围棋', ACCENT_COLOR)
    print_text(screen, font, INFO_X, 80, '当前回合', ACCENT_COLOR)

    stone_y = 118
    stone_color = BLACK_COLOR if board.current == BLACK else WHITE_COLOR
    draw_stone_at(screen, INFO_X + 8, stone_y, stone_color)
    print_text(screen, font, INFO_X + 48, stone_y - 10, stone_name(board.current))

    print_text(screen, font, INFO_X, 170, '提子', ACCENT_COLOR)
    print_text(screen, font, INFO_X, 205, f'黑提: {board.captures[BLACK]}')
    print_text(screen, font, INFO_X, 235, f'白提: {board.captures[WHITE]}')

    print_text(screen, font, INFO_X, 290, '操作说明', ACCENT_COLOR)
    tips = [
        '左键: 落子',
        'P键: 虚手',
        '回车: 重新开始',
        '双方连续虚手后数目',
    ]
    for index, tip in enumerate(tips):
        print_text(screen, font, INFO_X, 325 + index * 30, tip)

    if board.is_game_over():
        print_text(screen, font, INFO_X, 470, '对局结束', MARK_COLOR)
        print_text(screen, font, INFO_X, 500, '按回车重开', MARK_COLOR)
    elif message:
        print_text(screen, font, INFO_X, 470, message, MARK_COLOR)


def draw_stone_at(screen, x, y, color):
    pygame.gfxdraw.filled_circle(screen, x, y, STONE_RADIUS, color)
    pygame.gfxdraw.aacircle(screen, x, y, STONE_RADIUS, color)


def get_click_point(mouse_pos):
    pos_x = mouse_pos[0] - START_X
    pos_y = mouse_pos[1] - START_Y
    if pos_x < -INSIDE_WIDTH or pos_y < -INSIDE_WIDTH:
        return None
    if mouse_pos[0] >= BOARD_SIZE:
        return None

    x = pos_x // SIZE
    y = pos_y // SIZE
    if pos_x % SIZE > STONE_RADIUS:
        x += 1
    if pos_y % SIZE > STONE_RADIUS:
        y += 1
    if x >= LINE_POINTS or y >= LINE_POINTS:
        return None
    return Point(x, y)


if __name__ == '__main__':
    main()
