# OPSYS_algo

OPSYS_algo is a Windows desktop operating-systems simulator built with Python and
PySide6. It provides interactive visualizations for CPU scheduling, memory
management, paging, page replacement, disk scheduling, and resource allocation.

## Requirements

- Windows 10 or later
- Python 3.10 or later
- PowerShell

## Installation and instructions

From the repository root, enter the simulator directory and create a virtual
environment:

```powershell
cd .\OS-Simulator
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
python -m pip install -r .\requirements.txt
```

Start the application:

```powershell
python .\main.py
```

The dashboard opens with one button for each simulator. Select a module, enter
its input values, then choose **Calculate**, **Start Simulation**, or
**Step-by-Step**, depending on the module. Use **Reset** or **Back to
Dashboard** to return to the module list.

If the virtual environment is not activated, use its executables directly:

```powershell
.\.venv\Scripts\python.exe .\main.py
.\.venv\Scripts\pyside6-designer.exe .\main_window.ui
```

To edit the Qt Designer form:

```powershell
.\.venv\Scripts\pyside6-designer.exe .\main_window.ui
```

## Build a standalone Windows executable

Install PyInstaller into the virtual environment:

```powershell
python -m pip install pyinstaller
```

Build a single windowed executable from the `OS-Simulator` directory:

```powershell
pyinstaller --clean --noconfirm --onefile --windowed `
  --name OS-Simulator `
  --icon .\app_icon.ico `
  --add-data ".\fonts;fonts" `
  --add-data ".\app_icon.ico;." `
  --add-data ".\app_icon.png;." `
  .\main.py
```

The result is `.\dist\OS-Simulator.exe`. The `--add-data` options include the
application icons and bundled Nunito fonts required by the interface.

## Headless dataset tests

The file [`tests/run_dataset_tests.py`](C:/Users/loisa/OneDrive/Documents/GitHub/OPSYS_algo/OS-Simulator/tests/run_dataset_tests.py)
runs repeatable checks for every simulator module without opening the GUI. It
tests both normal-sized and substantially larger datasets and exits with a
non-zero status if any check fails.

From the `OS-Simulator` directory, activate the virtual environment first:

```powershell
.\.venv\Scripts\Activate.ps1
```

Run both the small and large datasets for every module:

```powershell
python .\tests\run_dataset_tests.py --dataset all
```

Run only the smaller datasets:

```powershell
python .\tests\run_dataset_tests.py --dataset small
```

Run only the larger datasets:

```powershell
python .\tests\run_dataset_tests.py --dataset large
```

The large tests use deterministic generated data, so repeated runs can be
compared reliably. They cover 100 CPU processes, 50 Banker's Algorithm
processes, 10,000 page references, 1,000 disk requests, 50 fragmentation
processes, 1,000 multiprogramming jobs, and 1,000 segments.

To test one module at both sizes, add `--module`:

```powershell
python .\tests\run_dataset_tests.py --dataset all --module paging
python .\tests\run_dataset_tests.py --dataset all --module page-replacement
python .\tests\run_dataset_tests.py --dataset all --module disk
```

Available module names are:

```text
cpu
bankers
paging
page-replacement
disk
fragmentation
multiprogramming
segmentation
```

Typical successful output looks like:

```text
[PASS] paging (small): 7 pages; address 500 translated to 756
[PASS] paging (large): 245 pages; address 999999 translated to 410175
```

The same tests can be run with the PowerShell wrapper:

```powershell
.\tests\run_dataset_tests.ps1 -Dataset all
.\tests\run_dataset_tests.ps1 -Dataset large -Module cpu
```

## Algorithms and simulator modules

### CPU scheduling

Input rows contain a process ID, arrival time, burst time, and (for priority
scheduling) a priority value. The simulator reports the execution timeline,
completion time, waiting time, turnaround time, and averages.

- **FCFS (First-Come, First-Served):** runs ready processes in arrival order.
- **SJF (Shortest Job First):** non-preemptively selects the ready process with
  the smallest burst time.
- **Priority:** non-preemptively selects the ready process with the smallest
  numeric priority.
- **Round Robin:** gives each ready process a fixed time quantum and requeues
  unfinished processes.

Sample input:

```text
Algorithm: FCFS
P1: arrival=0, burst=5
P2: arrival=1, burst=3
P3: arrival=2, burst=2
```

Sample output:

```text
Schedule: P1 [0-5], P2 [5-8], P3 [8-10]
Average waiting time: 3.33
Average turnaround time: 6.67
```

### Banker's Algorithm

The resource-allocation simulator checks whether the current allocation is
safe. For each process, it computes `Need = Maximum - Allocation`, then finds a
process whose remaining need can be satisfied by the available work. Its
resources are released and the process is added to the safe sequence. The
result is either a safe sequence or an unsafe-state warning.

Sample input:

