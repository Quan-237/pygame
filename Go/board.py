"""围棋棋盘逻辑：落子、提子、打劫、虚手与数目"""

from collections import namedtuple

Point = namedtuple('Point', 'X Y')

EMPTY = 0
BLACK = 1
WHITE = 2

DIRECTIONS = ((0, 1), (0, -1), (1, 0), (-1, 0))


def opponent(color):
    return WHITE if color == BLACK else BLACK


class GoBoard:
    def __init__(self, size=19):
        self.size = size
        self.grid = [[EMPTY] * size for _ in range(size)]
        self.current = BLACK
        self.ko_point = None
        self.captures = {BLACK: 0, WHITE: 0}
        self.pass_count = 0
        self.last_move = None
        self.history = []

    def in_bounds(self, x, y):
        return 0 <= x < self.size and 0 <= y < self.size

    def stone_at(self, point):
        return self.grid[point.Y][point.X]

    def can_play(self, point):
        if self.pass_count >= 2:
            return False
        if not self.in_bounds(point.X, point.Y):
            return False
        if self.grid[point.Y][point.X] != EMPTY:
            return False
        if self.ko_point == (point.X, point.Y):
            return False
        return self._is_legal_move(point.X, point.Y, self.current)

    def play(self, point):
        """落子，成功返回 True"""
        if not self.can_play(point):
            return False

        color = self.current
        x, y = point.X, point.Y
        self.grid[y][x] = color

        # 提掉无气的对方棋子
        captured_positions = []
        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            if not self.in_bounds(nx, ny):
                continue
            if self.grid[ny][nx] == opponent(color):
                group, liberties = self._get_group(nx, ny)
                if len(liberties) == 0:
                    for gx, gy in group:
                        self.grid[gy][gx] = EMPTY
                        captured_positions.append((gx, gy))

        # 自杀手：落子后己方无气且未提子，则非法
        _, my_liberties = self._get_group(x, y)
        if len(my_liberties) == 0 and not captured_positions:
            self.grid[y][x] = EMPTY
            return False

        # 打劫：仅提一子且己方新子仅一气时，禁止对方立即回提
        self.ko_point = None
        if len(captured_positions) == 1:
            _, liberties_after = self._get_group(x, y)
            if len(liberties_after) == 1:
                self.ko_point = captured_positions[0]

        self.captures[color] += len(captured_positions)
        self.current = opponent(color)
        self.pass_count = 0
        self.last_move = point
        self.history.append(self._board_hash())
        return True

    def pass_turn(self):
        """虚手；双方连续虚手则终局"""
        if self.pass_count >= 2:
            return
        self.ko_point = None
        self.pass_count += 1
        self.last_move = None
        self.current = opponent(self.current)
        self.history.append(self._board_hash())

    def is_game_over(self):
        return self.pass_count >= 2

    def score(self):
        """中国规则数目：子空加俘虏，白棋贴 7.5 目"""
        territory = {BLACK: 0, WHITE: 0}
        visited = set()

        for y in range(self.size):
            for x in range(self.size):
                if self.grid[y][x] != EMPTY:
                    continue
                if (x, y) in visited:
                    continue
                region, borders = self._empty_region(x, y)
                visited.update(region)
                owners = {self.grid[by][bx] for bx, by in borders if self.grid[by][bx] != EMPTY}
                if owners == {BLACK}:
                    territory[BLACK] += len(region)
                elif owners == {WHITE}:
                    territory[WHITE] += len(region)

        stones = {BLACK: 0, WHITE: 0}
        for row in self.grid:
            for cell in row:
                if cell != EMPTY:
                    stones[cell] += 1

        black_score = stones[BLACK] + territory[BLACK] + self.captures[BLACK]
        white_score = stones[WHITE] + territory[WHITE] + self.captures[WHITE] + 7.5
        return black_score, white_score

    def reset(self):
        self.__init__(self.size)

    def _is_legal_move(self, x, y, color):
        removed = []
        self.grid[y][x] = color
        captured = False
        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            if self.in_bounds(nx, ny) and self.grid[ny][nx] == opponent(color):
                group, liberties = self._get_group(nx, ny)
                if len(liberties) == 0:
                    captured = True
                    for gx, gy in group:
                        removed.append((gx, gy, opponent(color)))
                        self.grid[gy][gx] = EMPTY

        _, liberties = self._get_group(x, y)
        legal = captured or len(liberties) > 0

        # 还原试下的棋盘状态
        self.grid[y][x] = EMPTY
        for gx, gy, stone_color in removed:
            self.grid[gy][gx] = stone_color
        return legal

    def _get_group(self, x, y):
        color = self.grid[y][x]
        stack = [(x, y)]
        group = set()
        liberties = set()

        while stack:
            cx, cy = stack.pop()
            if (cx, cy) in group:
                continue
            if not self.in_bounds(cx, cy) or self.grid[cy][cx] != color:
                continue
            group.add((cx, cy))
            for dx, dy in DIRECTIONS:
                nx, ny = cx + dx, cy + dy
                if not self.in_bounds(nx, ny):
                    continue
                if self.grid[ny][nx] == EMPTY:
                    liberties.add((nx, ny))
                elif self.grid[ny][nx] == color:
                    stack.append((nx, ny))

        return group, liberties

    def _empty_region(self, x, y):
        stack = [(x, y)]
        region = set()
        borders = set()

        while stack:
            cx, cy = stack.pop()
            if (cx, cy) in region:
                continue
            if not self.in_bounds(cx, cy) or self.grid[cy][cx] != EMPTY:
                continue
            region.add((cx, cy))
            for dx, dy in DIRECTIONS:
                nx, ny = cx + dx, cy + dy
                if not self.in_bounds(nx, ny):
                    continue
                if self.grid[ny][nx] == EMPTY:
                    stack.append((nx, ny))
                else:
                    borders.add((nx, ny))

        return region, borders

    def _board_hash(self):
        return tuple(tuple(row) for row in self.grid)
