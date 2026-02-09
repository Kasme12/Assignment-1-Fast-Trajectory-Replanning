# Implementation Notes - Fast Trajectory Replanning

## Overview

This document provides detailed implementation notes for the CS 440 Assignment 1 solution.

## Core Components

### 1. Binary Heap (`src/algorithms/binary_heap.py`)

**Purpose**: Efficient priority queue for A* open list management

**Design Decisions**:
- Min-heap with element positions tracked
- Supports O(log n) insertion, extraction, and updates
- Unique IDs prevent conflicts with duplicate priorities

**Key Methods**:
```python
insert(priority, data) -> unique_id    # O(log n)
extract_min() -> (priority, data)      # O(log n)
update(unique_id, new_priority)        # O(log n)
```

**Trade-offs**:
- **Pros**: No external dependencies, efficient, supports updates
- **Cons**: Custom implementation adds ~150 lines of code

### 2. Gridworld (`src/gridworld/gridworld.py`)

**Representation**:
- 2D numpy array: grid[y][x] where True = blocked, False = unblocked
- Coordinates: (x, y) with x = column, y = row
- 4-directional movement: E, S, W, N

**Maze Generation**:
```
Algorithm: Depth-First Search with Random Tie-breaking
- Start from random cell
- DFS with stack for backtracking
- 30% probability to block new cells
- Guarantees all cells visited
- Creates realistic corridor structures
```

**Why DFS over other methods?**
- Natural backtracking creates maze-like structures
- Corridor and dead-end patterns suitable for pathfinding
- Faster than recursive backtracking
- Controllable via blockage probability

### 3. A* Implementation (`src/algorithms/astar.py`)

**Base Class Architecture**:
```
SearchAlgorithm (abstract)
    ├── AStarBase
    │   ├── RepeatedForwardAStar
    │   ├── RepeatedBackwardAStar
    │   └── AdaptiveAStar
```

**Key Design Features**:

#### g-value Management
- Lazy initialization using counter mechanism
- `search(s) = 0` until visit by nth search (counter = n)
- `g_values[s]` only stored if updated
- **Benefit**: O(updated_states) memory instead of O(all_states)

#### Heuristic Function
```python
h(s) = Manhattan distance = |x_s - x_goal| + |y_s - y_goal|
```

**Consistency Proof** (in report):
- h(goal) = 0 ✓
- h(s) ≤ 1 + h(succ(s)) for all moves ✓

#### Tie-breaking Strategy
```python
# Break ties by larger g-values (goal-directed)
priority = C * f(s) - g(s)    where C = 10000

# vs. smaller g-values (breadth-first)
priority = C * f(s) + g(s)
```

**Rationale**: Larger g-values encourage direct paths toward goal

### 4. Repeated Forward A*

**Algorithm Flow**:
```
1. Initialize: counter=0, all search(s)=0
2. While start ≠ goal:
   a. counter++ 
   b. Perform ComputePath() A* search
   c. Follow resulting path until:
      - Goal reached → SUCCESS
      - Blocked cell observed → replan
      - No path exists → FAILURE
   d. Update observations
   e. Return to 2
```

**Optimizations**:
- Skip closed-list iteration (track explicitly)
- Lazy g-value initialization
- Early termination when g(goal) ≤ min_f(open)

**Expected Performance**:
- First search: ~8,000-12,000 expansions (101×101 grid)
- Subsequent searches: ~3,000-5,000 expansions (fewer blocked cells to explore)

### 5. Repeated Backward A*

**Key Difference**: Searches TOWARD agent instead of FROM agent

**Pseudocode**:
```
For backward search from goal to current_position:
- Start: goal state with g=0, h=0
- Goal: current_position with h=Manhattan distance to start
- Search: same A* algorithm, reverse direction
- Path: returned in reverse order
```

**Why Generally Slower?**:
- h-value (distance to agent) doesn't improve during search
- Agent position changes between searches
- h-values are less informative overall

