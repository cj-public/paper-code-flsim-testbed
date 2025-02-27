import random
import secrets
import time

def test_predictability():
    # Set same seed to demonstrate predictability
    random.seed(42)
    
    print("Testing random.randint() predictability:")
    results_random = [random.randint(0, 100000000) for _ in range(5)]
    
    # Reset seed to show same numbers generated
    random.seed(42)
    results_random2 = [random.randint(0, 100000000) for _ in range(5)]
    
    print("\nrandom.randint() with same seed:")
    print(f"First run:  {results_random}")
    print(f"Second run: {results_random2}")
    print(f"Predictable? {results_random == results_random2}\n")
    
    print("Testing secrets.randbelow() unpredictability:")
    results_secrets = [secrets.randbelow(100000000) for _ in range(5)]
    results_secrets2 = [secrets.randbelow(100000000) for _ in range(5)]
    
    print("\nsecrets.randbelow() results:")
    print(f"First run:  {results_secrets}")
    print(f"Second run: {results_secrets2}")
    print(f"Predictable? {results_secrets == results_secrets2}")

def test_edge_cases():
    print("\nTesting edge cases:")
    
    # Test that we always get non-negative numbers
    results = [secrets.randbelow(100) for _ in range(1000)]
    print(f"All non-negative? {all(x >= 0 for x in results)}")
    
    # Test that we never get numbers >= max
    max_val = 100
    results = [secrets.randbelow(max_val) for _ in range(1000)]
    print(f"All under max ({max_val})? {all(x < max_val for x in results)}")
    
    # Test error handling for invalid input
    try:
        secrets.randbelow(0)
        print("Error: Should have raised ValueError for input 0")
    except ValueError:
        print("Correctly raises ValueError for input 0")
    
    try:
        secrets.randbelow(-1)
        print("Error: Should have raised ValueError for negative input")
    except ValueError:
        print("Correctly raises ValueError for negative input")

if __name__ == "__main__":
    test_predictability()
    test_edge_cases()