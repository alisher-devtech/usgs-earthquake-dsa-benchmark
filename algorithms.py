import sys
import time

sys.setrecursionlimit(50000)

def shouldSwap(r1, r2, col, ascending=True):
    v1, v2 = r1.get(col, 0) or 0, r2.get(col, 0) or 0
    return v1 > v2 if ascending else v1 < v2

def bubbleSort(arr, col, ascending=True):
    arr, n, comp, swap = list(arr), len(arr), 0, 0
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            comp += 1
            if shouldSwap(arr[j], arr[j + 1], col, ascending):
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swap += 1
                swapped = True
        if not swapped:
            break
    return arr, comp, swap

def selectionSort(arr, col, ascending=True):
    arr, n, comp, swap = list(arr), len(arr), 0, 0
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            comp += 1
            if shouldSwap(arr[min_idx], arr[j], col, ascending):
                min_idx = j
        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
            swap += 1
    return arr, comp, swap

def insertionSort(arr, col, ascending=True):
    arr, n, comp, swap = list(arr), len(arr), 0, 0
    for i in range(1, n):
        key = arr[i]
        j = i - 1
        while j >= 0:
            comp += 1
            if shouldSwap(arr[j], key, col, ascending):
                arr[j + 1] = arr[j]
                swap += 1
                j -= 1
            else:
                break
        arr[j + 1] = key
    return arr, comp, swap

def Merge(left, right, col, ascending, comp, swap):
    result, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        comp[0] += 1
        if not shouldSwap(left[i], right[j], col, ascending):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            swap[0] += 1
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

def mergeSort(arr, col, ascending=True):
    comp, swap = [0], [0]
    def sort(lst):
        if len(lst) <= 1:
            return lst
        mid = len(lst) // 2
        return Merge(sort(lst[:mid]), sort(lst[mid:]), col, ascending, comp, swap)
    return sort(list(arr)), comp[0], swap[0]

def partition(A, low, high, col, ascending, comp, swap):
    x, i = A[high], low - 1
    for j in range(low, high):
        comp[0] += 1
        if not shouldSwap(A[j], x, col, ascending):
            i += 1
            A[i], A[j] = A[j], A[i]
            swap[0] += 1
    A[i + 1], A[high] = A[high], A[i + 1]
    swap[0] += 1
    return i + 1

def quickSort(arr, col, ascending=True):
    A, comp, swap = list(arr), [0], [0]
    def sort(low, high):
        while low < high:
            q = partition(A, low, high, col, ascending, comp, swap)
            if q - low < high - q:
                sort(low, q - 1)
                low = q + 1
            else:
                sort(q + 1, high)
                high = q - 1
    sort(0, len(A) - 1)
    return A, comp[0], swap[0]

def countingSort(arr, col, ascending=True):
    A, n = list(arr), len(arr)
    if n <= 1:
        return A, 0, 0
    vals = [float(x.get(col, 0) or 0) for x in A]
    minVal, maxVal = min(vals), max(vals)
    span = maxVal - minVal
    scale = 10 if span <= 50 else (100000 / span if span > 100000 else 1)
    keys = [int(round((v - minVal) * scale)) for v in vals]
    M = max(keys)
    count_array = [0] * (M + 1)
    output_array = [None] * n
    for k in keys:
        count_array[k] += 1
    for i in range(1, M + 1):
        count_array[i] += count_array[i - 1]
    for j in range(n - 1, -1, -1):
        target_idx = count_array[keys[j]] - 1
        output_array[target_idx] = A[j]
        count_array[keys[j]] -= 1
    if not ascending:
        output_array.reverse()
    return output_array, n, n