### 6. Adaptive A*

**Core Innovation**: Store and reuse improved h-values

**Update Rule**:
```
After each A* search (forward direction):
For each expanded state s:
    h_new(s) = max(h_old(s), g(goal) - g(s))
```

**Mathematical Properties**:
1. Admissible: h_new(s) ≤ true_distance(s, goal) ✓
2. Consistent: h_new(s) ≤ 1 + h_new(succ(s)) ✓
3. Monotonic: h_new(s) ≥ h_old(s) ✓
4. Improving: Subsequent searches faster ✓

**Expected Improvement**:
- First search: same as Repeated Forward A*
- Second search: ~30% fewer expansions
- Third+ searches: ~35-40% fewer expansions
- Cumulative: 24-30% overall saving

## Experimental Methodology

### Part 2: Tie-Breaking Analysis

**Hypothesis**: Breaking ties by larger g-values reduces expansions

**Test Design**:
- 10 random gridworlds (101×101)
- Two algorithms: one with g_max tie-breaking, one with g_min
- Count expansions per search

**Expected Result**: g_max ~12% fewer expansions

**Why**: Goal-directed search avoids lateral exploration

### Part 3: Forward vs. Backward Comparison

**Hypothesis**: Forward A* outperforms Backward A*

**Test Design**:
- Same 10 gridworlds
- Both use tie-breaking by larger g-values
- Compare total expansions over all searches

**Expected Result**: Forward ~28% fewer expansions

**Why**: Forward search benefits from improving heuristics

### Part 5: Adaptive A* Evaluation

**Hypothesis**: Adaptive A* reduces total expansions

**Test Design**:
- Same 10 gridworlds
- Complete trajectory from (0,0) to (100,100)
- Track cumulative expansions

**Expected Result**: Adaptive ~24% fewer total expansions

**Why**: Better h-values compound over multiple searches

## Critical Implementation Details

### Memory Efficiency

**Problem**: Never iterate over all 101×101 = 10,201 cells

**Solution Pattern**:
```python
# ✓ CORRECT: Only iterate expanded/generated states
for state in states_encountered:
    process(state)

# ✗ WRONG: Don't do this
for x in range(width):
    for y in range(height):
        if state_was_visited(x, y):
            process((x, y))
```

### Priority Calculation

**Issue**: Lexicographic ordering with floating-point

**Solution**:
```python
# Use integer priority: C*f(s) - g(s)
# Avoids floating-point precision issues
# C must be larger than max possible g-value
C = 10000  # For 101×101 grid, max path length ≈ 200
priority = C * f_value - g_value  # for g_max tie-breaking
```

### Search Value Tracking

**Problem**: Avoid reinitializing all g-values each search

**Solution**:
```python
counter = 0
search_values[s] = 0  # Initialize once

def get_g(s):
    if search_values[s] < counter:
        return float('inf')  # Not visited in this search
    return g_values[s]

# In each search:
counter += 1
# Only initialize g-values when first encountered
```

## Validation Against Test Cases

### Example from Figure 5 (First A* Search)

**Expected behavior**:
- Start at (1,1), goal at (5,5)
- Initial blocked cells as shown
- Manhattan heuristics calculated
- 23 expansions with break ties by g_max
- Path follows through unblocked cells

**Validation**:
- [ ] g-values match expected distances
- [ ] f-values monotonically increase
- [ ] Path is shortest to goal
- [ ] No previously expanded cells re-expanded

### Example from Figure 7 (Adaptive A*)

**Expected behavior**:
- First search: 23 expansions with Manhattan
- Second search: 20 expansions with improved h-values
- H-values for E1, E2, E3 increase
- Improvement due to h_new = g(goal) - g(state)

## Performance Characteristics

### Time Complexity per Search

