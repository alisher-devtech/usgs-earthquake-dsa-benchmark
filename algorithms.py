import time

def shouldSwap(r1, r2, col, ascending=True):
    v1 = r1.get(col, 0)
    if v1 is None:
        v1 = 0
    v2 = r2.get(col, 0)
    if v2 is None:
        v2 = 0
    if ascending:
        return v1 > v2
    else:
        return v1 < v2

def bubbleSort(arr, col, ascending=True):
    A = list(arr)
    n = len(A)
    comp = 0
    swap_count = 0
    for i in range(n - 1):
        swap = False
        for j in range(n - 1 - i):
            comp += 1
            if shouldSwap(A[j], A[j + 1], col, ascending):
                A[j], A[j + 1] = A[j + 1], A[j]
                swap = True
                swap_count += 1
        if swap == False:
            break
    return A, comp, swap_count

def selectionSort(arr, col, ascending=True):
    A = list(arr)
    n = len(A)
    comp = 0
    swap_count = 0
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            comp += 1
            if shouldSwap(A[min_idx], A[j], col, ascending):
                min_idx = j
        if min_idx != i:
            A[i], A[min_idx] = A[min_idx], A[i]
            swap_count += 1
    return A, comp, swap_count

def insertionSort(arr, col, ascending=True):
    A = list(arr)
    n = len(A)
    comp = 0
    swap_count = 0
    for i in range(1, n):
        key = A[i]
        j = i - 1
        while j >= 0:
            comp += 1
            if shouldSwap(A[j], key, col, ascending):
                A[j + 1] = A[j]
                swap_count += 1
                j -= 1
            else:
                break
        A[j + 1] = key
    return A, comp, swap_count

def Merge(arr, p, q, r, col, ascending, comp, swap):
    left = arr[p : q + 1]
    right = arr[q + 1 : r + 1]
    i = 0
    j = 0
    k = p
    while i < len(left) and j < len(right):
        comp[0] += 1
        if not shouldSwap(left[i], right[j], col, ascending):
            arr[k] = left[i]
            i = i + 1
        else:
            arr[k] = right[j]
            swap[0] += 1
            j = j + 1
        k = k + 1
    while i < len(left):
        arr[k] = left[i]
        i = i + 1
        k = k + 1
    while j < len(right):
        arr[k] = right[j]
        j = j + 1
        k = k + 1

def mergeSort(arr, col, ascending=True, start=0, end=None, comp=None, swap=None):
    if comp is None:
        arr = list(arr)
        comp = [0]
        swap = [0]
        end = len(arr) - 1
        is_root = True
    else:
        is_root = False

    if start < end:
        mid = (start + end) // 2
        mergeSort(arr, col, ascending, start, mid, comp, swap)
        mergeSort(arr, col, ascending, mid + 1, end, comp, swap)
        Merge(arr, start, mid, end, col, ascending, comp, swap)

    if is_root:
        return arr, comp[0], swap[0]

def partition(A, low, high, col, ascending, comp, swap):
    x = A[high]
    i = low - 1
    for j in range(low, high):
        comp[0] += 1
        if not shouldSwap(A[j], x, col, ascending):
            i += 1
            A[i], A[j] = A[j], A[i]
            swap[0] += 1
    A[i + 1], A[high] = A[high], A[i + 1]
    swap[0] += 1
    return i + 1

def quickSort(A, col, ascending=True, low=0, high=None, comp=None, swap=None):
    if comp is None:
        A = list(A)
        comp = [0]
        swap = [0]
        high = len(A) - 1
        is_root = True
    else:
        is_root = False

    while low < high:
        q = partition(A, low, high, col, ascending, comp, swap)
        if (q - low) < (high - q):
            quickSort(A, col, ascending, low, q - 1, comp, swap)
            low = q + 1
        else:
            quickSort(A, col, ascending, q + 1, high, comp, swap)
            high = q - 1

    if is_root:
        return A, comp[0], swap[0]