def countingSortByDigit(A, units, swap):
    n = len(A)
    count_array = [0] * 10
    output_array = [None] * n
    for item, k in A:
        count_array[(k // units) % 10] += 1
    for i in range(1, 10):
        count_array[i] += count_array[i - 1]
    for j in range(n - 1, -1, -1):
        digit = (A[j][1] // units) % 10
        output_array[count_array[digit] - 1] = A[j]
        count_array[digit] -= 1
        swap[0] += 1
    for i in range(n):
        A[i] = output_array[i]

def radixSort(arr, col, ascending=True):
    A, n = list(arr), len(arr)
    if n <= 1:
        return A, 0, 0
    minVal = min(float(x.get(col, 0) or 0) for x in A)
    paired = [(x, int(round((float(x.get(col, 0) or 0) - minVal) * 100))) for x in A]
    M, units, swap = max(p[1] for p in paired), 1, [0]
    while M // units > 0:
        countingSortByDigit(paired, units, swap)
        units *= 10
    res = [p[0] for p in paired]
    if not ascending:
        res.reverse()
    return res, n * len(str(M)), swap[0]

def bucketSort(arr, col, ascending=True):
    A, n = list(arr), len(arr)
    if n <= 1:
        return A, 0, 0
    vals = [float(x.get(col, 0) or 0) for x in A]
    minVal, maxVal = min(vals), max(vals)
    span = (maxVal - minVal) or 1.0
    numBuckets = min(n, 100)
    buckets = [[] for _ in range(numBuckets)]
    for x, v in zip(A, vals):
        idx = min(int(numBuckets * (v - minVal) / span), numBuckets - 1)
        buckets[idx].append(x)
    totalComp, totalSwaps = 0, 0
    for b in buckets:
        if len(b) > 1:
            sortedB, comp, sw = insertionSort(b, col, ascending)
            totalComp += comp
            totalSwaps += sw
            b[:] = sortedB
    if not ascending:
        buckets.reverse()
    idx = 0
    for b in buckets:
        for y in b:
            A[idx] = y
            idx += 1
    return A, totalComp, totalSwaps

def heapify(A, n, i, col, ascending, comp, swap):
    target, left, right = i, 2 * i + 1, 2 * i + 2
    if left < n:
        comp[0] += 1
        if shouldSwap(A[left], A[target], col, ascending):
            target = left
    if right < n:
        comp[0] += 1
        if shouldSwap(A[right], A[target], col, ascending):
            target = right
    if target != i:
        A[i], A[target] = A[target], A[i]
        swap[0] += 1
        heapify(A, n, target, col, ascending, comp, swap)

def heapSort(arr, col, ascending=True):
    A, n, comp, swap = list(arr), len(arr), [0], [0]
    for i in range(n // 2 - 1, -1, -1):
        heapify(A, n, i, col, ascending, comp, swap)
    for i in range(n - 1, 0, -1):
        A[i], A[0] = A[0], A[i]
        swap[0] += 1
        heapify(A, i, 0, col, ascending, comp, swap)
    return A, comp[0], swap[0]

def shellSort(arr, col, ascending=True):
    A, n = list(arr), len(arr)
    comp, swap, gap = 0, 0, n // 2
    while gap > 0:
        for i in range(gap, n):
            temp, j = A[i], i
            while j >= gap:
                comp += 1
                if shouldSwap(A[j - gap], temp, col, ascending):
                    A[j] = A[j - gap]
                    swap += 1
                    j -= gap
                else:
                    break
            A[j] = temp
        gap //= 2
    return A, comp, swap

SORT_FUNCTIONS = {
    "Bubble Sort": bubbleSort,
    "Insertion Sort": insertionSort,
    "Selection Sort": selectionSort,
    "Merge Sort": mergeSort,
    "Quick Sort": quickSort,
    "Counting Sort": countingSort,
    "Radix Sort": radixSort,
    "Bucket Sort": bucketSort,
    "Heap Sort": heapSort,
    "Shell Sort": shellSort,
}

ALGORITHM_INFO = {
    "Bubble Sort": {"complexity": "O(n²)", "stable": "Yes"},
    "Insertion Sort": {"complexity": "O(n²)", "stable": "Yes"},
    "Selection Sort": {"complexity": "O(n²)", "stable": "No"},
    "Merge Sort": {"complexity": "O(n log n)", "stable": "Yes"},
    "Quick Sort": {"complexity": "O(n log n)", "stable": "No"},
    "Counting Sort": {"complexity": "O(n + k)", "stable": "Yes"},
    "Radix Sort": {"complexity": "O(d * (n + k))", "stable": "Yes"},
    "Bucket Sort": {"complexity": "O(n + k)", "stable": "Yes"},
    "Heap Sort": {"complexity": "O(n log n)", "stable": "No"},
    "Shell Sort": {"complexity": "O(n^1.5)", "stable": "No"},
}

def runSort(name, arr, col, ascending=True):
    if name not in SORT_FUNCTIONS:
        return arr, 0, 0, 0.0
    t0 = time.time()
    sortedArr, comp, swap = SORT_FUNCTIONS[name](arr, col, ascending)
    return sortedArr, comp, swap, (time.time() - t0) * 1000.0

def multiLevelCompare(r1, r2, col1, asc1, col2, asc2):
    v1_a, v1_b = r1.get(col1), r2.get(col1)
    if v1_a != v1_b:
        return v1_a > v1_b if asc1 else v1_a < v1_b
    v2_a, v2_b = r1.get(col2), r2.get(col2)
    return v2_a > v2_b if asc2 else v2_a < v2_b

def multiLevelSort(arr, col1, asc1, col2, asc2):
    comp, swap = [0], [0]
    def merge(left, right):
        res, i, j = [], 0, 0
        while i < len(left) and j < len(right):
            comp[0] += 1
            if not multiLevelCompare(left[i], right[j], col1, asc1, col2, asc2):
                res.append(left[i])
                i += 1
            else:
                res.append(right[j])
                swap[0] += 1
                j += 1
        res.extend(left[i:])
        res.extend(right[j:])
        return res
    def sort(lst):
        if len(lst) <= 1:
            return lst
        mid = len(lst) // 2
        return merge(sort(lst[:mid]), sort(lst[mid:]))
    t0 = time.time()
    return sort(list(arr)), comp[0], swap[0], (time.time() - t0) * 1000.0

def matchFilter(rowVal, query, filterType):
    sVal, sQ = str(rowVal).strip().lower(), str(query).strip().lower()
    if filterType == "contains": return sQ in sVal
    if filterType == "starts_with": return sVal.startswith(sQ)
    if filterType == "ends_with": return sVal.endswith(sQ)
    if filterType == "equals": return sVal == sQ
    try:
        if filterType == ">": return float(rowVal) > float(query)
        if filterType == "<": return float(rowVal) < float(query)
    except (ValueError, TypeError): pass
    return False

def linearSearch(arr, col, query, filterType="contains"):
    t0 = time.time()
    res = [r for r in arr if matchFilter(r.get(col, ""), query, filterType)]
    return res, len(arr), (time.time() - t0) * 1000.0

def binarySearch(arr, col, query):
    t0 = time.time()
    sortedList, _, _ = shellSort(arr, col, ascending=True)
    try:
        target = float(query) if sortedList and isinstance(sortedList[0].get(col), (int, float)) else query
    except ValueError:
        target = query
    low, high, comp, foundIdx = 0, len(sortedList) - 1, 0, -1
    while low <= high:
        comp += 1
        mid = (low + high) // 2
        mVal = sortedList[mid].get(col)
        if mVal == target:
            foundIdx = mid
            break
        elif mVal < target:
            low = mid + 1
        else:
            high = mid - 1
    res = []
    if foundIdx != -1:
        idx = foundIdx
        while idx >= 0 and sortedList[idx].get(col) == target:
            res.append(sortedList[idx])
            idx -= 1
        res.reverse()
        idx = foundIdx + 1
        while idx < len(sortedList) and sortedList[idx].get(col) == target:
            res.append(sortedList[idx])
            idx += 1
    return res, comp, (time.time() - t0) * 1000.0

def compositeSearch(arr, col1, f1, q1, op, col2, f2, q2):
    t0 = time.time()
    res = []
    for r in arr:
        m1, m2 = matchFilter(r.get(col1, ""), q1, f1), matchFilter(r.get(col2, ""), q2, f2)
        cond = (m1 and m2) if op == "AND" else ((m1 or m2) if op == "OR" else (m1 and not m2))
        if cond:
            res.append(r)
    return res, len(arr), (time.time() - t0) * 1000.0
