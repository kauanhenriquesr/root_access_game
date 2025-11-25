import pygame
import random
from settings import *

class UpgradeConsole:
    def __init__(self, player, dialogue_system):
        self.player = player
        self.dialogue_system = dialogue_system

        self.display_surface = pygame.display.get_surface()
        
        self.font = pygame.font.SysFont("consolas", 20) 
        self.header_font = pygame.font.SysFont("consolas", 30, bold=True)

        self.options = [] 
        self.rects = []

    def generate_options(self):
        
        # Lógica auxiliar para legibilidade do código
        p = self.player 
        scan_flag = "-sU" if p.projectile_type == "udp_packet" else "-sT"
        proto_name = "UDP" if p.projectile_type == "udp_packet" else "TCP"
        
        pool = [
            {
                'name': f'apt-get upgrade speed_v{p.level}', 
                'desc': 'Aumenta velocidade de movimento (+10%)', 
                'type': 'speed',
                'value': 1.1,
                'edu_text': 'Conceito: GESTÃO DE PACOTES (APT). Manter softwares atualizados via repositórios seguros garante que o sistema opere com as correções de performance mais recentes, evitando lentidão na resposta a incidentes.'
            },
            {
                'name': f'nmap -T{min(p.level, 5)} --min-rtt-timeout',
                'desc': 'Reduz delay de disparo (-15%)', 
                'type': 'cooldown', 
                'value': 0.85,
                'edu_text': f'Conceito: TIMING TEMPLATES (-T). O Nmap usa templates de 0 a 5 para definir a agressividade da varredura. Ajustar o RTT (Round-Trip Time) permite enviar pacotes mais rápido, otimizando a detecção de ameaças na rede.'
            },
            {
                'name': f'kernel_patch_v{(p.max_integrity+20)/100:.1f}_security_fix', 
                'desc': 'Aumenta integridade máxima (+20)', 
                'type': 'health', 
                'value': 20,
                'edu_text': 'Conceito: KERNEL HARDENING. O Kernel é o núcleo do sistema. Aplicar patches de segurança corrige vulnerabilidades críticas (CVEs), tornando o servidor mais resistente a falhas e tentativas de derrubada (Crash).'
            },
            {
                'name': f'nmap {scan_flag} --max-rate {int(p.projectile_damage + 5)}', 
                'desc': f'Aumenta payload de pacotes {proto_name} (+5)', 
                'type': 'damage', 
                'value': 5,
                'edu_text': f'Conceito: RATE LIMITING & PAYLOADS. No nmap, definir o --max-rate controla a taxa de envio de pacotes. Em segurança ofensiva, aumentar a carga (payload) simula testes de estresse para verificar se o firewall inimigo aguenta o tranco.'
            },
        ]
        
        self.options = random.sample(pool, 3)
        self.rects = [] 

    def apply_upgrade(self, upgrade):
        """Aplica a lógica matemática no Player"""
        print(f"Executando script: {upgrade['name']}...")
        
        if upgrade['type'] == 'speed':
            self.player.speed *= upgrade['value']
        elif upgrade['type'] == 'cooldown':
            self.player.projectile_cooldown *= upgrade['value']
        elif upgrade['type'] == 'health':
            self.player.max_integrity += upgrade['value']
            self.player.integrity += upgrade['value'] # Cura o valor ganho
        elif upgrade['type'] == 'damage':
            self.player.projectile_damage += upgrade['value']

    def display(self):
        # 1. Configuração da Janela
        width = 700
        height = 500
        x = (WIDTH - width) // 2
        y = (HEIGHT - height) // 2
        
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.display_surface, (0, 0, 0), bg_rect)
        pygame.draw.rect(self.display_surface, (0, 255, 0), bg_rect, 3)
        
        # 2. Cabeçalho
        header_text = f"root@server:~/updates# install_patch --level={self.player.level}"
        header_surf = self.font.render(header_text, True, (0, 255, 0))
        self.display_surface.blit(header_surf, (x + 20, y + 20))

        # 3. Loop das Opções
        mouse_pos = pygame.mouse.get_pos()
        self.rects = []
        hover_text = "Selecione um patch para aplicar ao sistema."
        hover_title = "TUX AI [UPGRADE LOG]:"

        if not self.options:
            self.generate_options()

        for index, option in enumerate(self.options):
            item_y = y + 100 + (index * 110)
            
            item_rect = pygame.Rect(x + 20, item_y, width - 40, 90)
            self.rects.append(item_rect)
            
            # Hover Effect
            color_text = (0, 255, 0)     # Verde Hacker
            color_desc = (0, 180, 0)     # Verde Escuro
            color_stats = (0, 255, 255)  # Ciano (para os números destacarem)
            


            if item_rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.display_surface, (0, 50, 0), item_rect)
                color_text = (200, 255, 200)
                cursor = self.font.render(">", True, (0, 255, 0))
                self.display_surface.blit(cursor, (x + 5, item_y + 10))
                hover_text = option.get('edu_text', "Analisando...")

            # Nome e Descrição
            name_surf = self.header_font.render(f"[{index+1}] {option['name']}", True, color_text)
            self.display_surface.blit(name_surf, (x + 30, item_y + 5))
            
            desc_surf = self.font.render(f"    >> {option['desc']}", True, color_desc)
            self.display_surface.blit(desc_surf, (x + 30, item_y + 35))

            # --- 4. CALCULAR E DESENHAR PREVIEW DOS STATS ---
            current_val = 0
            new_val = 0
            unit = ""
            
            # Lógica de previsão baseada no tipo (Mesma lógica do apply_upgrade)
            if option['type'] == 'speed':
                current_val = self.player.speed
                new_val = current_val * option['value']
                unit = "px/frame"
            elif option['type'] == 'cooldown':
                current_val = self.player.projectile_cooldown
                new_val = current_val * option['value']
                unit = "ms (delay)"
            elif option['type'] == 'health':
                current_val = self.player.max_integrity
                new_val = current_val + option['value']
                unit = "HP"
            elif option['type'] == 'damage':
                current_val = self.player.projectile_damage
                new_val = current_val + option['value']
                unit = "dmg"

            stat_text = f"    [ UPDATE LOG: {current_val:.1f} -> {new_val:.1f} {unit} ]"
            
            stat_surf = self.font.render(stat_text, True, color_stats)
            self.display_surface.blit(stat_surf, (x + 30, item_y + 60))
        
        # 5. Desenhar Caixa de Diálogo Educativa
        self.dialogue_system.execute(hover_text, hover_title)

    def update(self):
        """Retorna True se escolheu algo (para fechar o menu)"""
        # Verifica cliques
        if pygame.mouse.get_pressed()[0]: # Botão esquerdo
            mouse_pos = pygame.mouse.get_pos()
            
            for index, rect in enumerate(self.rects):
                if rect.collidepoint(mouse_pos):
                    # Aplicar upgrade e sinalizar para fechar menu
                    self.apply_upgrade(self.options[index])
                    
                    # Restaura toda a vida do player ao subir de nível
                    self.player.integrity = self.player.max_integrity

                    # Pequeno delay para não atirar assim que sair do menu
                    pygame.time.wait(200) 
                    return True
        return False
    