def countingSort(arr, col, ascending=True):
    A = list(arr)
    n = len(A)
    if n == 0:
        return A, 0, 0
    vals = []
    for x in A:
        val = x.get(col, 0)
        if val is None:
            val = 0
        vals.append(float(val))
    minVal = min(vals)
    maxVal = max(vals)
    span = maxVal - minVal
    if span <= 50:
        scale = 100
    elif span > 100000:
        scale = 100000 / span
    else:
        scale = 1
    keys = []
    for v in vals:
        keys.append(int(round((v - minVal) * scale)))
    M = max(keys)
    count_array = [0] * (M + 1)
    output_array = [0] * n
    for k in keys:
        count_array[k] = count_array[k] + 1
    for i in range(1, M + 1):
        count_array[i] = count_array[i] + count_array[i - 1]
    for j in range(n - 1, -1, -1):
        value = keys[j]
        target_idx = count_array[value] - 1
        output_array[target_idx] = A[j]
        count_array[value] -= 1
    if not ascending:
        output_array.reverse()
    return output_array, n, n

def counting_sort_by_digit(A, units, swap):
    n = len(A)
    count_array = [0] * 10
    output_array = [0] * n
    for x in A:
        digit = (x[1] // units) % 10
        count_array[digit] = count_array[digit] + 1
    for i in range(1, 10):
        count_array[i] = count_array[i] + count_array[i - 1]
    for j in range(n - 1, -1, -1):
        value = A[j]
        digit = (value[1] // units) % 10
        target_idx = count_array[digit] - 1
        output_array[target_idx] = value
        count_array[digit] = count_array[digit] - 1
        swap[0] += 1
    for i in range(n):
        A[i] = output_array[i]

def radixSort(arr, col, ascending=True):
    A = list(arr)
    n = len(A)
    if n == 0:
        return A, 0, 0
    vals = []
    for x in A:
        val = x.get(col, 0)
        if val is None:
            val = 0
        vals.append(float(val))
    minVal = min(vals)
    paired = []
    max_key = 0
    for i in range(n):
        int_key = int(round((vals[i] - minVal) * 100))
        paired.append((A[i], int_key))
        if int_key > max_key:
            max_key = int_key
    M = max_key
    units = 1
    swap = [0]
    while M // units > 0:
        counting_sort_by_digit(paired, units, swap)
        units *= 10
    res = []
    for p in paired:
        res.append(p[0])
    if not ascending:
        res.reverse()
    comparisons = n * len(str(M))
    return res, comparisons, swap[0]

def bucketSort(arr, col, ascending=True):
    A = list(arr)
    n = len(A)
    if n <= 1:
        return A, 0, 0
    vals = []
    for x in A:
        val = x.get(col, 0)
        if val is None:
            val = 0
        vals.append(float(val))
    minVal = min(vals)
    maxVal = max(vals)
    span = maxVal - minVal
    if span == 0:
        span = 1.0
    num_buckets = min(n, 100)
    buckets = [[] for i in range(num_buckets)]
    for i in range(n):
        v = vals[i]
        target_idx = int(num_buckets * (v - minVal) / span)
        if target_idx >= num_buckets:
            target_idx = num_buckets - 1
        buckets[target_idx].append(A[i])
    totalComp = 0
    totalSwaps = 0
    for x in buckets:
        if len(x) > 1:
            sortedB, comp, sw = insertionSort(x, col, ascending)
            totalComp += comp
            totalSwaps += sw
            x[:] = sortedB
    if not ascending:
        buckets.reverse()
    idx = 0
    for x in buckets:
        for y in x:
            A[idx] = y
            idx += 1
    return A, totalComp, totalSwaps

def heapify(A, n, i, col, ascending, comp, swap):
    target = i
    left = 2 * i + 1
    right = 2 * i + 2
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
    A = list(arr)
    n = len(A)
    comp = [0]
    swap = [0]
    for i in range(n // 2 - 1, -1, -1):
        heapify(A, n, i, col, ascending, comp, swap)
    for i in range(n - 1, 0, -1):
        A[i], A[0] = A[0], A[i]
        swap[0] += 1
        heapify(A, i, 0, col, ascending, comp, swap)
    return A, comp[0], swap[0]

def shellSort(arr, col, ascending=True):
    A = list(arr)
    n = len(A)
    comp = 0
    swap_count = 0
    gap = n // 2
    while gap > 0:
        for i in range(gap, n):
            key = A[i]
            j = i
            while j >= gap:
                comp += 1
                if shouldSwap(A[j - gap], key, col, ascending):
                    A[j] = A[j - gap]
                    swap_count += 1
                    j -= gap
                else:
                    break
            A[j] = key
        gap = gap // 2
    return A, comp, swap_count

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

def runSort(name, arr, col, ascending=True):
    if name not in SORT_FUNCTIONS:
        return arr, 0, 0, 0.0
    t0 = time.time()
    sortedArr, comp, swap = SORT_FUNCTIONS[name](arr, col, ascending)
    elapsed_ms = (time.time() - t0) * 1000.0
    return sortedArr, comp, swap, elapsed_ms

def multiLevelCompare(r1, r2, col1, asc1, col2, asc2):
    v1_a = r1.get(col1)
    v1_b = r2.get(col1)
    if v1_a != v1_b:
        if asc1:
            return v1_a > v1_b
        else:
            return v1_a < v1_b
    v2_a = r1.get(col2)
    v2_b = r2.get(col2)
    if asc2:
        return v2_a > v2_b
    else:
        return v2_a < v2_b

def multiLevelMerge(arr, p, q, r, col1, asc1, col2, asc2, comp, swap):
    left = arr[p : q + 1]
    right = arr[q + 1 : r + 1]
    i = 0
    j = 0
    k = p
    while i < len(left) and j < len(right):
        comp[0] += 1
        if not multiLevelCompare(left[i], right[j], col1, asc1, col2, asc2):
            arr[k] = left[i]
            i = i + 1
        else:
            arr[k] = right[j]
            swap[0] += 1
            j = j + 1
        k = k + 1
    while i < len(left):
        arr[k] = left[i]
        i = i + 1
        k = k + 1
    while j < len(right):
        arr[k] = right[j]
        j = j + 1
        k = k + 1

def multiLevelSort(arr, col1, asc1, col2, asc2, start=0, end=None, comp=None, swap=None):
    if comp is None:
        arr = list(arr)
        comp = [0]
        swap = [0]
        end = len(arr) - 1
        t0 = time.time()
        is_root = True
    else:
        is_root = False

    if start < end:
        mid = (start + end) // 2
        multiLevelSort(arr, col1, asc1, col2, asc2, start, mid, comp, swap)
        multiLevelSort(arr, col1, asc1, col2, asc2, mid + 1, end, comp, swap)
        multiLevelMerge(arr, start, mid, end, col1, asc1, col2, asc2, comp, swap)

    if is_root:
        elapsed_ms = (time.time() - t0) * 1000.0
        return arr, comp[0], swap[0], elapsed_ms

def matchFilter(rowVal, query, filterType):
    sVal = str(rowVal).strip().lower()
    sQ = str(query).strip().lower()
    if filterType == "contains":
        return sQ in sVal
    elif filterType == "starts_with":
        return sVal.startswith(sQ)
    elif filterType == "ends_with":
        return sVal.endswith(sQ)
    elif filterType == "equals":
        return sVal == sQ
    elif filterType == ">":
        try:
            return float(rowVal) > float(query)
        except (ValueError, TypeError):
            return False
    elif filterType == "<":
        try:
            return float(rowVal) < float(query)
        except (ValueError, TypeError):
            return False
    return False

def linearSearch(arr, col, query, filterType="contains"):
    t0 = time.time()
    res = []
    for r in arr:
        val = r.get(col, "")
        if matchFilter(val, query, filterType):
            res.append(r)
    elapsed_ms = (time.time() - t0) * 1000.0
    return res, len(arr), elapsed_ms

def binarySearch(arr, col, query):
    t0 = time.time()
    sortedList, sort_comp, sort_swap = shellSort(arr, col, ascending=True)
    try:
        target = float(query)
    except ValueError:
        target = query
    low = 0
    high = len(sortedList) - 1
    comp = 0
    foundIdx = -1
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
            idx = idx - 1
        res.reverse()
        idx = foundIdx + 1
        while idx < len(sortedList) and sortedList[idx].get(col) == target:
            res.append(sortedList[idx])
            idx = idx + 1
    elapsed_ms = (time.time() - t0) * 1000.0
    return res, comp, elapsed_ms

def compositeSearch(arr, col1, f1, q1, op, col2, f2, q2):
    t0 = time.time()
    res = []
    for r in arr:
        val1 = r.get(col1, "")
        val2 = r.get(col2, "")
        m1 = matchFilter(val1, q1, f1)
        m2 = matchFilter(val2, q2, f2)
        if op == "AND":
            cond = (m1 and m2)
        elif op == "OR":
            cond = (m1 or m2)
        else:
            cond = (m1 and not m2)
        if cond:
            res.append(r)
    elapsed_ms = (time.time() - t0) * 1000.0
    return res, len(arr), elapsed_ms
