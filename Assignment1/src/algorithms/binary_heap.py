"""
Binary heap implementation for the open list in A* search.
"""

from typing import List, Tuple, Any


class BinaryHeap:
    """
    A binary min-heap implementation using a list.
    Elements are (priority, unique_id, data) tuples where priority determines ordering.
    """
    
    def __init__(self):
        self.heap: List[Tuple[float, int, Any]] = []
        self._id_counter = 0
        self._position = {}  # Map from unique_id to position in heap
    
    def _parent(self, i: int) -> int:
        return (i - 1) // 2
    
    def _left_child(self, i: int) -> int:
        return 2 * i + 1
    
    def _right_child(self, i: int) -> int:
        return 2 * i + 2
    
    def _swap(self, i: int, j: int):
        """Swap elements at positions i and j."""
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
        # Update position map
        _, id1, _ = self.heap[i]
        _, id2, _ = self.heap[j]
        self._position[id1] = i
        self._position[id2] = j
    
    def _bubble_up(self, i: int):
        """Move element up the heap to maintain heap property."""
        while i > 0 and self.heap[i][0] < self.heap[self._parent(i)][0]:
            self._swap(i, self._parent(i))
            i = self._parent(i)
    
    def _bubble_down(self, i: int):
        """Move element down the heap to maintain heap property."""
        while True:
            smallest = i
            left = self._left_child(i)
            right = self._right_child(i)
            
            if left < len(self.heap) and self.heap[left][0] < self.heap[smallest][0]:
                smallest = left
            
            if right < len(self.heap) and self.heap[right][0] < self.heap[smallest][0]:
                smallest = right
            
            if smallest == i:
                break
            
            self._swap(i, smallest)
            i = smallest
    
    def insert(self, priority: float, data: Any) -> int:
        """
        Insert an element with given priority.
        Returns a unique ID for updating the element later.
        """
        unique_id = self._id_counter
        self._id_counter += 1
        
        idx = len(self.heap)
        self.heap.append((priority, unique_id, data))
        self._position[unique_id] = idx
        self._bubble_up(idx)
        
        return unique_id
    
    def extract_min(self) -> Tuple[float, Any]:
        """Remove and return the element with minimum priority."""
        if not self.heap:
            raise IndexError("extract_min from empty heap")
        
        priority, unique_id, data = self.heap[0]
        del self._position[unique_id]
        
        if len(self.heap) > 1:
            self.heap[0] = self.heap[-1]
            _, id_moved, _ = self.heap[0]
            self._position[id_moved] = 0
            self._bubble_down(0)
        
        self.heap.pop()
        
        return priority, data
    
    def update(self, unique_id: int, new_priority: float):
        """Update the priority of an element."""
        if unique_id not in self._position:
            raise KeyError(f"Element with id {unique_id} not in heap")
        
        i = self._position[unique_id]
        old_priority = self.heap[i][0]
        
        # Replace the element
        _, uid, data = self.heap[i]
        self.heap[i] = (new_priority, uid, data)
        
        if new_priority < old_priority:
            self._bubble_up(i)
        else:
            self._bubble_down(i)
    
    def is_empty(self) -> bool:
        """Check if the heap is empty."""
        return len(self.heap) == 0
    
    def __len__(self) -> int:
        return len(self.heap)
    
    def contains(self, unique_id: int) -> bool:
        """Check if element with given unique_id is in the heap."""
        return unique_id in self._position
