# Sistema de Som - Instruções

## Sons Implementados

O jogo agora possui um sistema completo de sons com os seguintes efeitos:

### Sons Criados:
1. **shoot.wav** - Toca quando o jogador atira
2. **wave_start.wav** - Toca quando uma nova horda inicia
3. **upgrade.wav** - Toca quando o menu de upgrades abre (level up)
4. **hit.wav** - Toca quando um inimigo leva dano
5. **enemy_death.wav** - Toca quando um inimigo morre
6. **player_hurt.wav** - Toca quando o jogador leva dano

### Como Substituir os Sons:

Os arquivos atualmente são silenciosos (placeholder). Para adicionar sons reais:

1. Encontre arquivos de som em formato **.wav** ou **.ogg**
2. Substitua os arquivos em `assets/sounds/`
3. Mantenha os mesmos nomes de arquivo

### Fontes Gratuitas de Sons:

- **Freesound.org** - Sons gratuitos da comunidade
- **OpenGameArt.org** - Sons para jogos
- **Zapsplat.com** - Efeitos sonoros gratuitos
- **Mixkit.co** - Sons de alta qualidade

### Música de Fundo (Opcional):

Para adicionar música de fundo:
1. Coloque um arquivo `background.ogg` em `assets/sounds/`
2. No `main.py`, adicione após criar o sound_manager:
   ```python
   self.sound_manager.play_music()
   ```

### Ajustar Volume:

Os volumes já estão pré-configurados, mas você pode ajustar nos métodos do `sound_manager.py`:
- `play_shoot(volume=0.3)` - 30% do volume
- `play_wave_start(volume=0.6)` - 60% do volume
- `play_upgrade(volume=0.5)` - 50% do volume
- etc.

### Testar:

Execute o jogo normalmente com `python main.py`. Os sons tocarão automaticamente quando:
- Você atirar
- Uma nova horda começar
- Você subir de nível
- Inimigos levarem/causarem dano
