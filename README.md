# CS200 - Data Structures & Algorithms (Project 1)
## USGS Earthquakes Explorer & DSA Algorithm Analyzer

This project fulfills all guidelines of **CS200 Project 1** using the official, free, open **USGS Earthquake API** (No API keys required).

---

## 📋 Features Checklist (Rubrics Compliance)

| Requirement | Implementation Details |
|---|---|
| **Domain** | USGS Earthquakes (Real-world scientific geophysical data) |
| **Count of Entities** | **15,000+ unique records** fetched via pagination (`offset` & `limit`) |
| **Scraper Controls** | **Start, Pause, Resume, Stop** using clean `QThread` |
| **Progress Bar** | Shows live count and progress from 0 to 15,000 |
| **Bonus Feature** | UI allows custom **API URL input** |
| **Attributes (9 total)** | `id`, `place`, `magnitude`, `time`, `depth`, `latitude`, `longitude`, `significance`, `status` |
| **UI Framework** | Lightweight, clean **PyQt5** single-window dashboard |
| **Sorting Algorithms (11)** | **Core Lab Algorithms:** `bubbleSort`, `insertionSort`, `selectionSort`, `mergeSort` (+ `hybridMerge`), `quickSort` (+ `partition`), `countingSort`, `radixSort` (+ `countingSortByDigit`), `bucketSort`<br>**Additional Algorithms:** `heapSort` (+ `heapify`), `shellSort` |
| **Sorting Metrics** | Time in **milliseconds**, number of **comparisons**, number of **swaps** |
| **Algorithm Labels** | **Time Complexity** ($O(n^2)$, $O(n \log n)$, $O(n + k)$, $O(d(n+k))$, $O(n^{1.5})$) and **Stability** (Yes/No) |
| **Benchmark Mode** | "Benchmark" button runs all 11 algorithms side-by-side with comparison table |
| **Sort Scope** | Sort either **Full Dataset** or **Current Filtered Results** |
| **Searching Algorithms** | **Linear Search** and **Binary Search** |
| **Advanced String Filters** | `contains`, `starts_with`, `ends_with`, `equals` (+ numeric `>` and `<`) |
| **Multi-Level Sorting** | Primary Column + Secondary Column with independent Asc/Desc order |
| **Multi-Column Searching**| Composite filters supporting **AND**, **OR**, and **NOT** |
| **Pagination & Display Tracker** | Full pagination controls (`First`, `Prev`, `Next`, `Last`, `Go to Page`, `Page Size: 500/1000/2000/5000`) and live indicator showing currently displayed records vs. total dataset (15,000). Ensures smooth GUI rendering without lag. |

---

## 🚀 How to Run

1. Open PowerShell or Command Prompt in the project folder:
   ```bash
   python main.py
   ```
2. The UI will open immediately.
3. The dataset (`earthquakes.json` with 15,000 rows) is already included, so you can test all sorting and searching instantly!
4. You can also press **Start Scraping** to demonstrate real live API calls, **Pause**, **Resume**, and **Stop** buttons to your instructor.

---

## 🎓 Teacher Evaluation Cheat Sheet (How to Rewrite if Deleted)

If your teacher deletes the code and asks you to write it from scratch, remember these simple templates:

### 1. The Helper Comparison Function (`shouldSwap`)
```python
def shouldSwap(row1, row2, col=None, ascending=True):
    v1 = row1.get(col, 0) if isinstance(row1, dict) else row1
    v2 = row2.get(col, 0) if isinstance(row2, dict) else row2
    return v1 > v2 if ascending else v1 < v2
```

### 2. Bubble Sort (`bubbleSort`)
```python
def bubbleSort(arr, start, end):
    total_elements = end - start + 1
    for i in range(total_elements - 1):
        swap = False
        for j in range(start, end - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swap = True
        if swap == False:
            break
    return arr
```

### 3. Selection Sort (`selectionSort`)
```python
def selectionSort(arr, start, end):
    for i in range(start, end):
        min_idx = i
        for j in range(i + 1, end + 1):
            if arr[min_idx] > arr[j]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
```

### 4. Insertion Sort (`insertionSort`)
```python
def insertionSort(arr, start, end):
    for i in range(start + 1, end + 1):
        key = arr[i]
        j = i - 1
        while j >= start and key < arr[j]:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
```

### 5. Merge Sort & Merge (`mergeSort`, `Merge`)
```python
def mergeSort(arr, start, end):
    if start < end:
        mid = (start + end) // 2
        mergeSort(arr, start, mid)
        mergeSort(arr, mid + 1, end)
        Merge(arr, start, mid, end)

def Merge(arr, p, q, r):
    left = arr[p : q + 1]
    right = arr[q + 1 : r + 1]
    i = 0
    j = 0
    k = p
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            arr[k] = left[i]
            i += 1
        else:
            arr[k] = right[j]
            j += 1
        k += 1
    while i < len(left):
        arr[k] = left[i]
        i += 1
        k += 1
    while j < len(right):
        arr[k] = right[j]
        j += 1
        k += 1
```

### 6. Quick Sort (`quickSort`, `partition`)
```python
def partition(A, low, high):
    x = A[high]
    i = low - 1
    for j in range(low, high):
        if A[j] < x:
            i += 1
            A[i], A[j] = A[j], A[i]
    A[i + 1], A[high] = A[high], A[i + 1]
    return i + 1

def quicksort(A, low, high):
    if low < high:
        q = partition(A, low, high)
        quicksort(A, low, q - 1)
        quicksort(A, q + 1, high)
```

### 7. Counting Sort (`countingSort`)
```python
def countingSort(A):
    if len(A) == 0:
        return A
    M = max(A)
    count_array = [0] * (M + 1)
    output_array = [0] * len(A)
    for x in A:
        count_array[x] += 1
    for i in range(1, M + 1):
        count_array[i] += count_array[i - 1]
    for j in range(len(A) - 1, -1, -1):
        value = A[j]
        target_idx = count_array[value] - 1
        output_array[target_idx] = value
        count_array[value] -= 1
    return output_array
```

### 8. Binary Search (`binarySearch`)
```python
def binarySearch(arr, col, target):
    low = 0
    high = len(arr) - 1
    comparisons = 0
    while low <= high:
        comparisons += 1
        mid = (low + high) // 2
        mid_val = arr[mid][col]
        if mid_val == target:
            return arr[mid], comparisons
        elif mid_val < target:
            low = mid + 1
        else:
            high = mid - 1
    return None, comparisons
```

### 6. Pause / Resume / Stop in Thread
```python
while self.is_running:
    while self.is_paused:
        time.sleep(0.2)
    if not self.is_running:
        break
    # fetch next batch from API
```
