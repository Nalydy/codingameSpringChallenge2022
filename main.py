import math
import sys
from collections import namedtuple
from abc import ABC, abstractmethod


# Main TODO :
# - Develop the Assassin class
# - Develop 'target the nearest enemy from hero' 
# - Do not contol weak monsters
# - Do not hit friendly monsters


########################
# Parsing and metadata #
########################

Entity = namedtuple('Entity', [
    'id', 'type', 'x', 'y', 'shield_life', 'is_controlled', 'health', 'vx', 'vy', 'near_base', 'threat_for', 'dist_from_base', 'threat'
])

TYPE_MONSTER = 0
TYPE_MY_HERO = 1
TYPE_OP_HERO = 2

NEAR_BASE_THREAT_FACTOR = 1000000

# base_x: The corner of the map representing your base
base_x, base_y = [int(i) for i in input().split()]
my_health, my_mana = (3, 0) # Just here for a full scope variable
enemy_base_x, enemy_base_y = (17630, 9000) if base_x == 0 else (0,0)
center_x, center_y = (8815, 4500)
dist_base_to_base = math.dist((base_x, base_y),(enemy_base_x, enemy_base_y))
heros_per_player = int(input())  # Always 3

threat_mapping = [1, 1000, -1000]

# Spells

WIND_MIN_RANGE = 1280
SHIELD_MIN_RANGE = 2200
CONTROL_MIN_RANGE = 2200

# Enemies

# Monsters

###########
# Helpers #
###########

def move_on_target(x, y):
    return f'MOVE {x} {y}'


def wind_away():
    global my_mana
    my_mana -= 10
    return f'SPELL WIND {enemy_base_x} {enemy_base_y}'

def control_away(id):
    global my_mana
    my_mana -= 10
    return f'SPELL CONTROL {id} {enemy_base_x} {enemy_base_y}'


def compute_threat(_type, x, y, near_base, threat_for, dist_from_base):
    if _type != TYPE_MONSTER:
        return 0
    
    base_threat = threat_mapping[threat_for]
    threat_with_dist = base_threat / dist_from_base

    final_threat =  threat_with_dist * (near_base * NEAR_BASE_THREAT_FACTOR + 1)

    if (near_base):
        print(f"WARNING, threat : {final_threat}", file=sys.stderr, flush=True)

    return final_threat


##################
# heros classes #
##################

class Hero(ABC):
    """Basic hero class"""

    @abstractmethod
    def choose_action(self):
        pass
    
    @abstractmethod
    def add_matadata_to_action(self, action: str):
        pass


class Protector(Hero):
    """Hero version that protect my base
    
    Can use :
        - WIND
        - CONTROL
        - SHIELD ? (TODO)
    """

    def __init__(self, entity):
        self.entity = entity
        self.__name__ = f"Protector"


    def choose_action(self):
            current_action = None
            global higgest_threat_dist_from_base
            global controlled_monsters_by_me

            print(f"Hero at {self.entity.dist_from_base} from base.", file=sys.stderr, flush=True)                       

            if monsters:
                higgest_threat = monsters[-1]

                dist_to_monster = math.dist((higgest_threat.x, higgest_threat.y),(self.entity.x, self.entity.y))
                print(f"Dist to monster : {dist_to_monster}", file=sys.stderr, flush=True)

                ### No mana
                if my_mana < 10:
                    current_action = move_on_target(higgest_threat.x, higgest_threat.y)
            
                ### Mana
                # Best to Wind

                # Monster targetting the enemy
                elif higgest_threat.threat < 0 and dist_to_monster <= WIND_MIN_RANGE:
                    current_action = wind_away()


                ## Defensives mesures

                # Monster way too close from base, and at wind range
                elif higgest_threat.dist_from_base < 1500 and dist_to_monster <= WIND_MIN_RANGE:
                    current_action = wind_away()

                # Monster way too close from base, and at control range
                elif higgest_threat.dist_from_base < 1500 and dist_to_monster <= CONTROL_MIN_RANGE:
                    current_action = control_away(higgest_threat.id)                

                # Monster near base
                elif higgest_threat.dist_from_base > 4800: # 5000 - 400

                    # At reange to controll and not already controlled
                    if dist_to_monster <= CONTROL_MIN_RANGE \
                       and higgest_threat.id not in controlled_monsters_by_me \
                       and higgest_threat.threat > 0: # To avoid multible controls and friendly ones
                        current_action = control_away(higgest_threat.id)
                        controlled_monsters_by_me.append(higgest_threat.id)
                
                # Default behavour : target the higgest threat
                else:
                    current_action = move_on_target(higgest_threat.x, higgest_threat.y)


            # We now move to enemy base if we are not so far from base and no monsters at sight
            # -> basic wild mana farm

            idle_spot_x, idle_spot_y = protectors_idle_spot[self.entity.id % heros_per_player]

            if self.entity.dist_from_base > 7500:
                current_action = move_on_target(idle_spot_x, idle_spot_y)
            
            if current_action:
                return self.add_matadata_to_action(current_action)

            # No monsters, go to idle point.
            else:
                return self.add_matadata_to_action(move_on_target(idle_spot_x, idle_spot_y))
         

    def add_matadata_to_action(self, action: str):
        return action + " " + str(self.__name__) + " " + f"{my_mana} MANA"

