import pygame, sys, random, math
from settings import *
from sprites import Player, Malware, Projectile

class Game:
    def __init__(self):
        # Inicialização básica do Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        # Grupos de Sprites
        self.visible_sprites = CameraGroup()
        self.active_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.projectile_sprites = pygame.sprite.Group()

        self.setup_system()

        self.enemy_spawn_event = pygame.USEREVENT + 1
        pygame.time.set_timer(self.enemy_spawn_event, SPAWN_RATE)

    def setup_system(self):
        # Note que agora passamos self.enemy_sprites e self.create_projectile
        self.player = Player(
            (WIDTH // 2, HEIGHT // 2), 
            [self.visible_sprites, self.active_sprites],
            self.enemy_sprites,
            self.create_projectile
        )
    
    def create_projectile(self, pos, direction):
        # Esta função é passada para o Player chamar quando quiser atirar
        Projectile(pos, direction, [self.visible_sprites, self.active_sprites, self.projectile_sprites])
    
    def spawn_enemy(self):
        # Lógica para spawnar inimigos FORA da tela
        # Escolhe um ângulo aleatório (0 a 360 graus)
        angle = random.uniform(0, 360)
        # Define uma distância segura (Raio) maior que a tela
        radius = WIDTH // 1.5 
        
        # Precisamos somar à posição atual do player para ser relativo a ele
        x = self.player.rect.centerx + radius * math.cos(math.radians(angle))
        y = self.player.rect.centery + radius * math.sin(math.radians(angle))
        
        Malware((x, y), self.player, [self.visible_sprites, self.active_sprites, self.enemy_sprites])


    def pause_menu(self):
        paused = True
        font = pygame.font.SysFont(None, 74)
        text = font.render('Pause Básico', True, COLOR_TEXT)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        paused = False
            
            self.screen.fill(COLOR_BG)
            self.screen.blit(text, text_rect)
            pygame.display.update()
            self.clock.tick(15)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # Quando o timer disparar, crie um inimigo
                if event.type == self.enemy_spawn_event:
                    self.spawn_enemy()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Jogo pausado
                        self.pause_menu()
            
            self.screen.fill(COLOR_BG)
            self.active_sprites.update()

            # --- COLISÕES ---
            
            # 1. Inimigo bate no Player (Dano)
            hit_list = pygame.sprite.spritecollide(self.player, self.enemy_sprites, False)
            if hit_list:
                self.player.take_damage(ENEMY_DAMAGE)
                
            # 2. Tiro bate no Inimigo (Morte do Malware)
            # groupcollide(grupo1, grupo2, kill1, kill2)
            # kill1=True (Tiro some), kill2=True (Inimigo morre)
            hits = pygame.sprite.groupcollide(self.projectile_sprites, self.enemy_sprites, True, True)
            
            if hits:
                # Opcional: Aqui futuramente adicionaremos XP e Sons
                # hits retorna um dicionário, podemos contar quantos morreram
                for projectile, enemies_hit in hits.items():
                    print(f"Malware eliminado! Memória liberada.")

            self.visible_sprites.custom_draw(self.player)
            self.draw_ui()

            pygame.display.update()
            self.clock.tick(FPS)

    def draw_ui(self):
        # Desenha a barra de "Integridade do Sistema"
        bar_width = 200
        bar_height = 20
        x = 20
        y = 20
        
        # Fundo da barra (cinza escuro)
        bg_rect = pygame.Rect(x, y, bar_width, bar_height)
        pygame.draw.rect(self.screen, (30, 30, 30), bg_rect)

        # Cálculo da porcentagem de vida
        ratio = self.player.integrity / PLAYER_MAX_INTEGRITY
        current_width = bar_width * ratio
        
        # Barra de vida atual
        # Muda de cor: Verde (seguro) -> Vermelho (crítico)
        if ratio > 0.6:
            color = (0, 255, 0)
        elif ratio > 0.3:
            color = (255, 255, 0)
        else:
            color = (255, 0, 0)

        current_rect = pygame.Rect(x, y, current_width, bar_height)
        pygame.draw.rect(self.screen, color, current_rect)
        
        # Borda da barra (Branca)
        pygame.draw.rect(self.screen, (255, 255, 255), bg_rect, 2)

# --- Classe de Câmera Simples ---
class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()
        
        # Grid de fundo (efeito visual Cyberpunk)
        self.bg_grid = pygame.Surface((2000, 2000)) # Tamanho do mapa teste
        self.bg_grid.fill(COLOR_BG)
        for x in range(0, 2000, TILE_SIZE):
            pygame.draw.line(self.bg_grid, COLOR_GRID, (x, 0), (x, 2000))
        for y in range(0, 2000, TILE_SIZE):
            pygame.draw.line(self.bg_grid, COLOR_GRID, (0, y), (2000, y))

    def custom_draw(self, player):
        # Calcular o deslocamento da câmera em relação ao player
        self.offset.x = player.rect.centerx - WIDTH // 2
        self.offset.y = player.rect.centery - HEIGHT // 2

        # Desenhar o chão deslocado
        bg_offset = (-self.offset.x, -self.offset.y) # Simples para teste
        self.display_surface.blit(self.bg_grid, bg_offset)

        # Desenhar os sprites com o deslocamento
        for sprite in self.sprites():
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

if __name__ == '__main__':
    game = Game()
    game.run()