class DialogueSystem:
    def __init__(self, player):
        self.player = player
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.SysFont("consolas", 18)
        self.title_font = pygame.font.SysFont("consolas", 18, bold=True)
        
        self.active = False
        self.current_text = ""
        self.current_title = "SIEM AI [SYSTEM LOG]:"

    def draw_text_wrapped(self, text, rect, color):
        """Quebra o texto automaticamente para caber na caixa"""
        y = rect.top
        line_height = self.font.get_height() * 1.2
        words = text.split(' ')
        current_line_words = []

        for word in words:
            test_line = ' '.join(current_line_words + [word])
            w, h = self.font.size(test_line)
            
            if w > rect.width:
                line_surf = self.font.render(' '.join(current_line_words), True, color)
                self.display_surface.blit(line_surf, (rect.left, y))
                y += line_height
                current_line_words = [word]
            else:
                current_line_words.append(word)
        
        if current_line_words:
            line_surf = self.font.render(' '.join(current_line_words), True, color)
            self.display_surface.blit(line_surf, (rect.left, y))

    def execute(self, text, title="TUX AI [SYSTEM LOG]:"):
        """Método principal para chamar no loop do jogo"""
        screen_w, screen_h = self.display_surface.get_size()
        
        # Config Layout
        box_height = 140
        margin = 20
        padding = 15
        
        box_rect = pygame.Rect(margin, screen_h - box_height - margin, screen_w - (margin * 2), box_height)
        
        # 1. Desenhar Fundo e Borda
        pygame.draw.rect(self.display_surface, (10, 15, 30), box_rect) # Fundo Azul Escuro
        pygame.draw.rect(self.display_surface, (0, 200, 200), box_rect, 2) # Borda Neon
        
        # 2. Desenhar Avatar (Player)
        avatar_size = 100
        avatar_rect = pygame.Rect(box_rect.left + padding, box_rect.top + padding, avatar_size, avatar_size)
        
        pygame.draw.rect(self.display_surface, (0, 0, 0), avatar_rect)
        pygame.draw.rect(self.display_surface, (0, 200, 200), avatar_rect, 1)
        
        if hasattr(self.player, 'image'):
             img_rect = self.player.image.get_rect(center=avatar_rect.center)
             self.display_surface.blit(self.player.image, img_rect)
        else:
             pygame.draw.rect(self.display_surface, COLOR_PLAYER, avatar_rect.inflate(-20, -20))

        # 3. Desenhar Texto
        text_x = avatar_rect.right + padding
        text_y = box_rect.top + padding
        text_w = box_rect.width - avatar_size - (padding * 3)
        
        # Título
        title_surf = self.title_font.render(title, True, (0, 255, 255))
        self.display_surface.blit(title_surf, (text_x, text_y))
        
        # Corpo do Texto
        body_rect = pygame.Rect(text_x, text_y + 30, text_w, box_rect.height - 30)
        self.draw_text_wrapped(text, body_rect, (220, 220, 220))

