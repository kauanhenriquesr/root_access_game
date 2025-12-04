import os
import pygame
import math
import os
import random
from settings import *

# Simples: só carregamos a imagem principal da horda `anonymus.png`.
# Procuramos em `assets/enemies/anonymus.png` primeiro, depois no root.
ANONYMUS_NAME = 'anonymus.png'
ENEMY_IMAGES = []
ENEMY_IMAGE_SOURCES = []
_fallback_color = (200, 50, 50)


def load_enemy_images():
    """Carrega as imagens dos inimigos após o Pygame estar inicializado.
    Usa `convert_alpha()` por isso deve ser chamado depois de `pygame.init()` e
    depois de criar o display em caso de backends que exigem vídeo.
    """
    # Limpa listas anteriores
    ENEMY_IMAGES.clear()
    ENEMY_IMAGE_SOURCES.clear()

    # Prioridade: assets/enemies/anonymus.png
    candidate_paths = [os.path.join(os.getcwd(), 'assets', 'enemies', ANONYMUS_NAME),
                       os.path.join(os.getcwd(), ANONYMUS_NAME)]

    loaded = None
    for path in candidate_paths:
        if os.path.isfile(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (ENEMY_SIZE, ENEMY_SIZE))
                ENEMY_IMAGES.append(img)
                ENEMY_IMAGE_SOURCES.append(os.path.basename(path))
                loaded = True
                break
            except Exception:
                loaded = False

    if not ENEMY_IMAGES:
        # fallback simples
        surf = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE), pygame.SRCALPHA)
        surf.fill(_fallback_color)
        ENEMY_IMAGES.append(surf)
        ENEMY_IMAGE_SOURCES.append(f"fallback_color_{_fallback_color}")


