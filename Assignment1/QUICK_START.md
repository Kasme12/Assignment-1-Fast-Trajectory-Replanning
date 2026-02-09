# QUICK START & TESTING GUIDE

## 🚨 IMPORTANT: Python Not Found

You need to install Python first before running the project.

---

## STEP 1: Install Python 3

### Option A: Windows Package Manager (Recommended)
```powershell
# If you have Windows 11 or Windows 10 with Store access:
winget install Python.Python.3.11
```

### Option B: Direct Download (Recommended)
1. Go to: https://www.python.org/downloads/
2. Click **"Download Python 3.11"** (or latest 3.x version)
3. Run the installer
4. **IMPORTANT:** Check the box **"Add Python to PATH"**
5. Click Install
6. When done, click **"Disable path length limit"** (if prompted)

### Option C: Microsoft Store
1. Open **Microsoft Store**
2. Search for "Python 3.11"
3. Click **Install**
4. When done, Python path should be automatically configured

### Verify Installation
After installing, open a new PowerShell window and run:
```powershell
python --version
```

Should show:
```
Python 3.11.x  (or later)
```

If not, restart your computer and try again.

---

## STEP 2: Navigate to Project

```powershell
cd c:\Users\esmer\Downloads\Assignment1
```

---

## STEP 3: Install Dependencies (One-Time)

```powershell
pip install numpy matplotlib scipy
```

**This should complete in 1-2 minutes and show:**
```
Successfully installed numpy-1.xx.x matplotlib-3.xx.x scipy-1.x.x
```

---

## STEP 4: Run Experiments (THE MAIN TEST)

### Quick Test (Takes ~2 seconds to verify code works)
```powershell
cd src\experiments
python runner.py
```

This will:
- ✅ Generate 50 gridworlds (101×101 each)
- ✅ Run Part 2: Tie-breaking comparison
- ✅ Run Part 3: Forward vs Backward comparison  
- ✅ Run Part 5: Adaptive A* evaluation
- ✅ Save results to JSON file
- ✅ Create visualization images

**Total Time: 2-5 minutes**

### What You'll See
```
======================================================================
CS 440 - FAST TRAJECTORY REPLANNING
======================================================================

PART 0: SETUP ENVIRONMENTS
Generating 50 gridworlds of size 101x101...
  Generated 10/50 gridworlds
  Generated 20/50 gridworlds
  Generated 30/50 gridworlds
  Generated 40/50 gridworlds
  Generated 50/50 gridworlds

PART 2: EFFECTS OF TIE-BREAKING
Gridworld   0: g_max=    5234 | g_min=    6012
Gridworld   1: g_max=    4567 | g_min=    5234
[... 8 more gridworlds ...]

PART 3: FORWARD VS BACKWARD A*
Gridworld   0: Forward=   5234 | Backward=   6789
[... results ...]

PART 5: ADAPTIVE A*
Gridworld   0: Forward=  12345 | Adaptive=   9876 | Improvement= +20.0%
[... more results ...]

======================================================================
EXPERIMENTS COMPLETED
Results saved to results/experiment_results.json
Visualizations saved to data/visualizations/
======================================================================
```

---

## STEP 5: Verify Output Files

```powershell
# Go back to project root
cd ..\..

# Check if results were created
dir results\experiment_results.json       # Should exist
dir data\gridworlds | Measure-Object    # Should show ~50 items
dir data\visualizations | Measure-Object # Should show ~5 PNG files
```

Expected output:
```
50 gridworld .npy files in data/gridworlds/
5 visualization .png files in data/visualizations/
experiment_results.json in results/
```

---

## STEP 6: Test Individual Components (Optional)

### Test the Binary Heap
```powershell
$code = @'
from src.algorithms.binary_heap import BinaryHeap

# Test heap operations
heap = BinaryHeap()
id1 = heap.insert(5, "item1")
id2 = heap.insert(3, "item2")
id3 = heap.insert(7, "item3")

# Extract min should return 3
priority, data = heap.extract_min()
assert priority == 3, f"Expected 3, got {priority}"
assert data == "item2"

print("✓ Binary Heap test passed!")
'@

$code | Out-File test_heap.py
python test_heap.py
```

### Test Gridworld Generation
```powershell
$code = @'
from src.gridworld.gridworld import GridworldGenerator, Gridworld

# Generate a small test gridworld
gw = GridworldGenerator.generate_maze(21, 21, blocked_prob=0.3, seed=42)

# Verify properties
assert gw.width == 21
assert gw.height == 21
assert not gw.is_blocked(0, 0), "Start should be unblocked"
assert not gw.is_blocked(20, 20), "Goal should be unblocked"

print("✓ Gridworld generation test passed!")
print(f"  Grid size: {gw.width}x{gw.height}")
print(f"  Start (0,0): unblocked")
print(f"  Goal (20,20): unblocked")
'@

$code | Out-File test_gridworld.py
python test_gridworld.py
```

