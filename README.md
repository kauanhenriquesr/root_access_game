# 🎮 Root Access: Protocolo Zero

Um jogo de sobrevivência em hordas com temática de segurança cibernética, desenvolvido em Python com Pygame.

## 📚 Informações Acadêmicas

**Disciplina:** Informática e Sociedade
**Instituição:** Universidade de Brasília 

### 👥 Equipe de Desenvolvimento

- Gustavo Rinaldi Braga de Albuquerque - 222008664
- Kauan Henrique Da Silva Rodrigues - 221017050
- Gustavo Choueiri - 232014010

## 📖 Sobre o Jogo

Root Access: Protocolo Zero é um jogo onde você assume o papel de um estagiário de TI que precisa defender o servidor da empresa contra invasões cibernéticas. Enfrente hordas cada vez mais difíceis de malwares enquanto fortalece suas defesas através de upgrades inspirados em ferramentas reais de segurança.

## 🎯 Mecânicas Principais

### Sistema de Hordas
- **Ondas Progressivas**: Cada horda aumenta o número de inimigos (começa com 5, +6 por horda)
- **Dificuldade Escalável**: Inimigos ficam mais fortes, rápidos e resistentes a cada nível
- **Intervalo Estratégico**: 3 segundos entre hordas para se recuperar

### Combate
- **Tiro Automático**: O personagem atira automaticamente no inimigo mais próximo
- **Sistema de Dano**: Inimigos causam dano ao colidir com o jogador
- **Invencibilidade Temporária**: 700ms de invulnerabilidade após levar dano

### Progressão
- **Sistema de XP**: Colete dados deixados pelos inimigos eliminados
- **Level Up**: Ganhe níveis e escolha upgrades inspirados em ferramentas reais

## 🛠️ Tecnologias Utilizadas

- **Python 3.11+**
- **Pygame 2.5.2**: Engine do jogo
- **Bibliotecas Padrão**: math, random, sys, os

## 🚀 Como Executar

### Pré-requisitos
```bash
pip install pygame
```

### Executando o Jogo
```bash
python main.py
```

## 🎮 Controles

- **Movimentação**: Setas direcionais ou W/A/S/D
- **Ataque**: Automático (mira no inimigo mais próximo)
- **Menu de Upgrades**: Clique nas opções com o mouse
- **Reiniciar**: Pressione ESPAÇO após Game Over
- **Pausar**: ESC

## 📁 Estrutura do Projeto

```
root_access_game/
├── main.py              # Loop principal do jogo
├── sprites.py           # Classes de sprites (Player, Malware, Projectile)
├── settings.py          # Configurações e constantes
├── ui.py                # Interface do usuário (menus, diálogos)
├── sound_manager.py     # Gerenciador de áudio
├── groups.py            # Grupos de sprites (vazio)
├── assets/
│   ├── Protagonista.png # Spritesheet do jogador
│   ├── Inimigo.png      # Spritesheet dos inimigos
│   ├── Projetil.png     # Sprite do projétil
│   ├── tux.webp         # Avatar para UI
│   └── sounds/          # Efeitos sonoros e trilha
└── README.md
```

## 🎓 Conceitos de Segurança Abordados

O jogo incorpora conceitos reais de cibersegurança de forma educativa:

- **APT (Advanced Package Tool)**: Gestão de pacotes e atualizações
- **Nmap**: Ferramenta de varredura de rede e timing templates
- **Kernel Hardening**: Patches de segurança no núcleo do sistema
- **Rate Limiting**: Controle de taxa de envio de pacotes
- **Payloads**: Carga de dados em pacotes de rede
- **UDP/TCP**: Protocolos de comunicação
- **Firewall**: Bloqueio de endereços maliciosos
- **CVEs**: Vulnerabilidades e correções de segurança

## 📊 Configurações Ajustáveis

Todas as configurações podem ser modificadas em `settings.py`:

- Velocidade do jogador
- Estatísticas dos inimigos
- Taxa de spawn
- Dano e cadência de tiro
- Multiplicadores de dificuldade
- Tempo entre hordas
- E muito mais!


## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

---
