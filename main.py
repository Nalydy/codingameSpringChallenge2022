import sys
import math
from abc import ABC, abstractmethod

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

TYPE_MONSTER = 0
TYPE_MY_HERO = 1
TYPE_OP_HERO = 2

# base_x: The corner of the map representing your base
base_x, base_y = [int(i) for i in input().split()]
my_health, my_mana = (3, 0) # Just here for a full scope variable
heroes_per_player = int(input())  # Always 3

########################
# Additionals metadata #
########################

## Minimmum range on spells
MR_WIND = 1280
MR_SHIELD = 2200
MR_CONTROL = 2200

## ThreatLevel
TL_BFF = 0
TL_FRIEND = 1
TL_NEUTRAL = 2
TL_DANGEROUS = 3
TL_PRIORITY = 4

####################
# Global variables #
####################

round_timer = 0 
monsters = []
opp_heroes = []

####################
# Helper functions #
####################

def debug(s: str) -> None:
    print(s, file=sys.stderr, flush=True)

##################
# helper classes #
##################

class Point():

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
    
    def getDistFrom(self, p) -> float:
        return math.dist((self.x, self.y),(p.x, p.y))
    
    def add(self, p) :
        return Point(self.x + p.x, self.y + p.y)

class Base():

    def __init__(self, x: int, y: int):
        self.p = Point(x, y)
        self.protectors_idle_spots = \
            [Point(6000, 2500), Point(2500, 6000), Point(5300, 3200)] \
            if x == 0 else \
            [Point(9500, 7100), Point(11350, 4800), Point(15130, 3000)]
        self.assassin_idle_spot = \
            Point(15500, 3500) if x == 0 else Point(1850, 6000)
        self.eb = Point(17630, 9000) if x == 0 else Point(0, 0)

    def get_protector_idle_spot(self, i: int) -> Point:
        global heroes_per_player
        return self.protectors_idle_spots[i % heroes_per_player]

base : Base = Base(base_x, base_y)

###################
# monster classes #
###################


class Monster():
    
    def __init__(self, _id: int, x: int, y: int, shield_life: int, is_controlled: int, health: int, vx: int, vy: int, near_base: int, threat_for: int):
        global base
        
        self.id, self.shield_life, self.is_controlled, self.health, self.vx, self.vy, self.near_base, self.threat_for = \
            _id, shield_life, is_controlled, health, vx, vy, near_base, threat_for
        
        self.p = Point(x, y)
        self.dist_from_base = self.p.getDistFrom(base.p)
        self.threat_level = threat_for + 2 if near_base == 0 else 2 * threat_for + 2
        self.next_pos = self.p.add(Point(vx, vy))

        debug(f"ID {self.id}, TL {self.threat_level}, DFB {int(self.dist_from_base)}, VX {self.vx}, VY {self.vy}")

        # variable that will be set later
        self.threat = 0
        self.attacked = 0 # Number of heros targeting the monster
        self.heros_needed = 1 #Number of heros needed to kill the monster
        self.need_more = True

        self.update_heros_needed()


    def update_need_more(self) -> None:
        # TODO : Take enemy WIND into possibility
        if self.shield_life:
            self.need_more = self.heros_needed > self.attacked
        
        # TODO : Do not waste mana on useless wind

        # With wind, only one hero is enough to protect
        self.need_more = self.attacked == 0


    def update_attacked(self) -> None:
        self.attacked += 1
        debug(f"MONSTER {self.id} is now attacked by {self.attacked} Heros")
        self.update_need_more()
    
    # True if more Heros need to 
    def update_heros_needed(self) -> None:

        if self.threat_level == TL_PRIORITY:
            # TODO Should be put in itit for more opti
            nb_steps_from_base = math.ceil(self.dist_from_base / 400)
            nb_hits_needed = self.health / 2

            self.heros_needed =  math.ceil((nb_hits_needed / nb_steps_from_base))
    
        debug(f"MONSTER {self.id} need {self.heros_needed} heros to be killed")

    def should_be_wind(self, hero):
        global MR_WIND
        global round_timer

        return self.p.getDistFrom(hero.p) <= MR_WIND \
            and self.shield_life == 0 \
            and self.dist_from_base < 5000 \
            and self.need_more # if can be killed without, why waste


#################
# heros classes #
#################

class Hero(ABC):
    """Basic hero class"""

    def __init__(self, _id: int, x: int, y: int, shield_life: int, is_controlled: int):
        global base

        self.id, self.shield_life, self.is_controlled = _id, shield_life, is_controlled
        self.p = Point(x, y)
        self.dist_from_base = self.p.getDistFrom(base.p)
        self.name = ""

    @abstractmethod
    def choose_action(self) -> str:
        pass

    def move(self, p: Point) -> str:
        return f'MOVE {p.x} {p.y}'

    def move_on_monster(self, m: Monster) -> str:
        m.update_attacked()
        # TODO : Improve by moving to the shortest way 
        return self.move(m.next_pos)
    
    def wind(self, p: Point) -> str:
        global my_mana
        my_mana -= 10
        return f'SPELL WIND {p.x} {p.y}'


