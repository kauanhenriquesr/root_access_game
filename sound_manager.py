import pygame
import os

class SoundManager:
    """Gerenciador centralizado de sons do jogo"""
    
    def __init__(self):
        pygame.mixer.init()
        
        # Carrega todos os sons
        self.shoot_sound = self.load_sound('assets/sounds/shoot.wav')
        self.wave_start_sound = self.load_sound('assets/sounds/wave_start.wav')
        self.upgrade_sound = self.load_sound('assets/sounds/upgrade.wav')
        self.hit_sound = self.load_sound('assets/sounds/hit.wav')
        self.enemy_death_sound = self.load_sound('assets/sounds/enemy_death.wav')
        self.player_hurt_sound = self.load_sound('assets/sounds/player_hurt.wav')
        self.game_over_sound = self.load_sound('assets/sounds/game_over.wav')
        
        # Música de fundo
        self.background_music_path = 'assets/sounds/soundtrack.wav'
        if os.path.exists(self.background_music_path):
            pygame.mixer.music.load(self.background_music_path)
            pygame.mixer.music.set_volume(0.3)
        else:
            # Tenta no diretório raiz
            alt_path = 'soundtrack.wav'
            if os.path.exists(alt_path):
                self.background_music_path = alt_path
                pygame.mixer.music.load(self.background_music_path)
                pygame.mixer.music.set_volume(0.3)
    
    def load_sound(self, path):
        """Carrega um som, retorna som vazio se não encontrar"""
        try:
            if os.path.exists(path):
                sound = pygame.mixer.Sound(path)
                return sound
            else:
                # Retorna som silencioso se arquivo não existir
                return pygame.mixer.Sound(buffer=bytes(32))
        except Exception as e:
            print(f"Aviso: Não foi possível carregar {path}: {e}")
            return pygame.mixer.Sound(buffer=bytes(32))
    
    def play_shoot(self, volume=0.2):
        """Som de tiro do jogador"""
        self.shoot_sound.set_volume(volume)
        self.shoot_sound.play()
    
    def play_wave_start(self, volume=0.6):
        """Som de início de horda"""
        self.wave_start_sound.set_volume(volume)
        self.wave_start_sound.play()
    
    def play_upgrade(self, volume=0.5):
        """Som de upgrade disponível"""
        self.upgrade_sound.set_volume(volume)
        self.upgrade_sound.play()
    
    def play_hit(self, volume=0.4):
        """Som de inimigo levando dano"""
        self.hit_sound.set_volume(volume)
        self.hit_sound.play()
    
    def play_enemy_death(self, volume=0.4):
        """Som de inimigo morrendo"""
        self.enemy_death_sound.set_volume(volume)
        self.enemy_death_sound.play()
    
    def play_player_hurt(self, volume=0.5):
        """Som de jogador levando dano"""
        self.player_hurt_sound.set_volume(volume)
        self.player_hurt_sound.play()
    
    def play_game_over(self, volume=2.0):
        """Som de game over (jogador morreu)"""
        self.game_over_sound.set_volume(volume)
        self.game_over_sound.play()
    
    def play_music(self, loop=-1):
        """Toca música de fundo (loop=-1 para repetir infinitamente)"""
        if os.path.exists(self.background_music_path):
            pygame.mixer.music.play(loop)
    
    def stop_music(self):
        """Para a música de fundo"""
        pygame.mixer.music.stop()
    
    def set_music_volume(self, volume):
        """Ajusta volume da música (0.0 a 1.0)"""
        pygame.mixer.music.set_volume(volume)
