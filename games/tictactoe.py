import arcade
import random

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Arcade Space Invaders"

SPRITE_SCALING_PLAYER = 0.5
SPRITE_SCALING_ENEMY = 0.5
SPRITE_SCALING_LASER = 0.8

PLAYER_MOVEMENT_SPEED = 5
BULLET_SPEED = 5

ENEMY_ROWS = 5
ENEMY_COLS = 11
ENEMY_X_SPACING = 60
ENEMY_Y_SPACING = 48
ENEMY_START_X = 60
ENEMY_START_Y = 500
ENEMY_BASE_SPEED = 1
ENEMY_SPEED_INCREMENT = 0.2
ENEMY_FIRE_CHANCE = 100

class GameView(arcade.View):
    """ Main game view """
    def __init__(self):
        super().__init__()
        
        # Sprite lists
        self.player_list = None
        self.enemy_list = None
        self.player_bullet_list = None
        self.enemy_bullet_list = None
        self.shield_list = None

        # Player info
        self.player_sprite = None
        self.score = 0
        self.lives = 3

        # Enemy info
        self.enemy_change_x = ENEMY_BASE_SPEED
        self.total_enemies = 0

        # Sounds
        self.player_shoot_sound = arcade.load_sound(":resources:sounds/laser2.wav")
        self.enemy_hit_sound = arcade.load_sound(":resources:sounds/hit2.wav")
        self.player_death_sound = arcade.load_sound(":resources:sounds/explosion2.wav")
        self.enemy_move_sound_1 = arcade.load_sound(":resources:sounds/jump1.wav")
        self.enemy_move_sound_2 = arcade.load_sound(":resources:sounds/jump2.wav")
        self.move_sound_timer = 0.5
        self.current_move_sound = 1

    def setup(self):
        """ Set up the game variables. """
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.player_bullet_list = arcade.SpriteList()
        self.enemy_bullet_list = arcade.SpriteList()
        self.shield_list = arcade.SpriteList(is_static=True)

        self.score = 0

        # Set up the player
        player_image_source = ":resources:images/space_shooter/playerShip1_blue.png"
        self.player_sprite = arcade.Sprite(player_image_source, SPRITE_SCALING_PLAYER)
        self.player_sprite.center_x = SCREEN_WIDTH / 2
        self.player_sprite.bottom = 32
        self.player_list.append(self.player_sprite)

        self.create_invaders()
        self.total_enemies = len(self.enemy_list)

        # Create shields
        for x in range(100, 701, 200):
            self.make_shield(x)

    def create_invaders(self):
        enemy_image_source = ":resources:images/enemies/alienGreen.png"
        for row in range(ENEMY_ROWS):
            for col in range(ENEMY_COLS):
                x = ENEMY_START_X + col * ENEMY_X_SPACING
                y = ENEMY_START_Y - row * ENEMY_Y_SPACING
                enemy = arcade.Sprite(enemy_image_source, SPRITE_SCALING_ENEMY)
                enemy.position = x, y
                self.enemy_list.append(enemy)

    def make_shield(self, x_start):
        shield_block_width = 5
        shield_block_height = 10
        shield_width_count = 20
        shield_height_count = 5
        y_start = 150
        for row in range(shield_height_count):
            for col in range(shield_width_count):
                if row < 2 and 6 < col < 14:
                    continue
                x = x_start + col * shield_block_width
                y = y_start + row * shield_block_height
                shield_block = arcade.SpriteSolidColor(shield_block_width, shield_block_height, arcade.color.LASER_GREEN)
                shield_block.position = x, y
                self.shield_list.append(shield_block)
    
    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)
        self.setup()

    def on_draw(self):
        self.clear()
        self.enemy_list.draw()
        self.player_bullet_list.draw()
        self.enemy_bullet_list.draw()
        self.shield_list.draw()
        self.player_list.draw()

        arcade.draw_text(f"Score: {self.score}", 10, 10, arcade.color.WHITE, 14)
        arcade.draw_text(f"Lives: {self.lives}", SCREEN_WIDTH - 80, 10, arcade.color.WHITE, 14)

    def on_update(self, delta_time):
        self.player_list.update()
        self.player_bullet_list.update()
        self.enemy_bullet_list.update()

        # --- Enemy Movement and Logic ---
        enemies_destroyed = self.total_enemies - len(self.enemy_list)
        current_speed = ENEMY_BASE_SPEED + enemies_destroyed * ENEMY_SPEED_INCREMENT
        
        if self.enemy_change_x > 0: self.enemy_change_x = current_speed
        else: self.enemy_change_x = -current_speed

        at_edge = False
        for enemy in self.enemy_list:
            enemy.center_x += self.enemy_change_x
            if (enemy.right > SCREEN_WIDTH and self.enemy_change_x > 0) or \
               (enemy.left < 0 and self.enemy_change_x < 0):
                at_edge = True
        
        if at_edge:
            self.enemy_change_x *= -1
            for enemy in self.enemy_list:
                enemy.center_y -= ENEMY_Y_SPACING / 2

        # --- Sound Timer ---
        self.move_sound_timer -= delta_time
        if self.move_sound_timer <= 0 and len(self.enemy_list) > 0:
            self.move_sound_timer = (len(self.enemy_list) / self.total_enemies) * 0.9 + 0.1
            if self.current_move_sound == 1:
                arcade.play_sound(self.enemy_move_sound_1)
                self.current_move_sound = 2
            else:
                arcade.play_sound(self.enemy_move_sound_2)
                self.current_move_sound = 1

        # --- Enemy Firing ---
        if len(self.enemy_list) > 0 and random.randrange(ENEMY_FIRE_CHANCE) == 0:
            x_positions = sorted(list(set(enemy.center_x for enemy in self.enemy_list)))
            fire_column_x = random.choice(x_positions)
            lowest_enemy = min((enemy for enemy in self.enemy_list if enemy.center_x == fire_column_x), key=lambda e: e.center_y, default=None)
            if lowest_enemy:
                bullet = arcade.Sprite(":resources:images/space_shooter/laserRed01.png", SPRITE_SCALING_LASER)
                bullet.center_x = lowest_enemy.center_x
                bullet.top = lowest_enemy.bottom
                bullet.change_y = -BULLET_SPEED
                self.enemy_bullet_list.append(bullet)

        # --- Collision Detection ---
        # Player bullets
        for bullet in self.player_bullet_list:
            hit_enemies = arcade.check_for_collision_with_list(bullet, self.enemy_list)
            hit_shields = arcade.check_for_collision_with_list(bullet, self.shield_list)
            if hit_enemies:
                bullet.remove_from_sprite_lists()
                for enemy in hit_enemies:
                    enemy.remove_from_sprite_lists()
                    self.score += 10
                    arcade.play_sound(self.enemy_hit_sound)
            elif hit_shields:
                bullet.remove_from_sprite_lists()
                for shield in hit_shields:
                    shield.remove_from_sprite_lists()
            if bullet.bottom > SCREEN_HEIGHT:
                bullet.remove_from_sprite_lists()

        # Enemy bullets
        for bullet in self.enemy_bullet_list:
            hit_shields = arcade.check_for_collision_with_list(bullet, self.shield_list)
            if hit_shields:
                bullet.remove_from_sprite_lists()
                for shield in hit_shields:
                    shield.remove_from_sprite_lists()
            if bullet.top < 0:
                bullet.remove_from_sprite_lists()

        # Player collision
        if arcade.check_for_collision_with_list(self.player_sprite, self.enemy_bullet_list):
            self.lives -= 1
            arcade.play_sound(self.player_death_sound)
            if self.lives <= 0:
                self.window.show_view(GameOverView(self.score))
            else:
                # Remove all bullets and reset player
                self.enemy_bullet_list = arcade.SpriteList()
                self.player_sprite.center_x = SCREEN_WIDTH / 2
        
        # --- Game Over Conditions ---
        if len(self.enemy_list) == 0:
            # Next wave
            self.create_invaders()
            self.total_enemies = len(self.enemy_list)

        for enemy in self.enemy_list:
            if enemy.bottom <= 120: # Shield height
                self.window.show_view(GameOverView(self.score))
                break

    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.SPACE:
            if len(self.player_bullet_list) == 0:
                bullet = arcade.Sprite(":resources:images/space_shooter/laserBlue01.png", SPRITE_SCALING_LASER)
                bullet.center_x = self.player_sprite.center_x
                bullet.bottom = self.player_sprite.top
                bullet.change_y = BULLET_SPEED
                self.player_bullet_list.append(bullet)
                arcade.play_sound(self.player_shoot_sound)

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT or key == arcade.key.A or key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = 0

class GameOverView(arcade.View):
    def __init__(self, score):
        super().__init__()
        self.score = score

    def on_draw(self):
        self.clear()
        arcade.draw_text("GAME OVER", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                         arcade.color.WHITE, font_size=50, anchor_x="center")
        arcade.draw_text(f"Final Score: {self.score}", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 75,
                         arcade.color.WHITE, font_size=20, anchor_x="center")
        arcade.draw_text("Click to play again", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 120,
                         arcade.color.WHITE, font_size=16, anchor_x="center")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        self.window.show_view(GameView())


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = GameView()
    window.show_view(start_view)
    arcade.run()

if __name__ == "__main__":
    main()