class Protector(Hero):
    """Hero version that protect my base
    
    Can use :
        - WIND
        - CONTROL (TODO)
        - SHIELD ? (TODO)
    """

    def __init__(self, _id: int, x: int, y: int, shield_life: int, is_controlled: int):
        global base
        super().__init__(_id, x, y, shield_life, is_controlled)
        self.idle_point: Point = base.get_protector_idle_spot(self.id)
        self.name = f"P"

        # TODO : add defensives mesures if opponent around
        # TODO : add a way to find if he has been controlled or wind
    
    def choose_action(self) -> str:
        # Global variables used
        global monsters
        global round_timer
        global my_mana
        global base

        target = None

        monster_to_target = [monster for monster in monsters if monster.need_more]

        if monster_to_target:
            target = monster_to_target[0]
        elif monsters:
            target = monsters[0]
        
        if target:
            if my_mana > 10:
                if target.should_be_wind(self):
                    return self.wind(base.eb)
            return self.move_on_monster(target)
        
        return self.move(self.idle_point)


class Assassin(Hero):
    """Hero version that attack enemy base
    
    Can use :
        - WIND (TODO)
        - CONTROL (TODO)
        - SHIELD ? (TODO)
    """

    def __init__(self, _id: int, x: int, y: int, shield_life: int, is_controlled: int):
        global base
        super().__init__(_id, x, y, shield_life, is_controlled)
        self.idle_point: Point = base.assassin_idle_spot
        self.name = f"A"
    
    # TODO : implement the real version of the assassin. ATM is the same as Protector.
    def choose_action(self) -> str:
        # Global variables used
        global monsters
        global round_timer
        global my_mana
        global base

        target = None

        monster_to_target = [monster for monster in monsters if monster.need_more]

        if monster_to_target:
            target = monster_to_target[0]
        elif monsters:
            target = monsters[0]
        
        if target:
            if my_mana > 10:
                if target.should_be_wind(self):
                    return self.wind(base.eb)
            return self.move_on_monster(target)
        
        return self.move(self.idle_point)

class Opponent(Hero):
    """Ennemy hero"""

    def __init__(self, _id: int, x: int, y: int, shield_life: int, is_controlled: int):
        super().__init__(_id, x, y, shield_life, is_controlled)
        self.name = f"O"

    def choose_action(self) -> str:
        return ""
    
    def set_controlled(self) -> None:
        self.is_controlled = True


#############
# Game loop #
#############

heroes_mapping = [Protector, Protector, Protector]

while True:
    for i in range(2):

        # Assassin is useless in early game, better have an other farmer / protector
        if round_timer > 60:
            heroes_mapping = [Protector, Protector, Assassin]

        # health: Your base health
        # mana: Ignore in the first league; Spend ten mana to cast a spell
        my_health, my_mana = [int(j) for j in input().split()]
        enemy_health, enemy_mana = [int(j) for j in input().split()]
        entity_count = int(input())  # Amount of heros and monsters you can see
        
        monsters = []
        my_heroes = []
        opp_heroes = []
    
        for i in range(entity_count):
            # _id: Unique identifier
            # _type: 0=monster, 1=your hero, 2=opponent hero
            # x,y: Position of this entity
            # shield_life: Ignore for this league; Count down until shield spell fades
            # is_controlled: Ignore for this league; Equals 1 when this entity is under a control spell
            # health: Remaining health of this monster
            # vx,vy: Trajectory of this monster
            # near_base: 0=monster with no target yet, 1=monster targeting a base
            # threat_for: Given this monster's trajectory, is it a threat to 1=your base, 2=your opponent's base, 0=neither
            _id, _type, x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for = [int(j) for j in input().split()]

            # Changing threat_for 2 -> -1
            threat_for = -1 if threat_for == 2 else threat_for
            
            if _type == TYPE_MONSTER:
                debug("##### Monsters :")
                monsters.append(Monster( _id, x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for))
            # TODO : have an assassin class
            # TODO : be able to switch classes depending on timer
            elif _type == TYPE_MY_HERO:
                my_heroes.append(heroes_mapping[_id % heroes_per_player](_id, x, y, shield_life, is_controlled))
            elif _type == TYPE_OP_HERO:
                opp_heroes.append(Opponent(_id, x, y, shield_life, is_controlled))

        monsters.sort(key=lambda monster: monster.dist_from_base)

        for i in range(heroes_per_player):

            hero: Hero = my_heroes[i]
            debug(f"##### Hero {hero.id} :")

            action: str = hero.choose_action()
            print(action + f" {hero.name}")

        # Affecting globals variables
        round_timer += 1    
    
