import pygame, sys, random, math
from settings import *
from sprites import Player, Malware, Projectile, DataDrop
from ui import UpgradeConsole, DialogueSystem, GameOverScreen
import sprites

class Game:
    def __init__(self):
        # Inicialização básica do Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        # Agora que o display foi criado, carregamos as imagens dos inimigos
        # que usam convert_alpha().
        sprites.load_enemy_images()
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        # Grupos de Sprites
        self.visible_sprites = CameraGroup()
        self.active_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.projectile_sprites = pygame.sprite.Group()
        self.data_sprites = pygame.sprite.Group()

        # Cria o Player
        self.setup_system()

        # UI Elements
        self.dialogue_system = DialogueSystem(self.player)
        self.upgrade_console = UpgradeConsole(self.player, self.dialogue_system)
        self.game_over_screen = GameOverScreen()
        
        # Estados do Jogo
        self.game_paused = False
        self.pause_menu = False
        self.game_over = False

        # Historia inicial
        self.show_story = True
        self.story_text1 = "Olá estagiário! Sei que é seu primeiro dia, mas justo hoje estamos sofrendo invasão no servidor principal. Use suas habilidades para eliminar as ameaças e fortalecer nossa segurança. A empresa INTEIRA DEPENDE de você!"
        self.story_text2 = "Use as setas ou WASD para se mover. Você deve enviar pacotes aos invasores e identificá-los. Após sua identificação, o sistema bloqueia seu endereço por firewall. Colete os dados para subir de nível e aplicar patches no sistema."
        self.start_time = pygame.time.get_ticks()
        self.first_enemies_killed = 0 
        
        # Quantificador de inimigos derrotados
        self.enemies_killed = 0

        self.spawnrate = SPAWN_RATE
        self.enemy_spawn_event = pygame.USEREVENT + 1
        pygame.time.set_timer(self.enemy_spawn_event, self.spawnrate)

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


    def pause(self):
        self.pause_menu = True
        font = pygame.font.SysFont(None, 74)
        text = font.render('Pause Básico', True, COLOR_TEXT)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        
        while self.pause_menu:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.pause_menu = False
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

                if self.game_over:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            self.reset_game()
                
                # Quando o timer disparar, crie um inimigo
                if event.type == self.enemy_spawn_event and not self.game_paused and not self.show_story:
                    self.spawn_enemy()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Jogo pausado
                        self.pause()
            
            self.screen.fill(COLOR_BG)


            if self.game_over:
                # Desenha o jogo congelado ao fundo (opcional)
                self.visible_sprites.custom_draw(self.player)
                # Desenha a tela de Game Over por cima
                self.game_over_screen.display()
        
            elif self.game_paused:

                 # == Menu de Upgrades ==
                self.visible_sprites.custom_draw(self.player)
                self.upgrade_console.display()
                if self.upgrade_console.update():
                    self.game_paused = False
            
            else: 
                self.active_sprites.update()
                # ROTINA NORMAL DE JOGO

                # Checagem de morte do player
                if self.player.integrity <= 0:
                    self.game_over = True
                    print("SISTEMA COMPROMETIDO. REINICIANDO...")

                # --- COLISÕES ---
                
                # 1. Inimigo bate no Player (Dano)
                hit_list = pygame.sprite.spritecollide(self.player, self.enemy_sprites, False)
                if hit_list:
                    self.player.take_damage(ENEMY_DAMAGE)
                    
                # 2. Tiro bate no Inimigo (Morte do Malware)
                # groupcollide(grupo1, grupo2, kill1, kill2)
                # kill1=True (Tiro some), kill2=True (Inimigo morre)
                hits = pygame.sprite.groupcollide(self.projectile_sprites, self.enemy_sprites, True, False)
                
                for projectile, enemies_hit in hits.items():
                        for enemy in enemies_hit: 
                            enemy.take_damage(self.player.projectile_damage)
                            if enemy.health <= 0:
                                # XP ao matar o inimigo
                                DataDrop(enemy.rect.center, self.player, [self.visible_sprites, self.active_sprites, self.data_sprites])
                                self.enemies_killed += 1
                # 3. Player coleta Data (XP)
                collected_data = pygame.sprite.spritecollide(self.player, self.data_sprites, True)
                for data in collected_data:
                    self.player.xp += data.value
                    # Verifica se o player subiu de nível
                    if self.player.xp >= self.player.xp_to_next_level:
                        self.player.level += 1
                        self.player.xp -= self.player.xp_to_next_level
                        
                        self.player.xp_to_next_level = int(self.player.xp_to_next_level * 1.5)
                        print(f"SYSTEM UPGRADE! Nível {self.player.level} alcançado.")
                        
                        # Upgrade
                        self.upgrade_console.generate_options()
                        self.game_paused = True
                
                self.visible_sprites.custom_draw(self.player)
                self.draw_ui()

                if pygame.time.get_ticks() - self.start_time < 10000:
                     self.dialogue_system.execute(
                         self.story_text1, 
                         "TUX AI [ALERTA DE INTRUSÃO]:"
                     )
                if pygame.time.get_ticks() - self.start_time < 30000 and pygame.time.get_ticks() - self.start_time > 10000:
                     self.dialogue_system.execute(
                         self.story_text2, 
                         "TUX AI [SISTEMA INICIALIZADO]:"
                     )
                     self.show_story = False
                
                 # Mensagem ao matar 20 inimigos        
                
                if self.enemies_killed == 20:
                    self.first_enemies_killed = pygame.time.get_ticks()
                
                if pygame.time.get_ticks() - self.first_enemies_killed  < 10000 and self.enemies_killed > 20:
                    self.dialogue_system.execute(
                        "Excelente trabalho! Com essas ameaças encontradas, nosso sistema está mais seguro. Continue assim e não hesite em usar o console de upgrades para fortalecer ainda mais nossas defesas.",
                        "TUX AI [SISTEMA ESTÁVEL]:"
                    )

            pygame.display.update()
            self.clock.tick(FPS)

    # main.py (Dentro da classe Game)

    def reset_game(self):
        # 1. Limpa todos os grupos de sprites
        self.visible_sprites.empty()
        self.active_sprites.empty()
        self.enemy_sprites.empty()
        self.projectile_sprites.empty()
        self.data_sprites.empty()
        
        # 2. Recria o setup inicial (Recria o player do zero)
        self.setup_system()
        self.game_over = False
        self.start_time = pygame.time.get_ticks() # Reinicia timer da história
        self.show_story = True
        self.enemies_killed = 0
        self.upgrade_console = UpgradeConsole(self.player, self.dialogue_system)
        print("SISTEMA REINICIALIZADO.")

    def draw_ui(self):
        # --- Barra de Vida --- (Integridade do Sistema)
        bar_width = 200
        bar_height = 20
        x = 20
        y = 20
        
        # Fundo da barra (cinza escuro)
        bg_rect = pygame.Rect(x, y, bar_width, bar_height)
        pygame.draw.rect(self.screen, (30, 30, 30), bg_rect)

        # Cálculo da porcentagem de vida
        ratio = self.player.integrity / self.player.max_integrity
        current_width = bar_width * ratio
        

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

        # --- Barra de XP ---
        bar_width = 200
        bar_height = 10
        x = 20
        y = 50

        # Fundo da barra (cinza escuro)
        bg_rect = pygame.Rect(x, y, bar_width, bar_height)
        pygame.draw.rect(self.screen, (30, 30, 30), bg_rect)
        # Cálculo da porcentagem de XP
        if self.player.xp_to_next_level > 0:
            xp_ratio = self.player.xp / self.player.xp_to_next_level
        else: xp_ratio = 0

        current_width = bar_width * xp_ratio
        current_rect = pygame.Rect(x, y, current_width, bar_height)

        pygame.draw.rect(self.screen, COLOR_XP, current_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), bg_rect, 1)
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
        bg_offset = (-self.offset.x, -self.offset.y)
        self.display_surface.blit(self.bg_grid, bg_offset)

        # Desenhar os sprites com o deslocamento
        for sprite in self.sprites():
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

if __name__ == '__main__':
    game = Game()
    game.run()