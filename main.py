import pygame, sys, random, math
from settings import *
from sprites import Player, Malware, Projectile, DataDrop
from ui import UpgradeConsole, DialogueSystem, GameOverScreen
from sound_manager import SoundManager
import sprites

class WaveManager:
    """Gerencia o sistema de hordas do jogo"""
    def __init__(self):
        self.current_wave = 1
        self.enemies_in_wave = WAVE_BASE_ENEMIES
        self.enemies_spawned = 0
        self.enemies_killed_this_wave = 0
        
        # Estados da horda
        self.wave_active = False
        self.wave_break = False
        self.break_start_time = 0
        
        # Multiplicadores de dificuldade
        self.health_multiplier = 1.0
        self.speed_multiplier = 1.0
        self.damage_multiplier = 1.0
    
    def start_wave(self, sound_manager=None):
        """Inicia uma nova horda"""
        self.wave_active = True
        self.wave_break = False
        self.enemies_spawned = 0
        self.enemies_killed_this_wave = 0
        
        # Calcula quantos inimigos nesta horda
        self.enemies_in_wave = WAVE_BASE_ENEMIES + (self.current_wave - 1) * WAVE_ENEMY_INCREMENT
        
        # Atualiza multiplicadores de dificuldade
        self.health_multiplier = 1.0 + (self.current_wave - 1) * (WAVE_HEALTH_MULTIPLIER - 1.0)
        self.speed_multiplier = 1.0 + (self.current_wave - 1) * (WAVE_SPEED_MULTIPLIER - 1.0)
        self.damage_multiplier = 1.0 + (self.current_wave - 1) * (WAVE_DAMAGE_MULTIPLIER - 1.0)
        
        # Toca som de início de horda
        if sound_manager:
            sound_manager.play_wave_start()
        
        print(f"\n{'='*50}")
        print(f"HORDA {self.current_wave} INICIADA!")
        print(f"Inimigos: {self.enemies_in_wave}")
        print(f"Dificuldade: x{round(self.health_multiplier, 2)}")
        print(f"{'='*50}\n")
    
    def end_wave(self):
        """Finaliza a horda atual e inicia o intervalo"""
        self.wave_active = False
        self.wave_break = True
        self.break_start_time = pygame.time.get_ticks()
        self.current_wave += 1
        
        print(f"\n{'='*50}")
        print(f"HORDA {self.current_wave - 1} COMPLETA!")
        print(f"Preparando próxima horda...")
        print(f"{'='*50}\n")
    
    def update(self):
        """Atualiza o estado do gerenciador de hordas"""
        # Se está no intervalo, verifica se acabou
        if self.wave_break:
            current_time = pygame.time.get_ticks()
            if current_time - self.break_start_time >= WAVE_BREAK_TIME:
                self.start_wave(sound_manager=None)
        
        # Se a horda está ativa e todos os inimigos foram mortos
        elif self.wave_active:
            if self.enemies_killed_this_wave >= self.enemies_in_wave:
                self.end_wave()
    
    def can_spawn_enemy(self):
        """Verifica se pode spawnar mais inimigos"""
        return self.wave_active and self.enemies_spawned < self.enemies_in_wave
    
    def enemy_spawned(self):
        """Registra que um inimigo foi spawnado"""
        self.enemies_spawned += 1
    
    def enemy_killed(self):
        """Registra que um inimigo foi morto"""
        self.enemies_killed_this_wave += 1
    
    def get_remaining_time(self):
        """Retorna o tempo restante do intervalo em segundos"""
        if self.wave_break:
            elapsed = pygame.time.get_ticks() - self.break_start_time
            remaining = max(0, WAVE_BREAK_TIME - elapsed)
            return remaining / 1000
        return 0
    
    def get_remaining_enemies(self):
        """Retorna quantos inimigos faltam ser mortos"""
        return self.enemies_in_wave - self.enemies_killed_this_wave

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

        # Sistema de Som
        self.sound_manager = SoundManager()
        
        # Cria o Player
        self.setup_system()

        # UI Elements
        self.dialogue_system = DialogueSystem(self.player)
        self.upgrade_console = UpgradeConsole(self.player, self.dialogue_system, self.sound_manager)
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

        # Sistema de Hordas
        self.wave_manager = WaveManager()
        self.wave_manager.start_wave(self.sound_manager)  # Inicia a primeira horda
        
        # Timer para spawn de inimigos (mais lento, controlado pelo wave_manager)
        self.enemy_spawn_event = pygame.USEREVENT + 1
        pygame.time.set_timer(self.enemy_spawn_event, 1000)  # Verifica a cada 1 segundo
        
        # Inicia música de fundo em loop
        self.sound_manager.play_music(loop=-1)

    def setup_system(self):
        # Note que agora passamos self.enemy_sprites e self.create_projectile
        self.player = Player(
            (WIDTH // 2, HEIGHT // 2), 
            [self.visible_sprites, self.active_sprites],
            self.enemy_sprites,
            self.create_projectile,
            self.sound_manager
        )
    
    def create_projectile(self, pos, direction):
        # Esta função é passada para o Player chamar quando quiser atirar
        Projectile(pos, direction, [self.visible_sprites, self.active_sprites, self.projectile_sprites])
        # Toca som de tiro
        self.sound_manager.play_shoot()
    
    def spawn_enemy(self):
        # Só spawna se o wave_manager permitir
        if not self.wave_manager.can_spawn_enemy():
            return
        
        # Lógica para spawnar inimigos FORA da tela
        # Escolhe um ângulo aleatório (0 a 360 graus)
        angle = random.uniform(0, 360)
        # Define uma distância segura (Raio) maior que a tela
        radius = WIDTH // 1.5 
        
        # Precisamos somar à posição atual do player para ser relativo a ele
        x = self.player.rect.centerx + radius * math.cos(math.radians(angle))
        y = self.player.rect.centery + radius * math.sin(math.radians(angle))
        
        # Cria o inimigo com os multiplicadores da horda atual
        enemy = Malware(
            (x, y), 
            self.player, 
            [self.visible_sprites, self.active_sprites, self.enemy_sprites],
            self.wave_manager.health_multiplier,
            self.wave_manager.speed_multiplier,
            self.wave_manager.damage_multiplier
        )
        
        # Registra que spawnou um inimigo
        self.wave_manager.enemy_spawned()


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
                # Atualiza o gerenciador de hordas
                self.wave_manager.update()
                
                self.active_sprites.update()
                # ROTINA NORMAL DE JOGO

                # Checagem de morte do player
                if self.player.integrity <= 0:
                    self.game_over = True
                    self.sound_manager.stop_music()  # Para a música de fundo
                    self.sound_manager.play_game_over()
                    print("SISTEMA COMPROMETIDO. REINICIANDO...")

                # --- COLISÕES ---
                
                # 1. Inimigo bate no Player (Dano)
                hit_list = pygame.sprite.spritecollide(self.player, self.enemy_sprites, False)
                if hit_list:
                    # Usa o dano específico do inimigo (com multiplicador da horda)
                    self.player.take_damage(hit_list[0].damage)
                    self.sound_manager.play_player_hurt()
                    
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
                                self.wave_manager.enemy_killed()  # Registra morte no wave_manager
                                self.sound_manager.play_enemy_death()
                            else:
                                self.sound_manager.play_hit()
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
        self.upgrade_console = UpgradeConsole(self.player, self.dialogue_system, self.sound_manager)
        
        # 3. Reinicia o sistema de hordas
        self.wave_manager = WaveManager()
        self.wave_manager.start_wave(self.sound_manager)
        
        # 4. Reinicia música de fundo
        self.sound_manager.play_music(loop=-1)
        
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
        
        # --- Informações da Horda ---
        font = pygame.font.SysFont(None, 32)
        
        # Exibe o número da horda
        wave_text = font.render(f"HORDA: {self.wave_manager.current_wave}", True, COLOR_TEXT)
        self.screen.blit(wave_text, (WIDTH - 220, 20))
        
        # Se está em intervalo, mostra contagem regressiva
        if self.wave_manager.wave_break:
            remaining_time = int(self.wave_manager.get_remaining_time())
            countdown_text = font.render(f"Próxima horda em: {remaining_time}s", True, (255, 200, 0))
            self.screen.blit(countdown_text, (WIDTH // 2 - 150, 20))
        else:
            # Mostra inimigos restantes
            remaining = self.wave_manager.get_remaining_enemies()
            enemies_text = font.render(f"Inimigos: {remaining}/{self.wave_manager.enemies_in_wave}", True, (255, 100, 100))
            self.screen.blit(enemies_text, (WIDTH - 220, 60))
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