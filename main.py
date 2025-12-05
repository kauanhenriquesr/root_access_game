import pygame, sys, random, math
from settings import *
from sprites import Player, Malware, Projectile, DataDrop
from ui import UpgradeConsole, DialogueSystem, GameOverScreen, VictoryScreen, PauseScreen, StartScreen
from sound_manager import SoundManager
import sprites

WAVE_TIPS = {
    2: "Alerta! Estão fazendo varredura de portas (port scanning) com Nmap pra descobrir quais serviços a gente deixou aberto. Dica: só deixe liberado o que realmente for necessário.",
    3: "Começou a ENUMERAÇÃO! Estão tentando listar usuários, serviços e compartilhamentos. Menos coisa exposta = menos lugar pra atacar. Desative o que não for usado.",
    4: "BRUTE FORCE na área! Milhares de tentativas de senha por segundo. Senhas fortes + limite de tentativas + autenticação em duas etapas salvam a conta.",
    5: "Tem SNIFFER na rede! Se o tráfego não for criptografado, dá pra ler tudo. Use sempre HTTPS, SSH e outras conexões seguras. Nada de senha em texto puro.",
    6: "Possível ARP POISONING! O invasor está tentando se passar pelo roteador pra ficar no meio da conversa (man-in-the-middle). Onde der, use conexões criptografadas de ponta a ponta.",
    7: "Tentativa de SQL INJECTION detectada! Estão mandando comandos maliciosos pelos campos de formulário. Regra de ouro: nunca confiar na entrada do usuário, sempre validar e tratar.",
    8: "Ataque XSS (Cross-Site Scripting)! Scripts maliciosos estão rodando na tela do usuário pra roubar sessão ou enganar visualmente. Filtre o que é exibido e não deixe código vir direto da entrada.",
    9: "O tráfego explodiu de repente: cheira a ataque de NEGAÇÃO DE SERVIÇO (DoS/DDoS). A ideia é derrubar o servidor pelo cansaço. Limitar pedidos e usar filtros ajuda a segurar a onda.",
    10: "Eles querem persistência no sistema! Tentam instalar backdoors e apagar logs pra voltar depois sem serem notados. Manter registros seguros e ferramentas de segurança ativas é essencial."
}


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

        # Flag para indicar que uma dica deve ser mostrada
        self.show_tip_trigger = False 
        self.tip_text = ""
    
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
        
        if self.current_wave >= 2:
            tip = WAVE_TIPS.get(self.current_wave, "Análise de tráfego concluída. Nenhuma anomalia crítica.")
            self.tip_text = tip
            self.show_tip_trigger = True 
        
        self.wave_active = False
        self.wave_break = True
        self.break_start_time = pygame.time.get_ticks()
        
        # Prepara para a próxima
        self.current_wave += 1
    
    def update(self):
        """Atualiza o estado do gerenciador de hordas"""
        # Se está no intervalo, verifica se acabou
        if self.wave_break:
            if not self.show_tip_trigger:
                # 3 segundos de intervalo entre hordas iniciais
                if pygame.time.get_ticks() - self.break_start_time >= 3000:
                    return True
        
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
        self.victory_screen = VictoryScreen()
        self.pause_screen = PauseScreen(self.player)
        self.start_screen = StartScreen()
        
        # (opcional) iniciar música de fundo já no menu:
        self.sound_manager.play_music(loop=-1)

        # Mostrar tela inicial antes de começar o jogo
        self.show_start_screen()

        # Estados do Jogo
        self.game_paused = False
        self.pause_menu = False
        self.game_over = False
        self.game_won = False
        self.showing_wave_tip = False

        # Historia inicial
        # 2. HISTÓRIA REESCRITA (Mais imersiva e profissional)
        self.show_story = True
        self.story_text1 = "Atenção, estagiário: detectamos tráfego não desejado na borda da rede. Se deixarmos esses pacotes passarem, a disponibilidade dos nossos serviços será comprometida. O servidor não pode cair!"
        self.story_text2 = "Use WASD para navegar na malha de rede. Sua tarefa é mitigar os danos. Use os protocolos de defesa para neutralizar as conexões maliciosas. Colete os logs (XP) para aplicar patches de segurança manter a Integridade do sistema. Os nossos dados não podem ser corrompidos."
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
        
        self.pause_screen.display()
        while self.pause_menu:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.pause_menu = False
            pygame.display.update()
            self.clock.tick(15)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # INPUT DE GAME OVER OU VITÓRIA
                if self.game_over or self.game_won:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            self.reset_game()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Jogo pausado
                        self.pause()
                
                # Avançar Dica da Horda (ESPAÇO)
                if self.showing_wave_tip and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.showing_wave_tip = False
                        # Se passou da horda 10, vence o jogo
                        self.wave_manager.start_wave(self.sound_manager)
                    
                    # Quando o timer disparar, crie um inimigo
                if event.type == self.enemy_spawn_event and not self.game_paused and not self.show_story and not self.game_over and not self.game_won and not self.showing_wave_tip:
                    self.spawn_enemy()
            
            self.screen.fill(COLOR_BG)


            # LÓGICA DE VITÓRIA / DERROTA
            if self.game_over:
                self.visible_sprites.custom_draw(self.player)
                self.game_over_screen.display()
            
            elif self.game_won:
                # Desenha o jogo ao fundo
                self.visible_sprites.custom_draw(self.player)
                # Desenha tela de vitória
                self.victory_screen.display()
        
            elif self.game_paused:
                 self.visible_sprites.custom_draw(self.player)
                 self.upgrade_console.display()
                 if self.upgrade_console.update():
                    self.game_paused = False
            
            elif self.showing_wave_tip:
                # Intervalo entre hordas (Tux fala)
                self.visible_sprites.custom_draw(self.player)
                
                # Relatório de Horda
                title_tip = f"TUX AI [RELATÓRIO HORDA {self.wave_manager.current_wave - 1}]:"
                text_tip = self.wave_manager.tip_text + " (Pressione ESPAÇO para continuar)"
                
                self.dialogue_system.execute(text_tip, title_tip)

            else:
                
                should_start = self.wave_manager.update()
                
                # Se for para começar horda automaticamente (hordas < 5)
                if should_start:
                    self.wave_manager.start_wave(self.sound_manager)
                
                # Se for para mostrar dica (horda >= 5)
                if self.wave_manager.show_tip_trigger:
                    self.showing_wave_tip = True
                    self.wave_manager.show_tip_trigger = False


                if self.wave_manager.current_wave > 10:
                    self.game_won = True
                    self.sound_manager.stop_music()
                    self.sound_manager.play_upgrade() 
                    print("SISTEMA SEGURO. AMEAÇA ELIMINADA.")
                
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
                        "Excelente trabalho! Com essas ameaças controladas, nosso sistema está mais seguro. Continue assim e não hesite em usar o console de upgrades para fortalecer ainda mais nossas defesas.",
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
        
        # 2. Recria o setup inicial
        self.setup_system()
        self.game_over = False
        self.game_won = False
        self.start_time = pygame.time.get_ticks()
        self.show_story = True
        self.enemies_killed = 0
        self.upgrade_console = UpgradeConsole(self.player, self.dialogue_system, self.sound_manager)
        self.pause_screen = PauseScreen(self.player)
        self.dialogue_system = DialogueSystem(self.player)
        
        # 3. Reinicia o sistema de hordas
        self.wave_manager = WaveManager()
        self.wave_manager.start_wave(self.sound_manager)
        
        # 4. Reinicia música de fundo
        self.sound_manager.play_music(loop=-1)
        
        print("SISTEMA REINICIALIZADO.")

        # 5. Volta para a tela inicial
        self.show_start_screen()


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
        font = pygame.font.SysFont("consolas", 24)
        
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

    def show_start_screen(self):
        showing = True
        while showing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        showing = False   # Sai da tela inicial e começa o jogo
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            # Fundo e tela inicial
            self.screen.fill(COLOR_BG)
            self.start_screen.display()

            pygame.display.update()
            self.clock.tick(30)



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