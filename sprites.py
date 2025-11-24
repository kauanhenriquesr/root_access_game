import pygame
import math
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, enemy_sprites, create_projectile_func):
        super().__init__(groups)
        # Carrega sprite do jogador (tux2.jpg) se disponível, senão usa placeholder
        try:
            loaded = pygame.image.load("tux.webp").convert_alpha()
            # Armazena a imagem base e escala para o tamanho do tile
            self.base_image = pygame.transform.scale(loaded, (50, 50))
        except Exception:
            # Fallback: superfície simples colorida
            self.base_image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            self.base_image.fill(COLOR_PLAYER)

        # Imagem atual usada para efeitos (cópia de base_image)
        self.image = self.base_image.copy()
        
        # Hitbox e Posicionamento
        self.rect = self.image.get_rect(topleft=pos)
        
        # Vetor de movimento (x, y)
        self.direction = pygame.math.Vector2()

        # Stats
        self.vulnerable = True
        self.hurt_time = 0
        self.image_alpha = 255 # Para o efeito de piscar

        # Novas referências para o combate
        self.enemy_sprites = enemy_sprites 
        self.create_projectile = create_projectile_func # Função callback para criar o tiro
        
        # Cooldown do tiro
        self.can_shoot = True
        self.shoot_time = 0

        # Sistema de LEVEL
        self.xp = 0
        self.level = 1
        self.xp_to_next_level = 100

        # --- Atributos do player ---
        self.speed = PLAYER_SPEED
        self.max_integrity = PLAYER_MAX_INTEGRITY
        self.integrity = self.max_integrity

        # Arma
        self.projectile_damage = PROJECTILE_DAMAGE
        self.projectile_cooldown = WEAPON_COOLDOWN
        self.projectile_speed = PROJECTILE_SPEED

    def input(self):
        keys = pygame.key.get_pressed()

        # Movimento WASD ou Setas
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.direction.y = -1
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = 1
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction.x = -1
        else:
            self.direction.x = 0

    def move(self, speed):
        # Normalizar vetor (para não andar mais rápido na diagonal)
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()
        
        self.rect.center += self.direction * speed

    def take_damage(self, amount):
        if self.vulnerable:
            self.integrity -= amount
            self.vulnerable = False
            self.hurt_time = pygame.time.get_ticks()
            print(f"ALERTA DE SEGURANÇA: Integridade em {self.integrity}%")
            
            # Efeito visual de dano (overlay branco momentâneo)
            flash = self.base_image.copy()
            # Adiciona branco por cima para simular flash
            white = pygame.Surface(flash.get_size(), pygame.SRCALPHA)
            white.fill((255, 255, 255, 180))
            flash.blit(white, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            self.image = flash
    
    def cooldowns(self):
        current_time = pygame.time.get_ticks()

        if not self.vulnerable:
            # Verifica se o tempo de invencibilidade acabou
            if current_time - self.hurt_time >= PLAYER_INVINCIBILITY:
                self.vulnerable = True
                # Restaura a imagem base e garante opacidade total
                self.image = self.base_image.copy()
                self.image.set_alpha(255)
            else:
                # Efeito de piscar (Flicker) enquanto invulnerável
                # Alterna a transparência baseado no tempo (senoide simples simulada)
                if (current_time // 100) % 2 == 0:
                    temp = self.base_image.copy()
                    temp.set_alpha(100)
                    self.image = temp
                else:
                    temp = self.base_image.copy()
                    temp.set_alpha(255)
                    self.image = temp

    def check_death(self):
        if self.integrity <= 0:
            # Por enquanto, apenas fecha o jogo, depois faremos uma tela de Game Over
            print("FATAL ERROR: SYSTEM CRASHED")
            pygame.quit()
            exit()
        
    def get_nearest_enemy(self):
        # Cria uma lista de inimigos e suas distâncias
        if not self.enemy_sprites:
            return None
            
        nearest_enemy = None
        min_distance = float('inf') # Começa com infinito
        
        player_vec = pygame.math.Vector2(self.rect.center)
        
        for enemy in self.enemy_sprites:
            enemy_vec = pygame.math.Vector2(enemy.rect.center)
            # distance_to é uma função otimizada do Pygame
            dist = player_vec.distance_to(enemy_vec)
            
            if dist < min_distance:
                min_distance = dist
                nearest_enemy = enemy
                
        return nearest_enemy

    def auto_shoot(self):
        current_time = pygame.time.get_ticks()
        
        # Verifica Cooldown
        if self.can_shoot:
            target = self.get_nearest_enemy()
            
            if target: # Só atira se tiver inimigo
                self.can_shoot = False
                self.shoot_time = current_time
                
                # Calcular direção do tiro
                player_vec = pygame.math.Vector2(self.rect.center)
                target_vec = pygame.math.Vector2(target.rect.center)
                
                # Vetor direção = Destino - Origem
                try: direction = (target_vec - player_vec).normalize()
                except ValueError:
                    direction = pygame.math.Vector2(0, 0)
                # Chama a função lá do main para criar o tiro
                self.create_projectile(self.rect.center, direction)

    def weapon_cooldowns(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.projectile_cooldown:
                self.can_shoot = True

    def update(self):
        self.input()
        self.move(self.speed)
        self.cooldowns()      # Invencibilidade
        self.weapon_cooldowns() # Recarga da arma
        self.auto_shoot()     # Tenta atirar
        self.check_death()

class Malware(pygame.sprite.Sprite):
    def __init__(self, pos, player, groups):
        super().__init__(groups)
        
        # Visual (Placeholder: Quadrado Vermelho com "Glitch")
        self.image = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE))
        self.image.fill(COLOR_ENEMY)
        
        self.rect = self.image.get_rect(center=pos)
        
        self.health = ENEMY_HEALTH

        # Mecânica de Perseguição
        self.player = player # Referência ao alvo (o servidor)
        self.speed = ENEMY_SPEED
        self.direction = pygame.math.Vector2()

        # Dano ticar
        self.hit_time = 0
        self.is_flashing = False

    def hunt_player(self):
        # Vetor do Inimigo até o Player
        player_vector = pygame.math.Vector2(self.player.rect.center)
        enemy_vector = pygame.math.Vector2(self.rect.center)
        
        # Subtrair vetores dá a direção (Distância)
        distance = player_vector - enemy_vector

        # Normalizar: Transforma a distância em direção pura (valor entre -1 e 1)
        if distance.magnitude() > 0:
            self.direction = distance.normalize()
        else:
            self.direction = pygame.math.Vector2()

    def take_damage(self, amount):
        self.health -= amount
        self.is_flashing = True
        self.hit_time = pygame.time.get_ticks()

        if self.health <= 0:
            self.kill()
    
    def visuals(self):
        if self.is_flashing:
            current_time = pygame.time.get_ticks()
            # Acusador de dano
            self.image.fill((255, 255, 255))

            # Duração do efeito
            if current_time - self.hit_time > 100:
                self.is_flashing = False
                self.image.fill(COLOR_ENEMY)
    
    def update(self):
        self.hunt_player()
        # Move o inimigo na direção calculada
        self.rect.center += self.direction * self.speed
        self.visuals()

class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos, direction, groups):
        super().__init__(groups)
        
        # Visual: Um pequeno "bit" quadrado
        self.image = pygame.Surface((10, 10))
        self.image.fill(COLOR_PROJECTILE)
        self.rect = self.image.get_rect(center=pos)
        
        # Física
        self.direction = direction
        self.speed = PROJECTILE_SPEED
        
        # Tempo de vida (para não lagar o jogo com tiros infinitos voando)
        self.spawn_time = pygame.time.get_ticks()

    def update(self):
        # Move o projétil
        self.rect.center += self.direction * self.speed
        
        # Checa se o tempo de vida acabou
        if pygame.time.get_ticks() - self.spawn_time > PROJECTILE_LIFETIME:
            self.kill() # Remove o sprite de todos os grupos e libera memória

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