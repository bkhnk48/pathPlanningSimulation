# Add hallway module

## Directory
- Unzip and add `hallway_simulator_module` to `model`
- Unzip and add `data` to the main directory
- create or use the file `functions.txt`
    ```text
    y = 3 * x + 599 (0,600)
    y = 0 * x + 2399 (601,1200)
    y = -1 * x + 3600 (1201, 3600)
    ```

## main.py
- Add these lines to the top of `main.py`:
```python
import os
os.system("rm -rf data/input/*")
os.system("rm -rf data/output/*")
os.system("rm -rf data/timeline/*")
os.system("rm -rf data/tmp/*")
```

- Add these lines to bottom of `choose_solver`:
```python
# choose to run sfm or not
print("Choose to run sfm or not:")
print("1 - Run sfm")
print("0 - Not run sfm")
choice = input("Enter your choice (1 or 0): ")
if choice == '1':
    config.sfm = True
elif choice == '0':
    config.sfm = False
else:
    print("Invalid choice. Defaulting to not run sfm.")
    config.sfm = False
```

## config.py

- Add these lines to the bottom of `config.py`
```python
useSFM = False
functions_file = "functions.txt"
```

