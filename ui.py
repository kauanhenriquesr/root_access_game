import pygame
import random
from settings import *

class UpgradeConsole:
    def __init__(self, player):
        self.player = player
        self.display_surface = pygame.display.get_surface()
        # Fonte Monospace (Courier ou Consolas) para look de terminal
        self.font = pygame.font.SysFont("consolas", 20) 
        self.header_font = pygame.font.SysFont("consolas", 30, bold=True)
        
        # Definição dos Upgrades Possíveis
        # Cada upgrade tem: Texto Display, Chave do atributo, Valor a somar/multiplicar
        self.upgrade_pool = [
            {'name': 'sudo apt-get install speed', 'desc': 'Aumenta velocidade de movimento (+10%)', 'type': 'speed', 'value': 1.1},
            {'name': 'chmod +x packet_fire', 'desc': 'Reduz delay de disparo (-15%)', 'type': 'cooldown', 'value': 0.85},
            {'name': 'kernel_patch_v2.4', 'desc': 'Aumenta integridade máxima (+20)', 'type': 'health', 'value': 20},
            {'name': 'insmod damage_module', 'desc': 'Aumenta dano do pacote (+5)', 'type': 'damage', 'value': 5},
        ]
        
        self.options = [] # Opções sorteadas para o menu atual
        self.rects = []   # Áreas clicáveis

    def generate_options(self):
        """Sorteia 3 opções aleatórias do pool"""
        self.options = random.sample(self.upgrade_pool, 3)
        self.rects = [] # Limpa os retângulos antigos

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
        # 1. Desenhar Fundo Preto (Terminal)
        # Cria uma janela menor que a tela cheia
        width = 700
        height = 500
        x = (WIDTH - width) // 2
        y = (HEIGHT - height) // 2
        
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.display_surface, (0, 0, 0), bg_rect)         # Fundo Preto
        pygame.draw.rect(self.display_surface, (0, 255, 0), bg_rect, 3)    # Borda Verde Hacker
        
        # 2. Cabeçalho do Terminal
        header_text = f"root@server:~/updates# install_patch --level={self.player.level}"
        header_surf = self.font.render(header_text, True, (0, 255, 0))
        self.display_surface.blit(header_surf, (x + 20, y + 20))

        # 3. Desenhar Opções
        mouse_pos = pygame.mouse.get_pos()
        self.rects = [] # Reinicia a lista de colisão para este frame

        for index, option in enumerate(self.options):
            # Calcular posição Y de cada item
            item_y = y + 100 + (index * 100)
            
            # Criar retângulo da opção
            item_rect = pygame.Rect(x + 20, item_y, width - 40, 80)
            self.rects.append(item_rect)
            
            # Hover Effect (Muda a cor do fundo se passar o mouse)
            color_text = (0, 255, 0)
            if item_rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.display_surface, (0, 50, 0), item_rect) # Fundo verde escuro
                color_text = (200, 255, 200) # Texto fica mais claro
                # Desenha cursor >
                cursor = self.font.render(">", True, (0, 255, 0))
                self.display_surface.blit(cursor, (x + 5, item_y + 10))

            # Texto do Nome (Comando)
            name_surf = self.header_font.render(f"[{index+1}] {option['name']}", True, color_text)
            self.display_surface.blit(name_surf, (x + 30, item_y + 10))
            
            # Texto da Descrição
            desc_surf = self.font.render(f"    >> {option['desc']}", True, (0, 180, 0))
            self.display_surface.blit(desc_surf, (x + 30, item_y + 45))

    def update(self):
        """Retorna True se escolheu algo (para fechar o menu)"""
        # Verifica cliques
        if pygame.mouse.get_pressed()[0]: # Botão esquerdo
            mouse_pos = pygame.mouse.get_pos()
            
            for index, rect in enumerate(self.rects):
                if rect.collidepoint(mouse_pos):
                    # Aplicar upgrade e sinalizar para fechar menu
                    self.apply_upgrade(self.options[index])
                    # Pequeno delay para não atirar assim que sair do menu
                    pygame.time.wait(200) 
                    return True
        return False