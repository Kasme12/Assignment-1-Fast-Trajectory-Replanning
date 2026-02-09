import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

print(f"Project root: {project_root}")
print(f"Python version: {sys.version}")
print(f"sys.path[0]: {sys.path[0]}")

try:
    from src.gridworld.gridworld import Gridworld, GridworldGenerator
    print("✓ Gridworld imports OK")
except Exception as e:
    print(f"✗ Gridworld import failed: {e}")

try:
    from src.algorithms.astar import RepeatedForwardAStar, RepeatedBackwardAStar, AdaptiveAStar
    print("✓ A* imports OK")
except Exception as e:
    print(f"✗ A* import failed: {e}")

try:
    from src.visualization.visualizer import GridworldVisualizer, ExperimentAnalyzer
    print("✓ Visualization imports OK")
except Exception as e:
    print(f"✗ Visualization import failed: {e}")

print("\nAll imports successful!")

# Try quick algorithm test
try:
    gw = GridworldGenerator.generate_maze(21, 21, blocked_prob=0.3, seed=0)
    print(f"\n✓ Generated 21x21 gridworld: {gw.width}x{gw.height}")
    
    algo = RepeatedForwardAStar(gw)
    print("✓ Created RepeatedForwardAStar instance")
    
    algo_a = AdaptiveAStar(gw)
    print("✓ Created AdaptiveAStar instance")
    
    print("\n✅ All tests passed!")
except Exception as e:
    print(f"\n✗ Algorithm test failed: {e}")
    import traceback
    traceback.print_exc()
