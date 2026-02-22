# SPACE BOT ADVENTURE

# IMPORTS
import random

# CONFIG
WIDTH = 800
HEIGHT = 600
TILE = 32


# =========================
# GAME STATE
# =========================

game_state = "menu"
sound_on = True

music_started = False

score = 0
win = False


# =========================
# MAP / WALLS
# =========================

walls = []
WALL = 8


def build_maze():

    walls.clear()

    # Borders
    walls.append(Rect((0, 0), (WIDTH, WALL)))
    walls.append(Rect((0, HEIGHT - WALL), (WIDTH, WALL)))
    walls.append(Rect((0, 0), (WALL, HEIGHT)))
    walls.append(Rect((WIDTH - WALL, 0), (WALL, HEIGHT)))

    def h(col, row, length):
        walls.append(
            Rect((col * TILE, row * TILE), (length * TILE, WALL))
        )

    def v(col, row, length):
        walls.append(
            Rect((col * TILE, row * TILE), (WALL, length * TILE))
        )

    for r in range(3, 17, 4):
        for c in range(2, 22, 4):
            h(c, r, 3)

    for c in range(4, 22, 4):
        for r in range(5, 16, 4):
            v(c, r, 3)


build_maze()


# =========================
# PELLETS
# =========================

pellets = []


def create_pellets():

    pellets.clear()

    for x in range(64, WIDTH - 64, 64):
        for y in range(64, HEIGHT - 64, 64):

            test = Rect(x - 5, y - 5, 10, 10)

            blocked = False

            for w in walls:
                if test.colliderect(w):
                    blocked = True
                    break

            if not blocked:
                pellets.append(test)


create_pellets()


# =========================
# CLASSES
# =========================


class Player:

    def __init__(self, pos):

        self.frames = {

            "idle": [
                "player",
                "player_idle1",
                "player_idle2",
            ],

            "down": [
                "player",
                "player_idle2",
            ],

            "up": [
                "playerb",
                "playerb1",
            ],

            "left": [
                "playerl1",
                "playerl2",
            ],

            "right": [
                "playerr1",
                "playerr2",
            ],
        }

        self.direction = "idle"
        self.frame = 0
        self.timer = 0

        self.speed = 4

        self.actor = Actor(self.frames["idle"][0])
        self.actor.pos = pos

        # Hitbox menor
        self.hitbox = Rect(0, 0, 24, 24)
        self.update_hitbox()


    def update_hitbox(self):
        self.hitbox.center = self.actor.pos


    def draw(self):
        self.actor.draw()


    def animate(self):

        self.timer += 1

        if self.timer >= 10:

            self.timer = 0
            self.frame += 1

            if self.frame >= len(self.frames[self.direction]):
                self.frame = 0

            self.actor.image = self.frames[self.direction][self.frame]


    def move(self):

        moving = False


        # ---------- X ----------

        old_x = self.actor.x

        if keyboard.left:
            self.actor.x -= self.speed
            self.direction = "left"
            moving = True

        elif keyboard.right:
            self.actor.x += self.speed
            self.direction = "right"
            moving = True

        self.update_hitbox()

        for w in walls:
            if self.hitbox.colliderect(w):
                self.actor.x = old_x
                self.update_hitbox()


        # ---------- Y ----------

        old_y = self.actor.y

        if keyboard.up:
            self.actor.y -= self.speed
            self.direction = "up"
            moving = True

        elif keyboard.down:
            self.actor.y += self.speed
            self.direction = "down"
            moving = True

        self.update_hitbox()

        for w in walls:
            if self.hitbox.colliderect(w):
                self.actor.y = old_y
                self.update_hitbox()


        if not moving:
            self.direction = "idle"

        self.animate()

class PatrolEnemy:

    def __init__(self, pos, axis):

        self.frames = [
            "enemy",
            "enemy_idle",
            "enemy_idle2"
        ]

        self.frame = 0
        self.timer = 0

        self.actor = Actor(self.frames[0])
        self.actor.pos = pos

        self.speed = 2
        self.axis = axis

        self.min_x = 2 * TILE
        self.max_x = 22 * TILE

        self.min_y = 2 * TILE
        self.max_y = 15 * TILE


    def animate(self):

        self.timer += 1

        if self.timer >= 12:
            self.timer = 0
            self.frame += 1

            if self.frame >= len(self.frames):
                self.frame = 0

            self.actor.image = self.frames[self.frame]


    def draw(self):
        self.actor.draw()


    def update(self):

        # movimento
        if self.axis == "x":

            self.actor.x += self.speed

            if self.actor.x < self.min_x or self.actor.x > self.max_x:
                self.speed *= -1


        elif self.axis == "y":

            self.actor.y += self.speed

            if self.actor.y < self.min_y or self.actor.y > self.max_y:
                self.speed *= -1


        # animação
        self.animate()


