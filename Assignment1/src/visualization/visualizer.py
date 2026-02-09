"""
Visualization and analysis tools for gridworld experiments.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Dict, Tuple, List, Optional, Set
import os


class GridworldVisualizer:
    """Visualize gridworlds and pathfinding results."""
    
    @staticmethod
    def visualize_gridworld(gridworld, title: str = "Gridworld", save_path: str = None):
        """Visualize a gridworld (black = blocked, white = unblocked)."""
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # Create image: 1 = blocked (white), 0 = unblocked (black)
        img = 1 - gridworld.grid.astype(int)
        
        ax.imshow(img, cmap='gray', origin='upper')
        ax.set_title(title)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        
        plt.tight_layout()
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        
        plt.close()
    
    @staticmethod
    def visualize_path(gridworld, path: List[Tuple[int, int]], start: Tuple[int, int],
                       goal: Tuple[int, int], title: str = "Path", save_path: str = None):
        """Visualize a path on the gridworld."""
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # Create image
        img = 1 - gridworld.grid.astype(int)
        ax.imshow(img, cmap='gray', origin='upper')
        
        # Draw path
        if path and len(path) > 1:
            xs = [p[0] for p in path]
            ys = [p[1] for p in path]
            ax.plot(xs, ys, 'b-', linewidth=2, label='Path')
        
        # Mark start and goal
        ax.plot(start[0], start[1], 'go', markersize=10, label='Start')
        ax.plot(goal[0], goal[1], 'r*', markersize=15, label='Goal')
        
        ax.set_title(title)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.legend()
        
        plt.tight_layout()
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        
        plt.close()
    
    @staticmethod
    def visualize_agent_knowledge(gridworld, observations: Dict[Tuple[int, int], bool],
                                  agent_pos: Tuple[int, int], title: str = "Agent Knowledge",
                                  save_path: str = None):
        """
        Visualize what the agent knows about the gridworld.
        White = observed unblocked
        Black = observed blocked
        Gray = unobserved
        """
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # Create visualization
        vis = np.ones((gridworld.height, gridworld.width)) * 0.5  # Gray for unknown
        
        for y in range(gridworld.height):
            for x in range(gridworld.width):
                if (x, y) in observations:
                    vis[y, x] = 1.0 if not observations[(x, y)] else 0.0
        
        ax.imshow(vis, cmap='gray', origin='upper', vmin=0, vmax=1)
        
        # Mark agent position
        ax.plot(agent_pos[0], agent_pos[1], 'bo', markersize=10, label='Agent')
        
        ax.set_title(title)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.legend()
        
        plt.tight_layout()
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        
        plt.close()


class ExperimentAnalyzer:
    """Analyze and compare search algorithm performance."""
    
    @staticmethod
    def compare_algorithms(results: Dict[str, Dict]) -> str:
        """
        Compare results from different algorithms.
        
        Args:
            results: Dict mapping algorithm names to result dictionaries
                    containing 'expansions', 'path_length' keys
        
        Returns:
            Formatted analysis string
        """
        output = []
        output.append("=" * 60)
        output.append("Algorithm Comparison")
        output.append("=" * 60)
        
        for algo_name, result in results.items():
            output.append(f"\n{algo_name}:")
            output.append(f"  Total Expansions: {result.get('expansions', 'N/A')}")
            output.append(f"  Path Length: {result.get('path_length', 'N/A')}")
            if 'runtime' in result:
                output.append(f"  Runtime: {result['runtime']:.4f}s")
        
        # Calculate improvements
        if len(results) > 1:
            algo_names = list(results.keys())
            baseline = results[algo_names[0]]['expansions']
            
            output.append("\n" + "=" * 60)
            output.append("Improvement over " + algo_names[0])
            output.append("=" * 60)
            
            for algo_name in algo_names[1:]:
                reduction = (baseline - results[algo_name]['expansions']) / baseline * 100
                output.append(f"\n{algo_name}: {reduction:+.1f}% reduction in expansions")
        
        return "\n".join(output)
    
    @staticmethod
    def generate_statistics(results_list: List[Dict]) -> Dict:
        """
        Generate statistics from a list of results.
        
        Args:
            results_list: List of result dictionaries
        
        Returns:
            Dictionary with statistics
        """
        expansions = [r['expansions'] for r in results_list]
        path_lengths = [r['path_length'] for r in results_list]
        
        return {
            'mean_expansions': np.mean(expansions),
            'std_expansions': np.std(expansions),
            'min_expansions': np.min(expansions),
            'max_expansions': np.max(expansions),
            'mean_path_length': np.mean(path_lengths),
            'std_path_length': np.std(path_lengths),
        }
