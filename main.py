import arcade
import math

#! ЛЕВО И ПРАВО НЕ РАБОТАЕТ

SPRITE_SCALING_PLAYER = .15
SPRITE_SCALING_LASER = 0.8
SPRITE_SCALING_ENEMY_MAIN = .3
SPRITE_SCALING_BULLET = .5

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Gouge pandemonium"

# СКОРОСТЬ ДВИЖЕНИЯ
MOVEMENT_SPEED = 3

# СКОРОСТЬ ПОВОРОТА
ANGLE_SPEED = 4

BOX_SIZE = .4

#СКОРОСТЬ ПУЛИ
BULLET_SPEED = 10



class Player(arcade.Sprite):

    def __init__(self, image, scale):
        super().__init__(image, scale)
        self.speed = 0


    def update(self):
        angle_rad = math.radians(self.angle)

        self.angle += self.change_angle

        self.center_x += -self.speed * math.sin(angle_rad)
        self.center_y += self.speed * math.cos(angle_rad)

        
    def rotate_around_point(self, point: arcade.Point, degrees: float):
        # Make the sprite turn as its position is moved
        self.angle += degrees
        # Move the sprite along a circle centered around the passed point
        self.position = arcade.rotate_point(
            self.center_x, self.center_y,
            point[0], point[1], degrees)


class GougeGame(arcade.Window):
    """ MAIN CLASS """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self._correct = True
        self.score = 0
        self.score_text = None

        self.mouse_pos = 0, 0
        # Переменные, в которых будут храниться списки спрайтов
        self.player_list = None
        self.player_sprite = None
        
        self.wall_list = None
        self.physics_engine = None

        self.bullet_list = None
        self.enemy_list = None

        arcade.set_background_color(arcade.color.AMAZON)



    def setup(self):
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.death_list = arcade.SpriteList()


        # ПОЛОЖЕНИЕ ИГРОКА
        self.player_sprite = Player("image/sas-main.png", SPRITE_SCALING_PLAYER)
        self.player_sprite.center_x = SCREEN_WIDTH / 2
        self.player_sprite.center_y = SCREEN_HEIGHT / 2
        self.player_list.append(self.player_sprite)
        self.score = 0
        self.death = Player("image/blood.png", scale=.8)
        

            
        # ПОЛОЖЕНИЕ ВРАГА
        self.enemy_sprite = Player("image/surv-main.png", SPRITE_SCALING_ENEMY_MAIN)
        self.enemy_sprite.center_x = 50
        self.enemy_sprite.center_y = 70
        self.enemy_list.append(self.enemy_sprite)

        # -- SETUP WALLS
        # CREATE ROW BOXES
        for x in range(173, 650, 64):
            wall = arcade.Sprite(":resources:images/tiles/boxCrate_double.png",
                                BOX_SIZE)
            wall.center_x = x
            wall.center_y = 200
            self.wall_list.append(wall)

        # CREATE COLUMN BOXES
        for y in range(273, 500, 64):
            wall = arcade.Sprite(":resources:images/tiles/boxCrate_double.png",
                                 BOX_SIZE)
            wall.center_x = 465
            wall.center_y = y
            self.wall_list.append(wall)

        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite,
                                                         self.wall_list)


    def on_draw(self):
        """ ОТРИСОВКА """
        self.clear()
        self.player_list.draw()
        self.wall_list.draw()
        self.bullet_list.draw()
        self.enemy_list.draw()
        self.death_list.draw()


        output = f"Score: {self.score}"
        arcade.draw_text(output, 10, 20, arcade.color.WHITE, 14)


        

    def on_update(self, delta_time: float):
        self.player_list.update()
        self.physics_engine.update()
        self.bullet_list.update()
        self.aim_player(delta_time)
        # Перебрать пули
        for bullet in self.bullet_list:

            # Проверем пулю, чтобы увидеть, попала ли она во врага
            hit_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)
            hit2_list = arcade.check_for_collision_with_list(bullet, self.wall_list)
            
            # Если это так, избавляемся от пули
            if len(hit_list) > 0 or len(hit2_list) > 0:
                bullet.remove_from_sprite_lists()


            # За каждого попадаемого врага прибавляем к счету и убираем врага
            for enemy in hit_list:
                enemy.remove_from_sprite_lists()
                self.death.center_y = enemy.center_y
                self.death.center_x = enemy.center_x

                self.death_list.append(self.death)

                self.score += 1

            # Если пуля вылетает за пределы экрана, убераем ее
            if bullet.bottom > self.width or bullet.top < 0 or bullet.right < 0 or bullet.left > self.width:
                bullet.remove_from_sprite_lists()



    def aim_player(self, delta_time):
        mouse_angle = arcade.get_angle_degrees(
            self.player_sprite.center_y, self.player_sprite.center_x,
            self.mouse_pos[1], self.mouse_pos[0]
        )

        mouse_angle += 90

        if self.correct:
            # Rotate the barrel sprite with one end at the tank's center
            # Subtract the old angle to get the change in angle
            angle_change = mouse_angle - self.player_sprite.angle
            self.player_sprite.rotate_around_point(self.player_sprite.position, angle_change)
        else:
            # Swivel the barrel with its center aligned with the body's 
            self.player_sprite.angle = mouse_angle




# --
# ..
    def on_mouse_press(self, x, y, button, modifiers):
        """ Called whenever the mouse button is clicked """

        # Создать пулю
        bullet = arcade.Sprite(":resources:images/space_shooter/laserBlue01.png", SPRITE_SCALING_BULLET)

        # Расположить пулю в текущем местоположении игрока
        start_x = self.player_sprite.center_x
        start_y = self.player_sprite.center_y
        bullet.center_x = start_x
        bullet.center_y = start_y

        # Получить от мыши место назначения для пули
        dest_x = x
        dest_y = y

        # Посчитать, как доставить пулю до места назначения
        # Расчет угла в радианах между начальными точками
        # и конечные точки. Это угол, под которым полетит пуля
        x_diff = dest_x - start_x
        y_diff = dest_y - start_y
        angle = math.atan2(y_diff, x_diff)

        # Наклонить спрайт пули так, чтобы не было похоже, что она летит боком
        bullet.angle = math.degrees(angle)
        print(f"Bullet angle: {bullet.angle:.2f}")

        # С учетом угла рассчитать изменение Х и изменить У 
        bullet.change_x = math.cos(angle) * BULLET_SPEED
        bullet.change_y = math.sin(angle) * BULLET_SPEED

        # Добавляем пулю в соответствующий список
        self.bullet_list.append(bullet)


    def on_key_press(self, symbol: int, modifiers: int):
        """ CALLED PRESSED USER KEYS"""

        # FORWARD/BACK
        if symbol == arcade.key.W:
            self.player_sprite.speed = -MOVEMENT_SPEED
        elif symbol == arcade.key.S:
            self.player_sprite.speed = MOVEMENT_SPEED

        # ROTATE LEFT/ RIGHT
        elif symbol == arcade.key.A:
            self.player_sprite.change_angle = ANGLE_SPEED
        elif symbol == arcade.key.D:
            self.player_sprite.change_angle = -ANGLE_SPEED
    

    def on_key_release(self, symbol: int, modifiers: int):
        """ CALLED WHEN USER DROP KEY"""
        if symbol == arcade.key.W or symbol == arcade.key.S:
            self.player_sprite.speed = 0
        elif symbol == arcade.key.A or symbol == arcade.key.D:
            self.player_sprite.change_angle = 0

        
    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        self.mouse_pos = x, y
        print(f"Mouse pos: {x}, {y}")

        
    @property
    def correct(self):
        return self._correct