class ChaserEnemy:

    def __init__(self, pos):

        self.frames = [
            "enemy2",
            "enemy2_idle",
        ]

        self.frame = 0
        self.timer = 0

        self.actor = Actor(self.frames[0])
        self.actor.pos = pos

        self.speed = 2

        # Anti-travamento
        self.last_pos = self.actor.pos
        self.stuck_timer = 0


    def draw(self):
        self.actor.draw()


    def animate(self):

        self.timer += 1

        if self.timer >= 15:

            self.timer = 0
            self.frame += 1

            if self.frame >= len(self.frames):
                self.frame = 0

            self.actor.image = self.frames[self.frame]


    def can_move(self, dx, dy):

        test = Rect(
            self.actor.left + dx,
            self.actor.top + dy,
            self.actor.width,
            self.actor.height,
        )

        for w in walls:
            if test.colliderect(w):
                return False

        return True


    def update(self, target):

        self.animate()


        # ----------------------------
        # Detectar se está travado
        # ----------------------------

        if self.actor.pos == self.last_pos:
            self.stuck_timer += 1
        else:
            self.stuck_timer = 0

        self.last_pos = self.actor.pos


        # ----------------------------
        # Movimentos possíveis
        # ----------------------------

        moves = []

        if self.can_move(self.speed, 0):
            moves.append((self.speed, 0))

        if self.can_move(-self.speed, 0):
            moves.append((-self.speed, 0))

        if self.can_move(0, self.speed):
            moves.append((0, self.speed))

        if self.can_move(0, -self.speed):
            moves.append((0, -self.speed))


        if not moves:
            return


        # ----------------------------
        # Se estiver travado → movimento aleatório
        # ----------------------------

        if self.stuck_timer > 20:

            dx, dy = random.choice(moves)

            self.actor.x += dx
            self.actor.y += dy

            self.stuck_timer = 0
            return


        # ----------------------------
        # Movimento normal (perseguir)
        # ----------------------------

        best = None
        best_dist = 999999


        for dx, dy in moves:

            nx = self.actor.x + dx
            ny = self.actor.y + dy

            dist = abs(nx - target.x) + abs(ny - target.y)

            if dist < best_dist:
                best_dist = dist
                best = (dx, dy)


        if best:
            self.actor.x += best[0]
            self.actor.y += best[1]


# =========================
# OBJECTS
# =========================

OFFSET = TILE // 2

player = Player((2 * TILE + OFFSET, 2 * TILE + OFFSET))

enemy_h = PatrolEnemy(
    (2 * TILE + OFFSET, 4 * TILE + OFFSET),
    "x",
)

enemy_v = PatrolEnemy(
    (23 * TILE + OFFSET, 3 * TILE + OFFSET),
    "y",
)

chaser = ChaserEnemy(
    (21*TILE + OFFSET, 15*TILE + OFFSET)
)


# =========================
# MENU BUTTONS
# =========================

btn_start = Rect((300, 220), (200, 50))
btn_sound = Rect((300, 300), (200, 50))
btn_exit = Rect((300, 380), (200, 50))


# =========================
# MOUSE
# =========================


def on_mouse_down(pos):

    global game_state, sound_on

    if game_state != "menu":
        return


    if btn_start.collidepoint(pos):

        game_state = "playing"


    elif btn_sound.collidepoint(pos):

        sound_on = not sound_on


    elif btn_exit.collidepoint(pos):

        exit()


# =========================
# DRAW
# =========================

def draw_text_outline(text, center, size, color):

    x, y = center

    # sombra / contorno
    screen.draw.text(text, center=(x-2, y-2), fontsize=size, color="black")
    screen.draw.text(text, center=(x+2, y-2), fontsize=size, color="black")
    screen.draw.text(text, center=(x-2, y+2), fontsize=size, color="black")
    screen.draw.text(text, center=(x+2, y+2), fontsize=size, color="black")

    # texto principal
    screen.draw.text(text, center=center, fontsize=size, color=color)

