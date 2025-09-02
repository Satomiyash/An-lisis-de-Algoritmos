def selectionSort(data, draw_callback):
    n = len(data)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            draw_callback(activos=[i, j, min_idx])
            yield
            if data[j] < data[min_idx]:
                min_idx = j
        data[i], data[min_idx] = data[min_idx], data[i]
        draw_callback(activos=[i, min_idx])
        yield
    draw_callback(activos=[])


def bubbleSort(arr, draw_callback):
    n = len(arr)
    for i in range(n-1):
        for j in range(0, n-i-1):
            draw_callback(activos=[j, j+1])
            yield
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
        draw_callback(activos=[j, j+1])
        yield
    draw_callback(activos=[])


def mergeSort(arr, draw_callback, start=0, end=None):
    if end is None:
        end = len(arr) - 1

    if start >= end:
        return

    mid = (start + end) // 2

    # Ordenar mitades recursivamente
    yield from mergeSort(arr, draw_callback, start, mid)
    yield from mergeSort(arr, draw_callback, mid + 1, end)

    # Fusionar las mitades ordenadas
    yield from merge(arr, draw_callback, start, mid, end)
    draw_callback(activos=[])


def merge(arr, draw_callback, start, mid, end):
    left = arr[start:mid+1]
    right = arr[mid+1:end+1]

    i = j = 0
    k = start

    while i < len(left) and j < len(right):
        draw_callback(activos=[k, start + i, mid + 1 + j])
        yield
        if left[i] <= right[j]:
            arr[k] = left[i]
            i += 1
        else:
            arr[k] = right[j]
            j += 1
        k += 1

    while i < len(left):
        draw_callback(activos=[k, start + i])
        yield
        arr[k] = left[i]
        i += 1
        k += 1

    while j < len(right):
        draw_callback(activos=[k, mid + 1 + j])
        yield
        arr[k] = right[j]
        j += 1
        k += 1

    draw_callback(activos=list(range(start, end+1)))
    yield


def quickSort(arr, draw_callback, start=0, end=None):
    if end is None:
        end = len(arr) - 1

    if start >= end:
        return

    pivot_index = start
    pivot = arr[pivot_index]

    left = start + 1
    right = end

    draw_callback(activos=[pivot_index, left, right])
    yield

    while left <= right:
        while left <= end and arr[left] <= pivot:
            left += 1
            draw_callback(activos=[pivot_index, left, right])
            yield

        while right >= start and arr[right] > pivot:
            right -= 1
            draw_callback(activos=[pivot_index, left, right])
            yield

        if left < right:
            arr[left], arr[right] = arr[right], arr[left]
            draw_callback(activos=[pivot_index, left, right])
            yield

    arr[pivot_index], arr[right] = arr[right], arr[pivot_index]
    draw_callback(activos=[pivot_index, right])
    yield

    yield from quickSort(arr, draw_callback, start, right - 1)
    yield from quickSort(arr, draw_callback, right + 1, end)
    draw_callback(activos=[])