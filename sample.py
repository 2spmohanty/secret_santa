import numpy as np

def create_matrix(arr, item):
    # Check if the array can be arranged into a len(arr) x 3 matrix
    if len(arr) < 3:
        raise ValueError("Array must have at least 3 elements to form a matrix with a row of identical items.")

    # Create an empty list to hold the rows of the matrix
    matrix = []

    # Add rows with different items until we have enough for the matrix
    used_items = set()

    # Add unique items to the matrix
    for value in arr:
        if value != item and value not in used_items:
            # Add a row with three different values (if possible)
            matrix.append([value, arr[(arr.index(value) + 1) % len(arr)], arr[(arr.index(value) + 2) % len(arr)]])
            used_items.add(value)
            if len(matrix) == len(arr) - 1:  # Stop if we've added enough unique items
                break

    # Add one row with the identical item
    matrix.append([item, item, item])

    # Convert to numpy array for better formatting
    result_matrix = np.array(matrix)

    return result_matrix

# Example usage
arr = ["A", "B", "C", "D", "E"]
item = "C"
matrix = create_matrix(arr, item)
print("Resulting Matrix:")
print(matrix)