#adventure.py

import random

LEVELS = [
    {"name":"Level 1 — Starter", "type":"score", "initial_blocks":3, "target_score":120},
    {"name":"Level 2 — Time Attack", "type":"timer", "initial_blocks":4, "time_limit":25, "target_score":180},
    {"name":"Level 3 — Shape Match", "type":"match", "initial_blocks":5, "shape_required":[(0,0),(1,0),(0,1),(1,1)]}
]

def apply_initial_blocks_to_grid(grid, count):
    attempts = 0
    filled = 0
    while filled < count and attempts < count * 50:
        x = random.randint(0, grid.size-1)
        y = random.randint(0, grid.size-1)
        if grid.cells[y][x] == grid.EMPTY:
            color = (random.randint(120,200), random.randint(100,190), random.randint(140,220))
            grid.cells[y][x] = color
            filled += 1
        attempts += 1

def start_level(level, grid):
    grid.clear_all()
    apply_initial_blocks_to_grid(grid, level.get("initial_blocks",0))
    mode = level["type"]
    state = {"mode":mode,"name":level.get("name","Level"),"score":0}
    if mode=="score":
        state["target"] = level.get("target_score",100)
    elif mode=="timer":
        state["timer"] = float(level.get("time_limit",30))
        state["target"] = level.get("target_score",150)
    elif mode=="match":
        shape = level.get("shape_required",[])
        state["shape_required"] = [(int(a),int(b)) for a,b in shape]
        state["completed"] = False
    return state
