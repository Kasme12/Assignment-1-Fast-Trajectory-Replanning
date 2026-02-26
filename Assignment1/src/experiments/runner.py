"""
Main experiment runner for the pathfinding assignment.
"""

import os
import sys
import json
import time
import random
import numpy as np
from typing import List, Dict, Tuple
import matplotlib.pyplot as plt

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.gridworld.gridworld import Gridworld, GridworldGenerator, save_gridworld, load_gridworld
from src.algorithms.astar import RepeatedForwardAStar, RepeatedBackwardAStar, AdaptiveAStar
from src.visualization.visualizer import GridworldVisualizer, ExperimentAnalyzer


def generate_test_gridworlds(num_gridworlds: int = 50, size: int = 101, output_dir: str = "data/gridworlds"):
    """Generate and save test gridworlds."""
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Generating {num_gridworlds} gridworlds of size {size}x{size}...")
    
    for i in range(num_gridworlds):
        # Generate with different seed for each
        gridworld = GridworldGenerator.generate_maze(size, size, blocked_prob=0.3, seed=i)
        
        # Ensure start and goal are unblocked
        gridworld.set_blocked(0, 0, False)
        gridworld.set_blocked(size-1, size-1, False)
        
        filepath = os.path.join(output_dir, f"gridworld_{i:03d}.npy")
        save_gridworld(gridworld, filepath)
        
        if (i + 1) % 10 == 0:
            print(f"  Generated {i + 1}/{num_gridworlds} gridworlds")
    
    print(f"Gridworlds saved to {output_dir}/")


def load_test_gridworlds(num_gridworlds: int = 50, input_dir: str = "data/gridworlds") -> List[Gridworld]:
    """Load test gridworlds."""
    gridworlds = []
    
    for i in range(num_gridworlds):
        filepath = os.path.join(input_dir, f"gridworld_{i:03d}.npy")
        try:
            gw = load_gridworld(filepath)
            gridworlds.append(gw)
        except FileNotFoundError:
            print(f"Warning: Could not load {filepath}")
    
    return gridworlds


def run_algorithm(algorithm, gridworld: Gridworld, start: Tuple[int, int], 
                  goal: Tuple[int, int]) -> Dict:
    """Run a single algorithm on a gridworld and return results."""
    start_time = time.time()
    
    result = algorithm.find_path(start, goal)
    
    elapsed = time.time() - start_time
    
    return {
        'expansions': algorithm.expansions,
        'path_found': algorithm.path_found,
        'path_length': len(result) if result else 0,
        'runtime': elapsed,
        'algorithm': type(algorithm).__name__
    }


def part0_setup_environments():
    """Part 0: Generate and visualize test gridworlds."""
    print("\n" + "="*70)
    print("PART 0: SETUP ENVIRONMENTS")
    print("="*70)
    
    generate_test_gridworlds(num_gridworlds=50, size=101)
    
    # Visualize a few sample gridworlds
    print("\nVisualizing sample gridworlds...")
    gridworlds = load_test_gridworlds(min(5, 50))
    
    for i, gw in enumerate(gridworlds):
        save_path = f"data/visualizations/gridworld_{i:03d}.png"
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        GridworldVisualizer.visualize_gridworld(gw, title=f"Gridworld {i}", save_path=save_path)
    
    print("Sample gridworld visualizations saved to data/visualizations/")



def part2_tie_breaking():
    """Part 2: Effects of tie-breaking."""
    print("\n" + "="*70)
    print("PART 2: EFFECTS OF TIE-BREAKING")
    print("="*70)
    
    # Load a subset of gridworlds (using first 5 for speed)
    gridworlds = load_test_gridworlds(5)
    
    results = {
        'tie_break_g_max': [],
        'tie_break_g_min': []
    }
    
    for i, gw in enumerate(gridworlds):
        start = (0, 0)
        goal = (gw.width - 1, gw.height - 1)
        
        # Forward A* with g_max
        algo1 = RepeatedForwardAStar(gw, tie_break_g_max=True)
        res1 = run_algorithm(algo1, gw, start, goal)
        results['tie_break_g_max'].append(res1)
        
        # Forward A* with g_min
        algo2 = RepeatedForwardAStar(gw, tie_break_g_max=False)
        res2 = run_algorithm(algo2, gw, start, goal)
        results['tie_break_g_min'].append(res2)
        
        print(f"Gridworld {i:3d}: g_max={res1['expansions']:5d} | g_min={res2['expansions']:5d}")
    
    stats_max = ExperimentAnalyzer.generate_statistics(results['tie_break_g_max'])
    stats_min = ExperimentAnalyzer.generate_statistics(results['tie_break_g_min'])
    
    print("\n" + ExperimentAnalyzer.compare_algorithms({
        'Forward A* (break ties by g_max)': {'expansions': stats_max['mean_expansions']},
        'Forward A* (break ties by g_min)': {'expansions': stats_min['mean_expansions']}
    }))
    
    print("\nObservation: Breaking ties in favor of larger g-values typically results")
    print("in fewer expansions because it prioritizes moving toward the goal.")
    
    return results