# TODO 
class Assassin(Hero):
    """Hero version that attack the enemy base
    
    Can use :
        - WIND (TODO)
        - SHIELD (TODO)
        - CONTROL (TODO)
    """

    def __init__(self, entity):
        self.entity = entity
        self.__name__ = f"Assassin {entity.id}"

    def choose_action(self):
        pass

    def add_matadata_to_action(self, action: str):
        return action + " " + str(self.__name__)

############################
# Class dependent metadata #
############################

heros_mapping = [Protector, Protector, Protector]

protectors_idle_spot = [(5000, 1000), (1000, 5000), (3000, 3000)] \
                       if base_x == 0 else \
                       [(12630, 8000), (16630, 4000), (14630, 5000)]


#############
# Game loop #
#############


while True:
    for i in range(2):
        # health: Your base health
        # mana: Ignore in the first league; Spend ten mana to cast a spell
        my_health, my_mana = [int(j) for j in input().split()]
        enemy_health, enemy_mana = [int(j) for j in input().split()]
        entity_count = int(input())  # Amount of heros and monsters you can see
        
        monsters = []
        my_heros = []
        opp_heros = []

    
        for i in range(entity_count):
            _id, _type, x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for = [int(j) for j in input().split()]
            
            # Custom metrics
            dist_from_base = math.dist((base_x, base_y),(x, y))
            threat = compute_threat(_type, x, y, near_base, threat_for, dist_from_base)

            entity = Entity(
                _id,            # _id: Unique identifier
                _type,          # _type: 0=monster, 1=your hero, 2=opponent hero
                x, y,           # x,y: Position of this entity
                shield_life,    # shield_life: Ignore for this league; Count down until shield spell fades
                is_controlled,  # is_controlled: Ignore for this league; Equals 1 when this entity is under a control spell
                health,         # health: Remaining health of this monster
                vx, vy,         # vx,vy: Trajectory of this monster
                near_base,      # near_base: 0=monster with no target yet, 1=monster targeting a base
                threat_for,     # threat_for: Given this monster's trajectory, is it a threat to 1=your base, 2=your opponent's base, 0=neither
                # Added
                dist_from_base = dist_from_base,
                threat = threat
            )
            
            if _type == TYPE_MONSTER:
                monsters.append(entity)
            elif _type == TYPE_MY_HERO:
                # We map the expected behaviour to the hero through our heros_mapping.
                print(f"Hero id {entity.id}.", file=sys.stderr, flush=True)   
                hero = heros_mapping[entity.id % heros_per_player](entity)
                my_heros.append(hero)
            elif _type == TYPE_OP_HERO:
                opp_heros.append(entity)


        monsters.sort(key=lambda monster: monster.threat)


        for i in range(heros_per_player):

            current_hero = my_heros[i]
            action = current_hero.choose_action()
            print(action)

        # reset global variable depending on each round
        controlled_monsters_by_me = []
        