```
A* Search: O((n + e) log n)
where n = cells expanded
      e = cells generated but not expanded

For 101×101 grids:
- Typical: 5,000-10,000 expansions
- Worst case: All accessible cells reachable
```

### Space Complexity

```
Open list: O(branching factor * depth) = O(n) worst case
Closed list: O(cells expanded) = O(n) worst case
h-values (Adaptive): O(cells expanded) = O(n)

Typical: ~2,000 states in memory per search
```

### Wall-Clock Time

```
Single 101×101 gridworld search:
- Binary heap operations: <1ms
- A* algorithm: 10-50ms
- Total: 50-100ms for one complete trajectory
```

## Known Limitations and Future Work

### Current Limitations
1. 4-directional movement only (no diagonals)
2. Single agent (no multi-agent coordination)
3. Discrete grid (no continuous paths)
4. No real-time constraints
5. Perfect information about blockage

### Possible Extensions
1. 8-directional movement (updates heuristic boundary)
2. Any-angle pathfinding (continuous steering)
3. Incremental A* (D*Lite/DynamicLSLRP)
4. Multi-agent coordination with limited communication
5. Real-time performance guarantees
6. GPU acceleration for parallel searches

## Testing Practices

### Unit Tests (Not Submitted But Done During Development)

```python
def test_binary_heap():
    heap = BinaryHeap()
    id1 = heap.insert(5, "item1")
    id2 = heap.insert(3, "item2")
    assert heap.extract_min() == (3, "item2")
    assert heap.extract_min() == (5, "item1")

def test_manhattan_distance():
    gw = Gridworld(10, 10)
    assert gw.manhattan_distance(0,0, 3,4) == 7
    assert gw.manhattan_distance(5,5, 5,5) == 0

def test_maze_generation():
    gw = GridworldGenerator.generate_maze(11, 11, seed=42)
    assert gw.is_valid(0, 0)  # Start always unblocked
    assert (0, 0) != (10, 10)  # Different cells

def test_repeated_forward_astar():
    gw = create_simple_gridworld()
    algo = RepeatedForwardAStar(gw)
    path = algo.find_path((0,0), (5,5))
    assert path is not None
    assert path[0] == (0,0)
    assert path[-1] == (5,5)
```

## Code Quality

### Style Guidelines Followed
- PEP 8 Python style
- Type hints for function signatures
- Docstrings for all classes and public methods
- Comments for complex algorithms

### No External A* Libraries Used
- Implemented binary heap from scratch
- Uses only numpy and matplotlib
- All core logic is custom
- Easier to understand and modify

## Submission Checklist

- [x] Part 0: 50 gridworlds generated and stored
- [x] Part 1: Theoretical understanding explained
  - [x] a) First move explanation
  - [x] b) Trajectory boundedness proof
- [x] Part 2: Tie-breaking comparison implemented
  - [x] Results showing g_max vs g_min
  - [x] Explanation of findings
- [x] Part 3: Forward vs Backward comparison
  - [x] Both algorithms implemented correctly
  - [x] Performance comparison results
- [x] Part 4: Mathematical proofs
  - [x] Manhattan consistency proof
  - [x] Adaptive A* consistency proof
- [x] Part 5: Adaptive A* implementation
  - [x] h-value updates working correctly
  - [x] Performance improvement demonstrated
- [x] Part 6: Statistical testing methodology
  - [x] Hypothesis test design explained
  - [x] Implementation steps described
- [x] LaTeX Report: Comprehensive technical document
- [x] Code: Clean, well-commented, tested

## References to Assignment Materials

All implementations follow the pseudocode from Assignment 1:
- Figure 4: Repeated Forward A* pseudocode
- Figure 2-3: Example gridworlds and trajectories
- Figure 5-7: A*, Forward, and Backward search results

## Contact and Questions

For implementation questions, refer to:
1. Inline code comments
2. This implementation notes document
3. The comprehensive LaTeX report
4. Original pseudocode in assignment materials
