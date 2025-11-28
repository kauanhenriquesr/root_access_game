# Configurações da Janela
WIDTH = 1280
HEIGHT = 720
FPS = 60
TITLE = "Root Access: Protocolo Zero"

# Configurações do Jogo
TILE_SIZE = 32  # Tamanho base para o pixel art (depois escalamos)

# Paleta de Cores (Cyberpunk Theme)
COLOR_BG = (10, 10, 20)        # Azul muito escuro (fundo do terminal)
COLOR_GRID = (40, 40, 60)      # Linhas da grid
COLOR_PLAYER = (0, 255, 200)   # Ciano Neon (O Agente)
COLOR_ENEMY = (255, 50, 50)    # Vermelho Erro (Malware)
COLOR_TEXT = (0, 255, 0)       # Verde Terminal

# Stats Iniciais
PLAYER_SPEED = 10
PLAYER_INTEGRITY = 100
PLAYER_MAX_INTEGRITY = 100
PLAYER_INVINCIBILITY = 700  # Tempo em ms que ele fica imune após hit

# Stats Iniciais Inimigos
ENEMY_SPEED = 3
ENEMY_SIZE = 62       # Um pouco menor que o player
ENEMY_DAMAGE = 10     # Dano causado ao player por colisão
ENEMY_HEALTH = 50     # Vida do inimigo
SPAWN_RATE = 500      # Milissegundos entre cada spawn (quanto menor, mais difícil)

#Stats do Tiro
PROJECTILE_SIZE = 10
PROJECTILE_SPEED = 10
PROJECTILE_LIFETIME = 1000 # Milissegundos que o tiro dura antes de sumir
PROJECTILE_DAMAGE = 25
WEAPON_COOLDOWN = 600      # Cadência de tiro (ms) - Quanto menor, mais rápido
COLOR_PROJECTILE = (255, 255, 0) # Amarelo 
PROJECTILE_SIZE = 78

# Configurações de XP (Data)
COLOR_XP = (170, 255, 0) # Verde brilhante
XP_SIZE = 8
MAGNET_RADIUS = 150      # Distância em pixels para o item começar a voar até o player
DATA_VALUE = 10          # Quanto XP cada item dá

# Paths
PATH_SPRITES = "assets/graphics/"