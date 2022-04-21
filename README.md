# Codingame challenge of spring 2022
My current solution for this challenge.

This code use Python 3.9.12
Current league : Bois 1 (added fog of war + a repusilv spell)

TODO :
- Create 3 class for each behaviour :
  - Protector :
    - Stay at base, can use wind to push monsters
  - Assassin :
    - Try to push monsters that are a threat for the enemy
  - Farmer :
    - Current behaviour. Focus the nearest threat.
- Have Assassin and Protector explore fog of war ASAP.
