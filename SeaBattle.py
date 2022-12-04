from random import randint


# Класс исключения
class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Вы стреляете за границы доски!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Эта область уже обстреляна"


class BoardWrongShipException(BoardException):
    pass


# Класс точек
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"


# Класс кораблей
class Ship:
    # o - ориентация корабля (0 - вертикально, 1 - горизонтально)
    def __init__(self, bow, q, o):
        self.bow = bow
        self.q = q
        self.o = o
        self.lives = q

    # Точки корабля
    @property
    def dots(self):
        ship_dots = []
        for i in range(self.q):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))  # Список координат точек

        return ship_dots

    # Проверка попадания
    def shooten(self, shot):
        return shot in self.dots


# Игровая доска
class Board:
    def __init__(self, hid=False, size=6):
        # hid - параметр скрытия доски
        # size - размер доски
        self.size = size
        self.hid = hid

        self.count = 0  # Количество уничтоженных кораблей

        self.field = [["O"] * size for _ in range(size)]  # - Игровая сетка (size * size)с текущим состоянием игры

        self.busy = []  # Список координат обстрелянных точек и точек с кораблями
        self.ships = []  # Список координат кораблей на доске

    # Расположение корабля
    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    # Контур корабля
    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def __str__(self):


        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")
        return res

    # Проверка нахождения точки за пределами доски
    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "T"
        print("Промах!")
        return False

    # Очищаем список координат обстрелянных точек и точек с кораблями
    def begin(self):
        self.busy = []

    # Общее количество кораблей на доске
    def defeat(self):
        return self.count == len(self.ships)


# Класс игрока
class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                again = self.enemy.shot(target)
                return again
            except BoardException as e:
                print(e)


# Класс игрок-компьютер
class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


# Класс игрок-пользователь
class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


# Класс игры
class Game:
    def __init__(self, size=6):
        self.lens = [3, 2, 2, 1, 1, 1, 1]
        self.size = size
        pl = self.random_board()  # Создаем доску игрока
        co = self.random_board()  # Создаем доску компьютера
        co.hid = True             # Скрываем корабли компьютера

        self.ai = AI(co, pl)      # Создаем игрока-компьютер
        self.us = User(pl, co)    # Создаем игрока-игрок

    # Генерация случайного расположения кораблей
    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    # Расстановка кораблей
    def random_place(self):
        board = Board(size=self.size)
        attempts = 0  # Количество попыток расстановки кораблей
        for q in self.lens:
            while True:
                attempts += 1
                if attempts > 2000:  # Ограничение количества попыток
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), q, randint(0, 1))
                try:
                    board.add_ship(ship)  # Добавление корабля
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    # Приветствие в начале игры
    @staticmethod
    def greet():
        print(" "*20,"-"*20)
        print(" "*22,"Игра морской бой")
        print(" "*20,"-"*20)
        print(" Координаты выстрела: x y ")
        print(" x - номер строки    y - номер столбца ")
        print("")
        

    def print_boards(self):
        c = str(self.us.board).split('\n')
        b = str(self.ai.board).split('\n')
        bc = " Ваша доска:".ljust(len(c[1]), ' ')
        ba = " Доска компьютера:".ljust(len(c[1]), ' ')
        print(bc, ' ' * 5, ba)
        for c, b in zip(c, b):
            print(c, ' ' * 5, b)
        print("-" * 60)

       
    # Игровой цикл
    def loop(self):
        num = 0  # Количество ходов
        while True:
            self.print_boards()
            if num % 2 == 0:
                again = self.us.move()
            else:
                again = self.ai.move()
            if again:  # Проверка повтора хода, согласно правилам игры
                num -= 1

            if self.ai.board.defeat():  # Проверка равенства количества уничтоженных кораблей общему количеству кораблей
                print("Вы выиграли!")
                break

            if self.us.board.defeat():  # Проверка равенства количества уничтоженных кораблей общему количеству кораблей
                print("Компьютер выиграл!")
                break
            num += 1

    # Старт игры
    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
