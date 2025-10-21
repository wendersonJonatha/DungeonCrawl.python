# 📜 Dungeon Crawl - Roguelike (Teste PG Zero)

Um projeto de jogo no estilo Roguelike, desenvolvido em Python utilizando o framework **Pygame Zero**, em conformidade com os requisitos rigorosos do teste de tutores.

---

## 🎯 Requisitos do Projeto

O projeto foi construído para atender aos seguintes critérios específicos:

- **Gênero:** Roguelike (visão de cima, movimento em grid suave).  
- **Módulos Permitidos:** Exclusivamente `pgzrun` (PgZero), `math`, `random` (não usado, mas permitido) e a classe `Rect` do Pygame.  
- **Mecânica de Jogo:** Possui um herói, múltiplos inimigos que patrulham áreas e combate por toque/turno.  
- **Áudio:** Implementação de música de fundo e efeitos sonoros de colisão.  
- **Interface:** Menu principal funcional com botões clicáveis.  

---

## 🛠️ Instalação e Execução

### Pré-requisitos
O projeto requer **Python 3.8+** e o **Pygame Zero**.

```bash
pip install pgzero
Estrutura de Pastas

Para que o jogo funcione corretamente (especialmente o áudio), mantenha a seguinte estrutura:

DungeonCrawl/
├── main.py             # Lógica principal e loop do jogo
├── game_logic.py       # Classes Hero, Enemy e Character
├── menu_logic.py       # Lógica dos botões e do menu
├── sounds/
│   ├── fundo.mp3       # Sua música de fundo (MP3 ou WAV)
│   └── hit.wav         # Seu efeito sonoro de colisão
└── images/
    ├── hero_idle_1.png # Seus sprites (devem seguir o padrão _idle_N e _walk_N)
    └── ...

Como Rodar

Navegue até o diretório principal do projeto (DungeonCrawl/) no terminal e execute:

pgzrun main.py

🕹️ Jogabilidade

O jogo segue um modelo simplificado de roguelike:

Movimento: Use o clique do mouse em uma célula adjacente (8 direções) para mover o herói. O movimento é suave e animado, mas restrito ao grid.

Combate: O dano só ocorre se o herói colidir com um inimigo quando estiver parado (simulando a mecânica de turnos).

Morte: Ao zerar a saúde, a tela de "GAME OVER!" aparece, e o jogo retorna automaticamente ao menu principal após 3 segundos.

🧑‍💻 Destaques Técnicos

As seguintes classes e recursos foram desenvolvidos para atender aos requisitos estritos:

1. Sistema de Movimento e Animação (game_logic.py)

Classe Character: Base para Hero e Enemy. Gerencia o movimento suave entre células (update_movement) e a animação de sprites.

Animação Cíclica: Implementação de idle_frames e walk_frames (conjuntos de 4 quadros: _1 a _4) para garantir a animação de sprite cíclica exigida.

Movimento Fluido: O herói aceita novos alvos de movimento imediatamente após um clique, melhorando a jogabilidade.

2. Contorno do Bug de Áudio

Devido a um bug de carregamento de áudio do Pygame Zero em alguns ambientes, a música de fundo (fundo.mp3) é carregada via pygame.mixer.music.load() e não via music.play().

Isso garante o funcionamento do áudio sem violar o requisito de não usar o módulo principal do Pygame (exceto a classe Rect).

3. Transição de Estado

A função dedicada return_to_menu() gerencia o agendamento de retorno do GAME OVER, garantindo que a música seja parada e que o estado mude sem conflitos.