def draw():

    screen.clear()


    # ---------- MENU ----------

    if game_state == "menu":

        screen.draw.text(
            "SPACE BOT ADVENTURE",
            center=(400, 120),
            fontsize=50,
            color="yellow",
        )

        screen.draw.filled_rect(btn_start, "darkblue")
        screen.draw.filled_rect(btn_sound, "darkblue")
        screen.draw.filled_rect(btn_exit, "darkblue")

        screen.draw.text("START", center=btn_start.center, fontsize=30)

        screen.draw.text(
            "SOUND: ON" if sound_on else "SOUND: OFF",
            center=btn_sound.center,
            fontsize=25,
        )

        screen.draw.text("EXIT", center=btn_exit.center, fontsize=30)

        return


    # ---------- GAME ----------

    for w in walls:
        screen.draw.filled_rect(w, "gray")

    for p in pellets:
        screen.draw.filled_circle(p.center, 4, "yellow")

    draw_text_outline(f"Score: {score}", (80, 25), 25, "white")

    player.draw()
    enemy_h.draw()
    enemy_v.draw()
    chaser.draw()


    if game_state == "gameover":

        box = Rect((200, 200), (400, 200))
        screen.draw.filled_rect(box, (20, 20, 20))
        screen.draw.rect(box, "red")

        draw_text_outline("GAME OVER", (400, 240), 60, "red")
        draw_text_outline("Press R to Restart", (400, 290), 25, "white")
        draw_text_outline("Press M for Menu", (400, 320), 25, "white")


    if game_state == "win":

        box = Rect((200, 200), (400, 220))
        screen.draw.filled_rect(box, (20, 20, 20))
        screen.draw.rect(box, "yellow")

        draw_text_outline("YOU WIN!", (400, 240), 60, "yellow")
        draw_text_outline(f"Final Score: {score}", (400, 290), 30, "white")
        draw_text_outline("Press R to Restart", (400, 320), 25, "white")
        draw_text_outline("Press M for Menu", (400, 350), 25, "white")

# =========================
# RESET
# =========================


def restart_game():

    global game_state, score, win, music_started

    music_started = False

    score = 0
    win = False

    create_pellets()

    player.actor.pos = (2 * TILE + OFFSET, 2 * TILE + OFFSET)
    enemy_h.actor.pos = (2 * TILE + OFFSET, 4 * TILE + OFFSET)
    enemy_v.actor.pos = (23 * TILE + OFFSET, 3 * TILE + OFFSET)
    chaser.actor.pos = (21 * TILE + OFFSET, 15 * TILE + OFFSET)

    game_state = "playing"

    enemy_h.frame = 0
    enemy_h.timer = 0

    enemy_v.frame = 0
    enemy_v.timer = 0

    chaser.frame = 0
    chaser.timer = 0
    chaser.stuck_timer = 0


# =========================
# UPDATE
# =========================


def update():

    global score, win, game_state, music_started

    # -------- MUSIC CONTROL --------

    if game_state == "playing" and sound_on:

        if not music_started:
            music.set_volume(0.4)
            music.play("bg")
            music_started = True

    else:
        music.stop()
        music_started = False

    # -------- END --------

    if game_state in ("gameover", "win"):

        if keyboard.r:
            restart_game()

        if keyboard.m:
            game_state = "menu"

        return


    if game_state != "playing":
        return


    # -------- PLAYER --------

    player.move()


    # -------- ENEMIES --------

    enemy_h.update()
    enemy_v.update()
    chaser.update(player.actor)


    # -------- SCORE --------

    for p in pellets[:]:

        if player.actor.colliderect(p):

            pellets.remove(p)
            score += 10

            if sound_on:
                sounds.coin.play()


    # -------- WIN --------

    if len(pellets) == 0:

        win = True
        game_state = "win"
        return


    # -------- LOSE --------

    if (
        player.actor.colliderect(enemy_h.actor)
        or player.actor.colliderect(enemy_v.actor)
        or player.actor.colliderect(chaser.actor)
    ):

        game_state = "gameover"