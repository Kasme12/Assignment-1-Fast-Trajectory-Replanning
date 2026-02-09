#!/usr/bin/env python
"""Minimal test to debug Part 5 issue."""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.gridworld.gridworld import GridworldGenerator, load_gridworld
from src.algorithms.astar import RepeatedForwardAStar, AdaptiveAStar
import time

def main():
    print("Testing Part 5 - Adaptive A*...")
    
    # Load just 3 gridworlds for quick test
    for i in range(3):
        try:
            filepath = f"data/gridworlds/gridworld_{i:03d}.npy"
            if not os.path.exists(filepath):
                print(f"Gridworld {i} not found at {filepath}")
                continue
                
            gw = load_gridworld(filepath)
            start = (0, 0)
            goal = (gw.width - 1, gw.height - 1)
            
            print(f"\nGridworld {i}:")
            print(f"  Grid size: {gw.width}x{gw.height}")
            
            # Test Forward A*
            print(f"  Testing Forward A*... ", end="", flush=True)
            start_time = time.time()
            algo_f = RepeatedForwardAStar(gw, tie_break_g_max=True)
            path_f = algo_f.find_path(start, goal)
            time_f = time.time() - start_time
            print(f"Done ({algo_f.expansions} expansions, {time_f:.3f}s)")
            
            # Test Adaptive A*
            print(f"  Testing Adaptive A*... ", end="", flush=True)
            start_time = time.time()
            algo_a = AdaptiveAStar(gw, tie_break_g_max=True)
            path_a = algo_a.find_path(start, goal)
            time_a = time.time() - start_time
            print(f"Done ({algo_a.expansions} expansions, {time_a:.3f}s)")
            
            improvement = (algo_f.expansions - algo_a.expansions) / max(1, algo_f.expansions) * 100
            print(f"  Improvement: {improvement:+.1f}%")
            
        except Exception as e:
            print(f"\n✗ Error on gridworld {i}: {e}")
            import traceback
            traceback.print_exc()
            break
    
    print("\n✓ Test completed!")

if __name__ == "__main__":
    main()
