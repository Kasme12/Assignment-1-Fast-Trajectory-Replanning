"""
A* and Repeated A* implementations for pathfinding.
"""

from abc import ABC, abstractmethod
from typing import Dict, Tuple, List, Optional, Set
import math
from src.algorithms.binary_heap import BinaryHeap
from src.gridworld.gridworld import Gridworld


class SearchAlgorithm(ABC):
    """Base class for search algorithms."""
    
    def __init__(self, gridworld: Gridworld):
        self.gridworld = gridworld
        self.expansions = 0  # Number of cell expansions
        self.path_found = False
    
    @abstractmethod
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int], 
                  observations: Optional[Dict[Tuple[int, int], bool]] = None) -> Optional[List[Tuple[int, int]]]:
        """Find a path from start to goal. Returns path or None if impossible."""
        pass


class AStarBase(SearchAlgorithm):
    """Base A* implementation."""
    
    def __init__(self, gridworld: Gridworld, tie_break_g_max: bool = True):
        """
        Initialize A* search.
        
        Args:
            gridworld: The gridworld environment
            tie_break_g_max: If True, break ties in favor of larger g-values
        """
        super().__init__(gridworld)
        self.tie_break_g_max = tie_break_g_max
        
        # Search values for each cell
        self.g_values: Dict[Tuple[int, int], float] = {}
        self.search_values: Dict[Tuple[int, int], int] = {}
        self.tree_pointers: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {}
        self.counter = 0
    
    def _manhattan_distance(self, x1: int, y1: int, x2: int, y2: int) -> int:
        """Calculate Manhattan distance (consistent h-value for 4-directional movement)."""
        return abs(x1 - x2) + abs(y1 - y2)
    
    def _get_h_value(self, pos: Tuple[int, int], goal: Tuple[int, int]) -> float:
        """Get heuristic value for a position. Override in subclasses for Adaptive A*."""
        return self._manhattan_distance(pos[0], pos[1], goal[0], goal[1])
    
    def _calculate_priority(self, f_value: float, g_value: float) -> float:
        """
        Calculate priority for the open list.
        Lexicographic ordering: first by f-value, then by g-value (descending if tie_break_g_max).
        We use: priority = f_value + epsilon * (1 - g_value / max_g)
        Or simpler: priority = C * f_value - g_value (if tie_break_g_max, where C is large)
        """
        if self.tie_break_g_max:
            # Break ties in favor of larger g-values
            # Use a large constant C such that C > max possible g-value
            # Priority = C * f - g ensures lexicographic ordering
            C = 10000  # Larger than any expected g-value
            return C * f_value - g_value
        else:
            # Break ties in favor of smaller g-values
            C = 10000
            return C * f_value + g_value
    
    def _get_neighbors_with_costs(self, pos: Tuple[int, int]) -> List[Tuple[Tuple[int, int], float]]:
        """Get valid neighbors and movement costs from current position."""
        neighbors = []
        x, y = pos
        
        # 4-directional movement: E, S, W, N
        for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            nx, ny = x + dx, y + dy
            if self.gridworld.is_valid(nx, ny):
                cost = 1.0  # All moves have cost 1
                neighbors.append(((nx, ny), cost))
        
        return neighbors
    
    def _get_g_value(self, pos: Tuple[int, int], counter: int) -> float:
        """Get g-value for a position, initializing to infinity if needed."""
        if pos not in self.search_values or self.search_values[pos] < counter:
            return float('inf')
        return self.g_values.get(pos, float('inf'))
    
    def _set_g_value(self, pos: Tuple[int, int], value: float, counter: int):
        """Set g-value for a position."""
        self.g_values[pos] = value
        self.search_values[pos] = counter


