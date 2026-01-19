def normalize_to_range(numbers, target_min=0, target_max=10):
    """
    Normalize a series of numbers to a specified range.
    
    Parameters:
    -----------
    numbers : list or array-like
        The input numbers to normalize
    target_min : float, default=0
        The minimum value of the target range
    target_max : float, default=10
        The maximum value of the target range
    
    Returns:
    --------
    list : Normalized values in the range [target_min, target_max]
    """
    if len(numbers) == 0:
        return []
    
    # Find min and max of input
    min_val = min(numbers)
    max_val = max(numbers)
    
    # Handle edge case where all numbers are the same
    if min_val == max_val:
        return [target_min] * len(numbers)
    
    # Normalize each number
    normalized = []
    for num in numbers:
        # Scale to 0-1, then to target range
        normalized_value = ((num - min_val) / (max_val - min_val)) * (target_max - target_min) + target_min
        normalized.append(normalized_value)
    
    return normalized


# Example usage
if __name__ == "__main__":
    # Test with different sets of numbers
    data1 = [1, 4, -1, 1.5, 0, 5, -2, 3.5, 1.5, 10, 1, 8, 1, 7, 0, 6]
    data2 = [2, 1, 1.5, 0, 7, 5, 2.5, 4, 8, 5, 5, 4, 10, 5, 6, 5]
    data3 = [6, 3, 7, 10, 4, 3.5, 6, 8, 3.5, 2, 5, 5, 1, 0, 3, 4]
    
    print("Original data:", data1)
    print("Normalized:", normalize_to_range(data1))
    print()
    
    print("Original data:", data2)
    print("Normalized:", normalize_to_range(data2))
    print()
    
    print("Original data:", data3)
    print("Normalized:", normalize_to_range(data3))