# ui.py (Adicione ao final)

class GameOverScreen:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.title_font = pygame.font.SysFont("consolas", 60, bold=True)
        self.text_font = pygame.font.SysFont("consolas", 24)
        self.sub_font = pygame.font.SysFont("consolas", 18)

    def display(self):
        # 1. Fundo Semi-transparente Vermelho (Sangue Digital)
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((20, 0, 0)) # Fundo quase preto, levemente vermelho
        overlay.set_alpha(230)   # Transparência
        self.display_surface.blit(overlay, (0, 0))

        # 2. Borda de Erro Crítico
        pygame.draw.rect(self.display_surface, (255, 0, 0), (50, 50, WIDTH-100, HEIGHT-100), 4)
        
        # 3. Textos
        center_x = WIDTH // 2
        
        # Título: SYSTEM FAILURE
        title_surf = self.title_font.render("SYSTEM FAILURE", True, (255, 0, 0))
        title_rect = title_surf.get_rect(center=(center_x, 150))
        self.display_surface.blit(title_surf, title_rect)
        
        # Mensagem Principal (A pedida)
        msg_lines = [
            "FATAL ERROR: Integridade do Servidor Comprometida.",
            "--------------------------------------------------",
            "RELATÓRIO DE INCIDENTE:",
            "Os dados cruciais da empresa foram vazados.",
            "Protocolo de RH ativado: VOCÊ FOI DEMITIDO.",
        ]
        
        for i, line in enumerate(msg_lines):
            color = (255, 255, 255) if i != 4 else (255, 50, 50) # A linha "Demits" em vermelho
            text_surf = self.text_font.render(line, True, color)
            text_rect = text_surf.get_rect(center=(center_x, 280 + (i * 40)))
            self.display_surface.blit(text_surf, text_rect)

        # 4. Botão de "Tentar Novamente" (Piscando)
        current_time = pygame.time.get_ticks()
        if (current_time // 500) % 2 == 0: # Pisca a cada meio segundo
            prompt_text = "Pressione [ESPAÇO] para Reinicializar o Sistema"
            prompt_surf = self.text_font.render(prompt_text, True, (0, 255, 0)) # Verde Esperança
            prompt_rect = prompt_surf.get_rect(center=(center_x, HEIGHT - 150))
            self.display_surface.blit(prompt_surf, prompt_rect)