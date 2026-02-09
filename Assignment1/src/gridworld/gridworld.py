"""
Gridworld environment for the pathfinding assignment.
"""

import numpy as np
from typing import Tuple, Set, List
import random


class Cell:
    """Represents a cell in the gridworld."""
    def __init__(self, x: int, y: int, is_blocked: bool = False):
        self.x = x
        self.y = y
        self.is_blocked = is_blocked
    
    def __eq__(self, other):
        if isinstance(other, Cell):
            return self.x == other.x and self.y == other.y
        return False
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def __repr__(self):
        return f"Cell({self.x}, {self.y})"


class Gridworld:
    """
    Represents a gridworld for pathfinding experiments.
    Cells are represented using (x, y) coordinates where x is column and y is row.
    """
    
    def __init__(self, width: int, height: int):
        """Initialize a gridworld of given dimensions."""
        self.width = width
        self.height = height
        # Grid[y][x] to match standard matrix indexing
        self.grid = np.zeros((height, width), dtype=bool)  # False = unblocked, True = blocked
    
    def set_blocked(self, x: int, y: int, blocked: bool = True):
        """Set a cell's blocked status."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y, x] = blocked
    
    def is_blocked(self, x: int, y: int) -> bool:
        """Check if a cell is blocked."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return True  # Out of bounds is treated as blocked
        return self.grid[y, x]
    
    def is_valid(self, x: int, y: int) -> bool:
        """Check if a cell is valid (within bounds and unblocked)."""
        return 0 <= x < self.width and 0 <= y < self.height and not self.is_blocked(x, y)
    
    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get valid unblocked neighbors (4-directional: N, S, E, W)."""
        neighbors = []
        # Order: East, South, West, North
        for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            nx, ny = x + dx, y + dy
            if self.is_valid(nx, ny):
                neighbors.append((nx, ny))
        return neighbors
    
    def manhattan_distance(self, x1: int, y1: int, x2: int, y2: int) -> int:
        """Calculate Manhattan distance between two cells."""
        return abs(x1 - x2) + abs(y1 - y2)
    
    def copy(self) -> 'Gridworld':
        """Create a copy of this gridworld."""
        copy = Gridworld(self.width, self.height)
        copy.grid = self.grid.copy()
        return copy


class GridworldGenerator:
    """Generate gridworlds using depth-first search maze generation."""
    
    @staticmethod
    def generate_maze(width: int, height: int, blocked_prob: float = 0.3, seed: int = None) -> Gridworld:
        """
        Generate a maze-like gridworld using depth-first search.
        
        Args:
            width: Width of the gridworld
            height: Height of the gridworld
            blocked_prob: Probability of marking a cell as blocked (default 0.3)
            seed: Random seed for reproducibility
        
        Returns:
            A Gridworld object with the generated maze
        """
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        gridworld = Gridworld(width, height)
        
        # Initially all cells are unblocked, we'll mark some as blocked
        gridworld.grid = np.zeros((height, width), dtype=bool)
        
        # Track visited cells
        visited = set()
        stack = []
        
        # Start from a random cell
        start_x = random.randint(0, width - 1)
        start_y = random.randint(0, height - 1)
        
        stack.append((start_x, start_y))
        visited.add((start_x, start_y))
        
        while stack or len(visited) < width * height:
            if not stack:
                # Find an unvisited cell to restart
                for y in range(height):
                    for x in range(width):
                        if (x, y) not in visited:
                            stack.append((x, y))
                            visited.add((x, y))
                            break
                    if stack:
                        break
            
            if not stack:
                break
            
            x, y = stack[-1]
            
            # Get unvisited neighbors (4-directional)
            unvisited_neighbors = []
            for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                    unvisited_neighbors.append((nx, ny))
            
            if unvisited_neighbors:
                # Choose a random unvisited neighbor
                nx, ny = random.choice(unvisited_neighbors)
                
                # With 30% probability mark as blocked, 70% mark as unblocked and continue
                if random.random() < blocked_prob:
                    gridworld.set_blocked(nx, ny, True)
                else:
                    gridworld.set_blocked(nx, ny, False)
                    stack.append((nx, ny))
                
                visited.add((nx, ny))
            else:
                # Backtrack
                stack.pop()
        
        return gridworld


def load_gridworld(filepath: str) -> Gridworld:
    """Load a gridworld from a numpy file."""
    grid = np.load(filepath)
    gridworld = Gridworld(grid.shape[1], grid.shape[0])
    gridworld.grid = grid
    return gridworld


def save_gridworld(gridworld: Gridworld, filepath: str):
    """Save a gridworld to a numpy file."""
    np.save(filepath, gridworld.grid)