def list_enemy_images():
    """Retorna uma cópia da lista das fontes das imagens carregadas."""
    return ENEMY_IMAGE_SOURCES.copy()

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, enemy_sprites, create_projectile_func, sound_manager=None):
        super().__init__(groups)

        # --------- IMAGEM DO TUX PARA A UI (base_image) ----------
        base_dir = os.path.dirname(__file__)
        try:
            # se o teu arquivo estiver em assets/tux.webp, usa essa linha:
            tux_path = os.path.join(base_dir, "assets", "tux.webp")
            tux_loaded = pygame.image.load(tux_path).convert_alpha()
            self.base_image = pygame.transform.scale(tux_loaded, (TILE_SIZE, TILE_SIZE))
        except Exception:
            # fallback caso não ache o arquivo
            self.base_image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            self.base_image.fill(COLOR_PLAYER)

        # --------- SPRITESHEET DO PROTAGONISTA (sprite que anda) ----------
        self.load_images()  # monta self.animations e self.hurt_frame

        self.status = "down_idle"
        self.frame_index = 0
        self.animation_speed = 0.15

        # AQUI usamos o protagonista como imagem de jogo
        self.image = self.animations[self.status][0]
        self.rect = self.image.get_rect(topleft=pos)


        # Movimento
        self.direction = pygame.math.Vector2()

        # Flags de dano/invencibilidade
        self.vulnerable = True
        self.hurt_time = 0
        self.hurt = False          # se está usando o frame de dano

        # Inimigos e tiro
        self.enemy_sprites = enemy_sprites
        self.create_projectile = create_projectile_func
        self.can_shoot = True
        self.shoot_time = 0
        
        # Som
        self.sound_manager = sound_manager

        # Sistema de level
        self.xp = 0
        self.level = 1
        self.xp_to_next_level = 100


        # Upgrades
        self.upgrades_history = []

        # Atributos do player
        self.speed = PLAYER_SPEED
        self.max_integrity = PLAYER_MAX_INTEGRITY
        self.integrity = self.max_integrity

        self.projectile_type = 'udp_packet'
        self.projectile_damage = PROJECTILE_DAMAGE
        self.projectile_cooldown = WEAPON_COOLDOWN
        self.projectile_speed = PROJECTILE_SPEED

    # ---------------- CARREGAR SPRITES -----------------

    def load_images(self):
        """
        Carrega Protagonista.png (3x3) e monta o dicionário de animações.

        Numeração dos frames (linha a linha):
        1 2 3
        4 5 6
        7 8 9
        """
        base_dir = os.path.dirname(__file__)
        img_path = os.path.join(base_dir, "assets", "Protagonista.png")
        sheet = pygame.image.load(img_path).convert_alpha()


        sheet_width, sheet_height = sheet.get_size()
        frame_width = sheet_width // 3
        frame_height = sheet_height // 3

        def get_frame(col, row):
            frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            frame.blit(
                sheet,
                (0, 0),
                pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height)
            )
            frame = pygame.transform.scale(frame, (TILE_SIZE*3, TILE_SIZE*3))
            return frame

        # Numeração 1–9
        f1 = get_frame(0, 0)  # 1
        f2 = get_frame(1, 0)  # 2
        f3 = get_frame(2, 0)  # 3
        f4 = get_frame(0, 1)  # 4
        f5 = get_frame(1, 1)  # 5
        f6 = get_frame(2, 1)  # 6
        f7 = get_frame(0, 2)  # 7
        f8 = get_frame(1, 2)  # 8
        f9 = get_frame(2, 2)  # 9 (dano)

        # Frame de dano
        self.hurt_frame = f9

        # Corrida pra baixo (1 e 2) + idle
        down_frames = [f1, f2]
        # Corrida pra cima (3 e 4)
        up_frames = [f3, f4]
        # Corrida pra esquerda (5–8)
        left_frames = [f5, f6, f7, f8]
        # Direita = flip horizontal da esquerda
        right_frames = [
            pygame.transform.flip(frame, True, False) for frame in left_frames
        ]

        self.animations = {
            "down": down_frames,
            "down_idle": [f1],
            "up": up_frames,
            "up_idle": [f3],
            "left": left_frames,
            "left_idle": [left_frames[0]],
            "right": right_frames,
            "right_idle": [right_frames[0]],
        }

    # ---------------- ENTRADA / MOVIMENTO -----------------

    def input(self):
        keys = pygame.key.get_pressed()

        self.direction.x = 0
        self.direction.y = 0

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.direction.y = -1
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.direction.y = 1

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = 1
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction.x = -1

    def get_status(self):
        # Direção principal
        if self.direction.y > 0:
            self.status = "down"
        elif self.direction.y < 0:
            self.status = "up"
        elif self.direction.x < 0:
            self.status = "left"
        elif self.direction.x > 0:
            self.status = "right"
        else:
            # parado → idle na última direção
            if "down" in self.status:
                self.status = "down_idle"
            elif "up" in self.status:
                self.status = "up_idle"
            elif "left" in self.status:
                self.status = "left_idle"
            elif "right" in self.status:
                self.status = "right_idle"
            else:
                self.status = "down_idle"

    def move(self, speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()
        self.rect.center += self.direction * speed
        
        # Limita o movimento dentro do mapa (2000x2000)
        map_size = 2000
        half_width = self.rect.width // 2
        half_height = self.rect.height // 2
        
        # Limita X
        if self.rect.centerx < half_width:
            self.rect.centerx = half_width
        elif self.rect.centerx > map_size - half_width:
            self.rect.centerx = map_size - half_width
        
        # Limita Y
        if self.rect.centery < half_height:
            self.rect.centery = half_height
        elif self.rect.centery > map_size - half_height:
            self.rect.centery = map_size - half_height

    # ---------------- DANO / INVENCIBILIDADE -----------------

    def take_damage(self, amount):
        if self.vulnerable:
            self.integrity -= amount
            self.vulnerable = False
            self.hurt = True
            self.hurt_time = pygame.time.get_ticks()
            print(f"ALERTA DE SEGURANÇA: Integridade em {self.integrity}%")

    def cooldowns(self):
        current_time = pygame.time.get_ticks()

        if not self.vulnerable:
            if current_time - self.hurt_time >= PLAYER_INVINCIBILITY:
                self.vulnerable = True
                self.hurt = False
                self.image.set_alpha(255)
            else:
                # Pisca enquanto invulnerável
                if (current_time // 100) % 2 == 0:
                    self.image.set_alpha(100)
                else:
                    self.image.set_alpha(255)

    # ---------------- TIRO AUTOMÁTICO -----------------

    def get_nearest_enemy(self):
        if not self.enemy_sprites:
            return None

        nearest_enemy = None
        min_distance = float('inf')
        player_vec = pygame.math.Vector2(self.rect.center)

        for enemy in self.enemy_sprites:
            enemy_vec = pygame.math.Vector2(enemy.rect.center)
            dist = player_vec.distance_to(enemy_vec)
            if dist < min_distance:
                min_distance = dist
                nearest_enemy = enemy

        return nearest_enemy

    def auto_shoot(self):
        current_time = pygame.time.get_ticks()

        if self.can_shoot:
            target = self.get_nearest_enemy()
            if target:
                self.can_shoot = False
                self.shoot_time = current_time

                player_vec = pygame.math.Vector2(self.rect.center)
                target_vec = pygame.math.Vector2(target.rect.center)

                try:
                    direction = (target_vec - player_vec).normalize()
                except ValueError:
                    direction = pygame.math.Vector2(0, 0)

                self.create_projectile(self.rect.center, direction)

    def weapon_cooldowns(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.projectile_cooldown:
                self.can_shoot = True

    # ---------------- ANIMAÇÃO -----------------

    def animate(self):
        # Se estiver em estado de dano, usa frame 9
        if self.hurt:
            self.image = self.hurt_frame
            return

        animation = self.animations[self.status]
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        self.image = animation[int(self.frame_index)]

    # ---------------- UPDATE GERAL -----------------

    def update(self):
        self.input()
        self.get_status()
        self.move(self.speed)
        self.cooldowns()
        self.weapon_cooldowns()
        self.auto_shoot()
        self.animate()


class Malware(pygame.sprite.Sprite):
    def __init__(self, pos, player, groups, health_mult=1.0, speed_mult=1.0, damage_mult=1.0):
        super().__init__(groups)
        
        # Carregar spritesheet do inimigo
        self.load_images()
        self.image = self.walk_frames[0]
        self.rect = self.image.get_rect(center=pos)

        # Aplica multiplicadores de dificuldade
        self.health = int(ENEMY_HEALTH * health_mult)
        self.max_health = self.health
        self.damage = int(ENEMY_DAMAGE * damage_mult)

        # Mecânica de perseguição
        self.player = player
        self.speed = ENEMY_SPEED * speed_mult
        self.direction = pygame.math.Vector2()

        # Animação
        self.animation_index = 0
        self.animation_speed = 0.15  # quanto maior, mais rápido alterna
        self.state = "walk"          # "walk" ou "hurt"
        self.hurt_time = 0
        self.hurt_duration = 120     # ms que fica no frame de dano

    def load_images(self):
        # Spritesheet: 2 colunas x 2 linhas
        # Pega a pasta onde o sprites.py está
        base_dir = os.path.dirname(__file__)
        # Monta o caminho completo até a imagem
        img_path = os.path.join(base_dir, "assets", "Inimigo.png")
        sheet = pygame.image.load(img_path).convert_alpha()
        sheet_width, sheet_height = sheet.get_size()


        frame_width = sheet_width // 2
        frame_height = sheet_height // 2

        def get_frame(col, row):
            frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            frame.blit(
                sheet,
                (0, 0),
                pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height),
            )
            # Escala para o tamanho do inimigo definido em settings.py
            frame = pygame.transform.scale(frame, (ENEMY_SIZE, ENEMY_SIZE))
            return frame

        # 0,0 e 1,0 → caminhada
        self.walk_frames = [get_frame(0, 0), get_frame(1, 0)]
        # 0,1 → dano
        self.hurt_frame = get_frame(0, 1)

    def hunt_player(self):
        player_vector = pygame.math.Vector2(self.player.rect.center)
        enemy_vector = pygame.math.Vector2(self.rect.center)
        distance = player_vector - enemy_vector

        if distance.magnitude() > 0:
            self.direction = distance.normalize()
        else:
            self.direction = pygame.math.Vector2()

    def take_damage(self, amount):
        self.health -= amount
        self.state = "hurt"
        self.hurt_time = pygame.time.get_ticks()

        if self.health <= 0:
            self.kill()

    def animate(self):
        if self.state == "walk":
            self.animation_index += self.animation_speed
            if self.animation_index >= len(self.walk_frames):
                self.animation_index = 0
            self.image = self.walk_frames[int(self.animation_index)]
        elif self.state == "hurt":
            self.image = self.hurt_frame

    def update_state(self):
        # Sai do estado de dano depois de hurt_duration ms
        if self.state == "hurt":
            current_time = pygame.time.get_ticks()
            if current_time - self.hurt_time >= self.hurt_duration:
                self.state = "walk"

    def update(self):
        self.hunt_player()
        self.rect.center += self.direction * self.speed
        self.update_state()
        self.animate()

class Projectile(pygame.sprite.Sprite):
    # cache da imagem pra não recarregar do disco toda hora
    _base_image = None

    @classmethod
    def _get_base_image(cls):
        if cls._base_image is None:
            base_dir = os.path.dirname(__file__)
            img_path = os.path.join(base_dir, "assets", "Projetil.png")

            image = pygame.image.load(img_path).convert_alpha()
            image = pygame.transform.scale(image, (PROJECTILE_SIZE, PROJECTILE_SIZE))

            cls._base_image = image
        return cls._base_image

    def __init__(self, pos, direction, groups, speed=PROJECTILE_SPEED, damage=PROJECTILE_DAMAGE):
        super().__init__(groups)

        # direção
        self.direction = pygame.math.Vector2(direction)
        if self.direction.length_squared() != 0:
            self.direction = self.direction.normalize()
        else:
            self.direction = pygame.math.Vector2(1, 0)

        self.speed = speed
        self.damage = damage

        # imagem base
        base_image = self._get_base_image()

        # calcula o ângulo a partir da direção
        # OBS: aqui estou assumindo que a sprite aponta "pra cima" originalmente.
        # Se ela apontar para a direita, é só tirar o -90.
        angle = math.degrees(math.atan2(-self.direction.y, self.direction.x)) - 90

        # rotaciona mantendo o centro
        self.image = pygame.transform.rotate(base_image, angle)
        self.rect = self.image.get_rect(center=pos)

    def update(self):
        # move o tiro
        self.rect.center += self.direction * self.speed
        # depois podemos colocar limite de tela / lifetime se quiser


class DataDrop(pygame.sprite.Sprite):
    def __init__(self, pos, player, groups):
        super().__init__(groups)
        
        # Visual: Pequeno quadrado de dados
        self.image = pygame.Surface((XP_SIZE, XP_SIZE))
        self.image.fill(COLOR_XP)
        self.rect = self.image.get_rect(center=pos)
        
        # Referências
        self.player = player
        self.value = DATA_VALUE
        
        # Física do Ímã
        self.speed = 0
        self.acceleration = 0.5  # Começa devagar e acelera
        self.max_speed = 15

    def update(self):
        # Calcular distância até o player
        player_vec = pygame.math.Vector2(self.player.rect.center)
        data_vec = pygame.math.Vector2(self.rect.center)
        distance = player_vec.distance_to(data_vec)
        
        # Se estiver dentro do raio do ímã
        if distance < MAGNET_RADIUS:
            # Calcular direção
            direction = (player_vec - data_vec).normalize()
            
            # Aumentar velocidade (Efeito de sucção)
            if self.speed < self.max_speed:
                self.speed += self.acceleration
            
            # Mover
            self.rect.center += direction * self.speed