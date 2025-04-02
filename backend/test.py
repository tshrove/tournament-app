#!/usr/bin/env python3
import sys
import os

print("Python path:", sys.path)
print("Current directory:", os.getcwd())
print("Directory contents:", os.listdir('.'))

try:
    with open('models.py', 'r') as f:
        print("\nmodels.py first line:", f.readline().strip())
except Exception as e:
    print("Error reading models.py:", e)

try:
    with open('app.py', 'r') as f:
        for i, line in enumerate(f):
            if i < 20:  # Print first 20 lines
                print(f"app.py line {i+1}: {line.strip()}")
except Exception as e:
    print("Error reading app.py:", e) 