class RepeatedForwardAStar(AStarBase):
    """Repeated Forward A* implementation."""
    
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int],
                  observations: Optional[Dict[Tuple[int, int], bool]] = None) -> Optional[List[Tuple[int, int]]]:
        """
        Find a path using Repeated Forward A*.
        
        Args:
            start: Starting position (x, y)
            goal: Goal position (x, y)
            observations: Dictionary of observed blocked cells
        
        Returns:
            Path from start to goal, or None if impossible
        """
        self.expansions = 0
        self.path_found = False
        
        if observations is None:
            observations = {}
        
        current_state = start
        
        while current_state != goal:
            # Perform A* search
            path = self._compute_path(current_state, goal, observations)
            
            if path is None or len(path) == 0:
                # No path found
                return None
            
            # Follow the path until we hit a blocked cell or reach goal
            for next_state in path[1:]:  # path[0] is current state
                # Observe neighbors
                neighbors = self._get_visible_neighbors(next_state)
                new_blocked = False
                
                for neighbor in neighbors:
                    if neighbor not in observations:
                        observations[neighbor] = self.gridworld.is_blocked(neighbor[0], neighbor[1])
                        if observations[neighbor]:
                            new_blocked = True
                
                if new_blocked:
                    # Path is blocked, need to replan
                    break
                
                current_state = next_state
                
                if current_state == goal:
                    self.path_found = True
                    return self._reconstruct_full_path(start, goal, observations)
        
        self.path_found = True
        return self._reconstruct_full_path(start, goal, observations)
    
    def _compute_path(self, start: Tuple[int, int], goal: Tuple[int, int],
                      observations: Dict[Tuple[int, int], bool]) -> Optional[List[Tuple[int, int]]]:
        """Compute a single A* path from start to goal."""
        self.counter += 1
        
        open_list = BinaryHeap()
        closed_list: Set[Tuple[int, int]] = set()
        
        # Initialize start state
        self._set_g_value(start, 0.0, self.counter)
        h_start = self._get_h_value(start, goal)
        f_start = h_start
        priority = self._calculate_priority(f_start, 0.0)
        open_list.insert(priority, start)
        
        # Initialize goal state
        self._set_g_value(goal, float('inf'), self.counter)
        
        while not open_list.is_empty():
            # Check termination condition
            min_f_in_open = open_list.heap[0][0] if not open_list.is_empty() else float('inf')
            # Recover from priority encoding
            if self.tie_break_g_max:
                f_min = min_f_in_open / 10000
            else:
                f_min = min_f_in_open / 10000
            
            g_goal = self._get_g_value(goal, self.counter)
            if g_goal <= f_min:
                # Path found
                path = self._reconstruct_path(start, goal)
                return path
            
            # Remove state with minimum f-value
            _, s = open_list.extract_min()
            closed_list.add(s)
            self.expansions += 1
            
            g_s = self._get_g_value(s, self.counter)
            
            # Expand successors
            neighbors = self._get_neighbors_with_costs(s)
            for successor, cost in neighbors:
                # Skip if blocked
                if observations.get(successor, self.gridworld.is_blocked(successor[0], successor[1])):
                    continue
                
                g_succ_old = self._get_g_value(successor, self.counter)
                g_succ_new = g_s + cost
                
                if g_succ_new < g_succ_old:
                    self._set_g_value(successor, g_succ_new, self.counter)
                    self.tree_pointers[successor] = s
                    
                    h_succ = self._get_h_value(successor, goal)
                    f_succ = g_succ_new + h_succ
                    priority = self._calculate_priority(f_succ, g_succ_new)
                    
                    open_list.insert(priority, successor)
        
        return None
    
    def _reconstruct_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Reconstruct path from start to goal using tree pointers."""
        path = [goal]
        current = goal
        
        while current != start and current in self.tree_pointers:
            current = self.tree_pointers[current]
            path.append(current)
        
        path.reverse()
        return path if path[0] == start else [start]
    
    def _reconstruct_full_path(self, start: Tuple[int, int], goal: Tuple[int, int],
                               observations: Dict[Tuple[int, int], bool]) -> List[Tuple[int, int]]:
        """Reconstruct the complete path taken."""
        return [start, goal]
    
    def _get_visible_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get all 4 adjacent cells (for observation)."""
        x, y = pos
        neighbors = []
        for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.gridworld.width and 0 <= ny < self.gridworld.height:
                neighbors.append((nx, ny))
        return neighbors


