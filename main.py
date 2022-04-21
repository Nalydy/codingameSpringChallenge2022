import sys
import math
from collections import namedtuple

# This code use Python 3.9.12

# Current league : Bois 2

def move_on_target(x, y):
    return f'MOVE {x} {y}'

# Parsing the standard input according to the problem statement.

Entity = namedtuple('Entity', [
    'id', 'type', 'x', 'y', 'shield_life', 'is_controlled', 'health', 'vx', 'vy', 'near_base', 'threat_for'
])

TYPE_MONSTER = 0
TYPE_MY_HERO = 1
TYPE_OP_HERO = 2

# base_x: The corner of the map representing your base
base_x, base_y = [int(i) for i in input().split()]
heroes_per_player = int(input())  # Always 3

# game loop
while True:
    for i in range(2):
        # health: Your base health
        # mana: Ignore in the first league; Spend ten mana to cast a spell
        my_health, my_mana = [int(j) for j in input().split()]
        enemy_health, enemy_mana = [int(j) for j in input().split()]
        entity_count = int(input())  # Amount of heros and monsters you can see
        
        monsters = []
        my_heroes = []
        opp_heroes = []

    
        for i in range(entity_count):
            _id, _type, x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for = [int(j) for j in input().split()]
            entity = Entity(
                _id,            # _id: Unique identifier
                _type,          # _type: 0=monster, 1=your hero, 2=opponent hero
                x, y,           # x,y: Position of this entity
                shield_life,    # shield_life: Ignore for this league; Count down until shield spell fades
                is_controlled,  # is_controlled: Ignore for this league; Equals 1 when this entity is under a control spell
                health,         # health: Remaining health of this monster
                vx, vy,         # vx,vy: Trajectory of this monster
                near_base,      # near_base: 0=monster with no target yet, 1=monster targeting a base
                threat_for      # threat_for: Given this monster's trajectory, is it a threat to 1=your base, 2=your opponent's base, 0=neither
            )
            
            if _type == TYPE_MONSTER:
                monsters.append(entity)
            elif _type == TYPE_MY_HERO:
                my_heroes.append(entity)
            elif _type == TYPE_OP_HERO:
                opp_heroes.append(entity)

        for i in range(heroes_per_player):
            very_dangerous_monsters = [monster for monster in monsters if monster.threat_for == 1 and monster.near_base == 1]

            dangerous_monsters = [monster for monster in monsters if monster.threat_for == 1]

            target = None
            current_heroes = my_heroes[i]
            current_action = None

            dist_from_base = math.dist((base_x, base_y),(current_heroes.x, current_heroes.y))
            print(f"Hero {i} is at {dist_from_base} from base.", file=sys.stderr, flush=True)

            # Focus dangerous monsters first
            if very_dangerous_monsters:
                target = dangerous_monsters[i % len(dangerous_monsters)]
                current_action = move_on_target(target.x, target.y)
            
            elif dangerous_monsters:
                target = dangerous_monsters[i % len(dangerous_monsters)]
                current_action = move_on_target(target.x, target.y)            

            # If not too far and no threats, focus a random monster
            # TODO : change this for 'nearest monster'
            elif monsters and current_action == None and dist_from_base < 8000:
                target = monsters[i % len(monsters)]
                current_action = move_on_target(target.x, target.y)
            
            # In the first league: MOVE <x> <y> | WAIT; In later leagues: | SPELL <spellParams>;
            if current_action:
                print(current_action)
            
            else:
                #print('WAIT')
                print(move_on_target(base_x, base_y))
                print(f"Hero {i} failed to pick a decision.", file=sys.stderr, flush=True)