```text
Available: [3, 3, 2]
P0 Allocation: [0, 1, 0]  Maximum: [7, 5, 3]
P1 Allocation: [2, 0, 0]  Maximum: [3, 2, 2]
P2 Allocation: [3, 0, 2]  Maximum: [9, 0, 2]
P3 Allocation: [2, 1, 1]  Maximum: [2, 2, 2]
P4 Allocation: [0, 0, 2]  Maximum: [4, 3, 3]
```

Sample output:

```text
Need(P1): [1, 2, 2]
System state: SAFE
One safe sequence: P1 -> P3 -> P4 -> P0 -> P2
```

### Paging

Paging divides a process into fixed-size pages and physical memory into frames.
The simulator calculates the page count, frame count, unused memory, and
translates a logical address using:

```text
page = logical_address // page_size
offset = logical_address % page_size
physical_address = frame * page_size + offset
```

Sample input:

```text
Process size: 1700 bytes
Page size: 256 bytes
Physical memory: 1024 bytes
Logical address: 500
Page 1 is assigned to frame 2
```

Sample output:

```text
Pages: 7
Frames: 4
Unused physical memory: 0 bytes
Logical address 500 -> page 1, offset 244
Physical address: 756
```

### Page replacement

Enter a page-reference string and a number of frames. The simulator records
each frame state, identifies hits and faults, and reports total faults, hits,
and fault rate.

- **FIFO:** replaces the page that has been in memory the longest.
- **LRU:** replaces the page that has not been used for the longest time.
- **Optimal:** replaces the page whose next use is farthest in the future.

Sample input:

```text
Reference string: 1 2 3 1 4 2
Frames: 3
Algorithm: FIFO
```

Sample output:

```text
Page faults: 5
Page hits: 1
Fault rate: 83.33%
```

### Disk scheduling

Enter the initial head position, disk size, and track requests. The simulator
shows the seek sequence, movement for every step, total head movement, and
average seek distance.

- **FCFS:** services requests in input order.
- **SSTF:** services the request closest to the current head.
- **SCAN:** moves like an elevator to a disk boundary, then reverses.
- **C-SCAN:** moves in one direction, wraps at the boundaries, and continues.
- **LOOK / C-LOOK:** variants of SCAN / C-SCAN that stop at the last request
  instead of the physical boundary.

Sample input:

```text
Algorithm: FCFS
Initial head: 50
Requests: 82, 170, 43, 140
```

Sample output:

```text
Seek sequence: 50 -> 82 -> 170 -> 43 -> 140
Total head movement: 367 cylinders
Average seek distance: 91.75 cylinders
```

### Fragmentation and partition allocation

The fragmentation simulator supports fixed or variable partitions and compares
three placement methods:

- **First Fit:** allocates to the first free region large enough.
- **Best Fit:** allocates to the smallest suitable free region.
- **Worst Fit:** allocates to the largest suitable free region.

It visualizes each allocation and reports allocated memory, remaining memory,
internal fragmentation, external fragmentation, and the largest free region.

Sample input:

```text
Partition mode: Variable Partitions
Method: Best Fit
Memory blocks: 100, 500, 200
Process requests: 180, 90, 300
```

Sample output:

```text
180 -> 200-byte region
90 -> 100-byte region
300 -> 500-byte region
Remaining free memory: 130 bytes
```

### Multiprogramming

This simulator admits jobs when both available RAM and the maximum degree of
multiprogramming allow them. It reports the job timeline, memory use, average
degree of multiprogramming, completion time, waiting and turnaround times, and
theoretical CPU utilization:

```text
CPU utilization = (1 - p^n) * 100
```

where `p` is the I/O wait ratio and `n` is the current degree of
multiprogramming.

Sample input:

```text
Total RAM: 1000 KB
OS reserved: 200 KB
Maximum DOM: 2
I/O wait ratio: 0.5
J1: arrival=0, size=300 KB, burst=4
J2: arrival=1, size=400 KB, burst=3
```

Sample output:

```text
Available to jobs: 800 KB
At DOM=2: CPU utilization = 75.00%
Total simulated time: 4
Completed jobs: J1, J2
```

### Segmentation

Segmentation stores a base and limit for each segment. A logical address
`(segment, offset)` is valid only when the segment exists and
`offset < limit`; valid addresses translate to `base + offset`. Overlapping
segments and out-of-range offsets are rejected.

Sample input:

```text
Segment 0: base=1000, limit=400
Segment number: 0
Offset: 120
```

Sample output:

```text
Valid translation
Physical address = 1000 + 120 = 1120
```

An offset of `400` for the same segment produces a segmentation fault because
the valid offsets are `0` through `399`.

## Project layout

```text
OS-Simulator/
  main.py                 Application entry point
  algorithms/             Algorithm implementations
  module/                 PySide6 simulator windows
  fonts/                  Bundled application fonts
  *.ui                    Qt Designer forms
  requirements.txt        Python dependencies
```