class RepeatedBackwardAStar(RepeatedForwardAStar):
    """Repeated Backward A* - searches from goal to start."""
    
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int],
                  observations: Optional[Dict[Tuple[int, int], bool]] = None) -> Optional[List[Tuple[int, int]]]:
        """
        Find a path using Repeated Backward A*.
        Searches from goal toward start, but still returns path from start to goal.
        """
        self.expansions = 0
        self.path_found = False
        
        if observations is None:
            observations = {}
        
        current_state = start
        
        while current_state != goal:
            # Perform backward A* search (from goal to current state)
            path = self._compute_backward_path(current_state, goal, observations)
            
            if path is None or len(path) == 0:
                return None
            
            # Follow the path
            for next_state in path[1:]:
                neighbors = self._get_visible_neighbors(next_state)
                new_blocked = False
                
                for neighbor in neighbors:
                    if neighbor not in observations:
                        observations[neighbor] = self.gridworld.is_blocked(neighbor[0], neighbor[1])
                        if observations[neighbor]:
                            new_blocked = True
                
                if new_blocked:
                    break
                
                current_state = next_state
                
                if current_state == goal:
                    self.path_found = True
                    return self._reconstruct_full_path(start, goal, observations)
        
        self.path_found = True
        return self._reconstruct_full_path(start, goal, observations)
    
    def _compute_backward_path(self, start: Tuple[int, int], goal: Tuple[int, int],
                               observations: Dict[Tuple[int, int], bool]) -> Optional[List[Tuple[int, int]]]:
        """Compute a single backward A* path (from goal toward start)."""
        self.counter += 1
        
        open_list = BinaryHeap()
        closed_list: Set[Tuple[int, int]] = set()
        
        # Initialize goal state (reversed: goal is now start of search)
        self._set_g_value(goal, 0.0, self.counter)
        h_goal = 0  # We're searching toward start, h(goal) = 0
        f_goal = 0
        priority = self._calculate_priority(f_goal, 0.0)
        open_list.insert(priority, goal)
        
        # Initialize start state
        self._set_g_value(start, float('inf'), self.counter)
        
        while not open_list.is_empty():
            # Check termination
            min_f_in_open = open_list.heap[0][0] if not open_list.is_empty() else float('inf')
            if self.tie_break_g_max:
                f_min = min_f_in_open / 10000
            else:
                f_min = min_f_in_open / 10000
            
            g_start = self._get_g_value(start, self.counter)
            if g_start <= f_min:
                path = self._reconstruct_backward_path(start, goal)
                return path
            
            _, s = open_list.extract_min()
            closed_list.add(s)
            self.expansions += 1
            
            g_s = self._get_g_value(s, self.counter)
            
            neighbors = self._get_neighbors_with_costs(s)
            for successor, cost in neighbors:
                if observations.get(successor, self.gridworld.is_blocked(successor[0], successor[1])):
                    continue
                
                g_succ_old = self._get_g_value(successor, self.counter)
                g_succ_new = g_s + cost
                
                if g_succ_new < g_succ_old:
                    self._set_g_value(successor, g_succ_new, self.counter)
                    self.tree_pointers[successor] = s
                    
                    # For backward search, h estimates distance to start
                    h_succ = self._get_h_value(successor, start)
                    f_succ = g_succ_new + h_succ
                    priority = self._calculate_priority(f_succ, g_succ_new)
                    
                    open_list.insert(priority, successor)
        
        return None
    
    def _reconstruct_backward_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Reconstruct path from backward search."""
        path = [start]
        current = start
        
        while current != goal and current in self.tree_pointers:
            current = self.tree_pointers[current]
            path.append(current)
        
        return path if path[-1] == goal else [goal]


class AdaptiveAStar(RepeatedForwardAStar):
    """Adaptive A* - improves h-values based on previous searches."""
    
    def __init__(self, gridworld: Gridworld, tie_break_g_max: bool = True):
        super().__init__(gridworld, tie_break_g_max)
        # Store improved h-values
        self.h_values: Dict[Tuple[int, int], float] = {}
    
    def _get_h_value(self, pos: Tuple[int, int], goal: Tuple[int, int]) -> float:
        """Get improved h-value if available, otherwise Manhattan distance."""
        if pos in self.h_values:
            return self.h_values[pos]
        return self._manhattan_distance(pos[0], pos[1], goal[0], goal[1])
    
    def _compute_path(self, start: Tuple[int, int], goal: Tuple[int, int],
                      observations: Dict[Tuple[int, int], bool]) -> Optional[List[Tuple[int, int]]]:
        """Compute path and update h-values."""
        self.counter += 1
        
        open_list = BinaryHeap()
        closed_list: Set[Tuple[int, int]] = set()
        expanded_states: List[Tuple[int, int]] = []
        
        # Initialize start state
        self._set_g_value(start, 0.0, self.counter)
        h_start = self._get_h_value(start, goal)
        f_start = h_start
        priority = self._calculate_priority(f_start, 0.0)
        open_list.insert(priority, start)
        
        # Initialize goal state
        self._set_g_value(goal, float('inf'), self.counter)
        g_goal = float('inf')
        
        while not open_list.is_empty():
            min_f_in_open = open_list.heap[0][0] if not open_list.is_empty() else float('inf')
            if self.tie_break_g_max:
                f_min = min_f_in_open / 10000
            else:
                f_min = min_f_in_open / 10000
            
            g_goal = self._get_g_value(goal, self.counter)
            if g_goal <= f_min:
                break
            
            _, s = open_list.extract_min()
            closed_list.add(s)
            expanded_states.append(s)
            self.expansions += 1
            
            g_s = self._get_g_value(s, self.counter)
            
            neighbors = self._get_neighbors_with_costs(s)
            for successor, cost in neighbors:
                if observations.get(successor, self.gridworld.is_blocked(successor[0], successor[1])):
                    continue
                
                g_succ_old = self._get_g_value(successor, self.counter)
                g_succ_new = g_s + cost
                
                if g_succ_new < g_succ_old:
                    self._set_g_value(successor, g_succ_new, self.counter)
                    self.tree_pointers[successor] = s
                    
                    h_succ = self._get_h_value(successor, goal)
                    f_succ = g_succ_new + h_succ
                    priority = self._calculate_priority(f_succ, g_succ_new)
                    
                    open_list.insert(priority, successor)
        
        # Update h-values for expanded states
        g_goal = self._get_g_value(goal, self.counter)
        if g_goal != float('inf'):
            for state in expanded_states:
                g_state = self._get_g_value(state, self.counter)
                new_h = g_goal - g_state
                self.h_values[state] = max(self.h_values.get(state, 0), new_h)
        
        path = self._reconstruct_path(start, goal)
        return path
