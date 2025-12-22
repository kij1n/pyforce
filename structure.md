```
controller 		# main loop, inputs, events
- input handler		# controller's main task, talks with model
- game controller	# state management

model
- gamestate         # overall state of the game
- entity-manager 	# game entities
- main-character 	# player character
- entity/enemy	# every other mob
  <-> bidirectional class state machine
- physics-manager 	# manage physics, collisions
    * pymunk
- settings-manager 	# read setting, then save
    * json
- menu-state # hold values for the menu

view
- game-renderer 	# render game: entities, player, background, etc.
- camera 		# manage what to render using pyscroll
  * pyscroll
- sprite-loader 	# load character and enemy sprites
- map-loader 		# load map from file
    * pytmx
- menurenderer 		# stores info form pygame-menu
    * pygame-menu
```
A better looking version:
```
root/
│
├── main.py                     # entry poing
├── settings.json
│
├── controller/                 
│   ├── __init__.py             # expose controller
│   ├── controller.py           # main loop and all
│   └── input_handler.py        # handle inputs
│
├── model/                      
│   ├── __init__.py             # expose view
│   ├── model.py                # model class
│   ├── json_manager.py         # reads/rrites JSON
│   ├── physics.py              # pymunk setup
│   └── entities/               
│       ├── __init__.py
│       ├── state_manager.py    # class for updating entity states
│       ├── player.py           # bro logic
│       └── enemy.py            # enemy logic
│
└── view/                       
    ├── __init__.py             # expose view
    ├── view.py                 # view class
    ├── camera.py               # pyscroll Logic
    ├── map_loader.py           # pytmx Logic
    └── ui.py                   # pygame-menu setup
```