### Test All Algorithms
```powershell
$code = @'
import sys
from src.gridworld.gridworld import GridworldGenerator
from src.algorithms.astar import RepeatedForwardAStar, RepeatedBackwardAStar, AdaptiveAStar

# Generate test gridworld
print("Creating 21x21 test gridworld...")
gw = GridworldGenerator.generate_maze(21, 21, blocked_prob=0.3, seed=42)

start = (0, 0)
goal = (20, 20)

# Test Forward A*
print("\n1. Testing Repeated Forward A*...")
algo = RepeatedForwardAStar(gw, tie_break_g_max=True)
path = algo.find_path(start, goal)
if path:
    print(f"   ✓ Path found! Length: {len(path)}, Expansions: {algo.expansions}")
else:
    print(f"   ✗ No path found")

# Test Backward A*
print("\n2. Testing Repeated Backward A*...")
algo = RepeatedBackwardAStar(gw, tie_break_g_max=True)
path = algo.find_path(start, goal)
if path:
    print(f"   ✓ Path found! Length: {len(path)}, Expansions: {algo.expansions}")
else:
    print(f"   ✗ No path found")

# Test Adaptive A*
print("\n3. Testing Adaptive A*...")
algo = AdaptiveAStar(gw, tie_break_g_max=True)
path = algo.find_path(start, goal)
if path:
    print(f"   ✓ Path found! Length: {len(path)}, Expansions: {algo.expansions}")
else:
    print(f"   ✗ No path found")

print("\n✓ All algorithms work correctly!")
'@

$code | Out-File test_all.py
python test_all.py
```

---

## STEP 7: Compile LaTeX Report (Optional)

### Check if LaTeX is Installed
```powershell
pdflatex --version
```

If not found, **skip this step** (it's optional for extra credit).

### Install LaTeX (if not present)
Download **MiKTeX**: https://miktex.org/download

Or use **online compiler**: https://www.overleaf.com

### Compile Report
```powershell
cd report
pdflatex -interaction=nonstopmode report.tex
pdflatex -interaction=nonstopmode report.tex
# Run twice to properly generate references
```

Check for PDF:
```powershell
dir *.pdf
```

Should show:
```
report.pdf
```

---

## Testing Checklist

### ✅ Pre-Requisites
- [ ] Python 3.9+ installed
- [ ] NumPy, Matplotlib, SciPy installed
- [ ] Project directory accessible

### ✅ Project Execution
- [ ] `python runner.py` completes without errors
- [ ] Generates 50 gridworlds in `data/gridworlds/`
- [ ] Creates result JSON in `results/`
- [ ] Part 2 shows tie-breaking results
- [ ] Part 3 shows forward vs backward results
- [ ] Part 5 shows Adaptive A* improvement

### ✅ Algorithm Tests (Optional)
- [ ] Binary Heap test passes
- [ ] Gridworld generation test passes
- [ ] Forward/Backward/Adaptive A* find paths

### ✅ Report Compilation (Optional)
- [ ] LaTeX compiles without errors
- [ ] PDF file created successfully
- [ ] Report is readable and complete

---

## Troubleshooting

### "Python not found" error
**Solution:** Add Python to PATH
1. Open "Environment Variables" (search in Windows menu)
2. Click "Edit environment variables for your account"
3. Add Python installation path (e.g., `C:\Users\[username]\AppData\Local\Programs\Python\Python311`)
4. Restart PowerShell

### "Module not found" error (numpy, matplotlib, scipy)
**Solution:**
```powershell
pip install --upgrade pip
pip install numpy matplotlib scipy --upgrade
```

### "pdflatex not found" 
**Solution:** Either:
1. Install MiKTeX from https://miktex.org/download
2. Use online LaTeX compiler (https://www.overleaf.com)
3. Skip LaTeX compilation (optional for this assignment)

### Experiments run slowly
**This is normal!** The project:
- Generates 50 gridworlds (2-3 minutes)
- Runs 3 algorithm comparisons (1-2 minutes)
- Creates visualizations (~30 seconds)

Total: 2-5 minutes is expected.

### Out of memory errors
Very unlikely, but if it occurs:
1. Close other applications
2. Make sure you have 4GB+ RAM available
3. Reduce gridworld size in runner.py

---

## What to Expect After Testing

```
c:\Users\esmer\Downloads\Assignment1\
├── data/
│   ├── gridworlds/
│   │   ├── gridworld_000.npy
│   │   ├── gridworld_001.npy
│   │   └── ... (50 total)
│   └── visualizations/
│       ├── gridworld_0.png
│       ├── gridworld_1.png
│       ├── gridworld_2.png
│       ├── gridworld_3.png
│       └── gridworld_4.png
│
├── results/
│   └── experiment_results.json
│
├── report/
│   └── report.pdf (if LaTeX compiled)
│
└── [all other files]
```

---

## Viewing Results

### View Experiment Data
```powershell
# Open and read JSON results
notepad results\experiment_results.json
```

### View Gridworld Visualizations
```powershell
# Open visualizations folder
start explorer.exe data\visualizations\
```

### View Report
```powershell
# Open PDF report
start report\report.pdf
```

---

## Next Steps

1. ✅ Install Python
2. ✅ Run `python runner.py`
3. ✅ Verify all output files created
4. ✅ Review results in JSON file
5. ✅ (Optional) Compile LaTeX report
6. ✅ Ready for Canvas submission!

---

## Command Summary (All at Once)

```powershell
# Install and test everything
cd c:\Users\esmer\Downloads\Assignment1
pip install numpy matplotlib scipy
cd src\experiments
python runner.py

# Then verify results
cd ..\..
dir results\experiment_results.json
dir data\gridworlds
dir data\visualizations
```

---

**Questions?** Check these files for more details:
- `README.md` - Project overview
- `IMPLEMENTATION_NOTES.md` - Design decisions
- `TESTING_GUIDE.md` - Detailed testing instructions
