import random as rd
import time
import numpy as np
import matplotlib.pyplot as plt


def generate_random_list():
    """Generates a random list of integers."""
    length = 20 
    return [rd.randint(0, 100) for _ in range(length)]  # Random numbers between 0 and 100

def random_graph():
    """Generates and saves a random graph."""
    x = generate_random_list()
    y = generate_random_list()

    plt.figure()
    plt.plot(x, y, marker='o')
    plt.title("Random Graph")
    plt.xlabel("X values")
    plt.ylabel("Y values")
    
    # Save with a timestamp to avoid overwriting
    filename = f"graphs/random_graph.png"
    plt.savefig(filename)
    plt.close()  # Close the figure to free memory
    print(f"Graph saved as {filename}")


def main():
    while True:
        random_list = generate_random_list()
        random_graph()
        print(f"New random list: {random_list}")
        time.sleep(5)  # Wait 10 seconds before generating the next list

if __name__ == "__main__":
    main() 