def part3_forward_vs_backward():
    """Part 3: Forward vs Backward A*."""
    print("\n" + "="*70)
    print("PART 3: FORWARD VS BACKWARD A*")
    print("="*70)
    
    gridworlds = load_test_gridworlds(5)
    
    results = {
        'forward': [],
        'backward': []
    }
    
    for i, gw in enumerate(gridworlds):
        start = (0, 0)
        goal = (gw.width - 1, gw.height - 1)
        
        # Forward A*
        algo_f = RepeatedForwardAStar(gw, tie_break_g_max=True)
        res_f = run_algorithm(algo_f, gw, start, goal)
        results['forward'].append(res_f)
        
        # Backward A*
        algo_b = RepeatedBackwardAStar(gw, tie_break_g_max=True)
        res_b = run_algorithm(algo_b, gw, start, goal)
        results['backward'].append(res_b)
        
        print(f"Gridworld {i:3d}: Forward={res_f['expansions']:5d} | Backward={res_b['expansions']:5d}")
    
    stats_f = ExperimentAnalyzer.generate_statistics(results['forward'])
    stats_b = ExperimentAnalyzer.generate_statistics(results['backward'])
    
    print("\n" + ExperimentAnalyzer.compare_algorithms({
        'Repeated Forward A*': {'expansions': stats_f['mean_expansions']},
        'Repeated Backward A*': {'expansions': stats_b['mean_expansions']}
    }))
    
    print("\nObservation: Forward A* typically explores fewer states because h-values")
    print("improve as we move toward the goal. Backward A* has less informed heuristics.")
    
    return results


def part5_adaptive_astar():
    """Part 5: Adaptive A*."""
    print("\n" + "="*70)
    print("PART 5: ADAPTIVE A*")
    print("="*70)
    sys.stdout.flush()
    
    gridworlds = load_test_gridworlds(5)
    
    results = {
        'forward': [],
        'adaptive': []
    }
    
    for i, gw in enumerate(gridworlds):
        sys.stdout.flush()
        start = (0, 0)
        goal = (gw.width - 1, gw.height - 1)
        
        # Repeated Forward A*
        algo_f = RepeatedForwardAStar(gw, tie_break_g_max=True)
        res_f = run_algorithm(algo_f, gw, start, goal)
        results['forward'].append(res_f)
        
        # Adaptive A*
        algo_a = AdaptiveAStar(gw, tie_break_g_max=True)
        res_a = run_algorithm(algo_a, gw, start, goal)
        results['adaptive'].append(res_a)
        
        total_exp_f = res_f['expansions']
        total_exp_a = res_a['expansions']
        improvement = (total_exp_f - total_exp_a) / max(1, total_exp_f) * 100 if total_exp_f > 0 else 0
        
        print(f"Gridworld {i:3d}: Forward={total_exp_f:6d} | Adaptive={total_exp_a:6d} | Improvement={improvement:+5.1f}%")
        sys.stdout.flush()
    
    stats_f = ExperimentAnalyzer.generate_statistics(results['forward'])
    stats_a = ExperimentAnalyzer.generate_statistics(results['adaptive'])
    
    print("\n" + ExperimentAnalyzer.compare_algorithms({
        'Repeated Forward A*': {'expansions': stats_f['mean_expansions']},
        'Adaptive A*': {'expansions': stats_a['mean_expansions']}
    }))
    
    print("\nObservation: Adaptive A* improves h-values after each search, making")
    print("subsequent searches more efficient by expanding fewer states.")
    
    return results


def main():
    """Run all experiments."""
    print("\n" + "="*70)
    print("CS 440 - FAST TRAJECTORY REPLANNING")
    print("Repeated A*, Adaptive A*, and Comparative Analysis")
    print("="*70)
    
    # Create output directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/visualizations", exist_ok=True)
    os.makedirs("results", exist_ok=True)
    
    # Part 0: Setup
    part0_setup_environments()
    

    # Part 2: Tie-breaking
    results_p2 = part2_tie_breaking()
    
    # Part 3: Forward vs Backward
    results_p3 = part3_forward_vs_backward()
    
    # Part 5: Adaptive A*
    print("\nRunning Part 5...", flush=True)
    results_p5 = part5_adaptive_astar()
    
    # Save results
    print("\nPreparing to save results...", flush=True)
    all_results = {
        'part2_tiebreaking': results_p2,
        'part3_forward_backward': results_p3,
        'part5_adaptive': results_p5
    }
    
    print("Converting results for JSON...", flush=True)
    with open("results/experiment_results.json", "w") as f:
        # Convert numpy types to Python types for JSON serialization
        json_results = {}
        for key, val in all_results.items():
            json_results[key] = {}
            for k, vals in val.items():
                json_results[key][k] = []
                for v in vals:
                    json_results[key][k].append({
                        'expansions': int(v['expansions']),
                        'path_length': int(v['path_length']),
                        'runtime': float(v['runtime']),
                        'algorithm': v['algorithm'],
                        'path_found': v['path_found']
                    })
        
        print("Writing JSON...", flush=True)
        json.dump(json_results, f, indent=2)
        print("JSON write complete.", flush=True)
    
    print("\n" + "="*70)
    print("EXPERIMENTS COMPLETED")
    print("Results saved to results/experiment_results.json")
    print("Visualizations saved to data/visualizations/")
    print("="*70)


if __name__ == "__main__":
    main()
