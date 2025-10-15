# The precursor to doing binary search is to see whether a function is monotonic
# Monotonic: non-decreasing or non-increasing, no fluctuations
# Feasible function: determines if an element meets the , so is Boolean array with consecutive 0s followed by 1s


def first_not_smaller(arr: list[int], target: int) -> int:
    # WRITE YOUR BRILLIANT CODE HERE
    left, right = 0, len(arr) - 1
    find_boundary = -1
    
    while left <= right:

        mid = (left + right) // 2

        # if arr[mid] mean that if its the bool True it returns true else it was a false
        # THIS:if arr[mid] >= target: is the feasible (monotonic) function. We reduced simple bs down to finding first true element in boolean
        # in other words for every number in a list, is either true or false if ran by the feasible function
        if arr[mid] >= target:
            # It's true which is good, but we still need keep looking left in-case this is not the boundary between True False
            right = mid -1
            find_boundary = mid
        else:
            left = mid + 1

    return find_boundary


def find_first_occurrence(arr: list[int], target: int) -> int:
    l = 0
    r = len(arr) - 1
    ans = -1
    while l <= r:
        mid = (l + r) // 2
        if arr[mid] == target:
            ans = mid
            r = mid - 1
        elif arr[mid] < target:
            l = mid + 1
        else:
            r = mid - 1
    return ans