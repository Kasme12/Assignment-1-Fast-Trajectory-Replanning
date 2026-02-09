#!/usr/bin/env python
"""Debug Adaptive A* on Gridworld 1 which causes hang."""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.gridworld.gridworld import GridworldGenerator
from src.algorithms.astar import RepeatedForwardAStar, AdaptiveAStar
import time

print("Testing Gridworld 1 issue...")

# Generate gridworld 1 (seed=1)
gw = GridworldGenerator.generate_maze(51, 51, blocked_prob=0.3, seed=1)
gw.set_blocked(0, 0, False)
gw.set_blocked(50, 50, False)

start = (0, 0)
goal = (50, 50)

print(f"Gridworld size: {gw.width}x{gw.height}")
print(f"Start: {start}, Goal: {goal}")

# Check if start and goal are directly adjacent
from src.algorithms.astar import AStarBase
base_algo = AStarBase(gw)
neighbors = base_algo._get_neighbors_with_costs(start)
print(f"Neighbors of start: {neighbors}")

if goal in [n[0] for n in neighbors]:
    print("✓ Goal is directly adjacent to start!")

# Test Forward A*
print("\nTesting Forward A*...")
algo_f = RepeatedForwardAStar(gw, tie_break_g_max=True)
start_time = time.time()
path_f = algo_f.find_path(start, goal)
time_f = time.time() - start_time
print(f"  Expansions: {algo_f.expansions}")
print(f"  Time: {time_f:.3f}s")
print(f"  Path: {path_f}")

# Test Adaptive A* with timeout
print("\nTesting Adaptive A* (with timeout)...")
algo_a = AdaptiveAStar(gw, tie_break_g_max=True)

import threading

result_container = {'path': None, 'time': None, 'expansions': None, 'done': False}

def run_adaptive():
    start_time = time.time()
    try:
        result_container['path'] = algo_a.find_path(start, goal)
        result_container['time'] = time.time() - start_time
        result_container['expansions'] = algo_a.expansions
        result_container['done'] = True
    except Exception as e:
        result_container['error'] = str(e)
        result_container['done'] = True

thread = threading.Thread(target=run_adaptive, daemon=True)
thread.start()
thread.join(timeout=10)

if not result_container['done']:
    print(f"  ✗ Adaptive A* timed out (>10 seconds)")
    print(f"  This indicates an infinite loop, likely in find_path replanning loop")
elif 'error' in result_container:
    print(f"  ✗ Error: {result_container['error']}")
else:
    path_a = result_container['path']
    time_a = result_container['time']
    print(f"  Expansions: {result_container['expansions']}")
    print(f"  Time: {time_a:.3f}s")
    print(f"  Path: {path_a}")
    
    improvement = (algo_f.expansions - result_container['expansions']) / max(1, algo_f.expansions) * 100
    print(f"  Improvement: {improvement:+.1f}%")
