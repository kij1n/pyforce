```
pyforce/
│
├── main.py                     # Entry point
├── settings.json               # Configuration (physics, paths, constants)
├── requirements.txt            # Dependencies
├── pyproject.toml              # Project metadata
│
├── game_state/                 # Controller Logic
│   ├── __init__.py
│   ├── controller.py           # Main loop, coordinates Model and View
│   ├── input_handler.py        # Processes keyboard/mouse events
│   └── json_manager.py         # Loads settings.json
│
├── game_data/                  # Model Logic
│   ├── __init__.py
│   ├── model.py                # Core game state container
│   ├── physics.py              # Pymunk physics engine wrapper
│   ├── entities/               # Game objects
│   │   ├── __init__.py
│   │   ├── entity_manager.py   # Manages creation/deletion of entities
│   │   ├── player.py           # Player specific logic
│   │   ├── enemy.py            # Enemy AI and behavior
│   │   ├── state_manager.py    # State machine implementation
│   │   ├── state.py            # State base class
│   │   ├── patrol_path.py      # Enemy patrol logic
│   │   └── entity_utils.py     # Collision box helpers
│   └── weaponry/               # Weapon logic
│       ├── __init__.py
│       ├── weapon.py           # Weapon base logic
│       ├── bullet.py           # Projectile logic
│       └── ammo.py             # Ammo definitions
│
├── game_view/                  # View Logic
│   ├── __init__.py
│   ├── view.py                 # Main rendering orchestrator
│   ├── ui.py                   # Pygame-menu integration
│   ├── entity_renderer.py      # Draws sprites/entities
│   ├── map_renderer.py         # PyTMX map rendering
│   └── sprite_loader.py        # Asset caching and loading
│
├── shared/                     # Common Utilities & Enums
│   ├── __init__.py
│   ├── game_state.py           # GameState enum (MENU, PLAYING, etc.)
│   ├── debug_elements.py       # Debug visualizers (hitboxes)
│   ├── direction.py            # Direction enum
│   ├── enemy_enum.py           # Enemy types
│   ├── state_name.py           # Entity states (IDLE, RUN, etc.)
│   ├── weapon_utils.py
│   └── where.py                # Coordinate data class
│
└── assets/                     # Game Resources
├── map/                    # TMX maps and tilesets
├── player/                 # Player sprites
└── enemies/                # Enemy sprites
```