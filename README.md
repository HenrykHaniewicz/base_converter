# Base-10 to Base-n Converter (±2 to ±36)

Convert any base-10 integer into bases from **-36 to -2** and **2 to 36**.  
For **negative bases**, the algorithm ensures **non-negative** output ("principal value" representation).

---

## Features

- Converts to any base `b` where `|b| ∈ [2, 36]`
- Handles **negative bases** (e.g., base -2) with positive remainders
- Prints output in a friendly way
- Can print conversions for **all bases** or **all positive bases**

---

## Requirements

- Python **3.9+**
- An OS

---

## Usage

```bash
python base_converter.py number [base]
python base_converter.py number --all
python base_converter.py number --allpos
```

### Arguments

- `number` (required): an integer in base 10 (e.g. `42`, `-13`)
- `base` (optional): an integer base where `|base| ∈ [2, 36]` (e.g. `2`, `16`, `-2`, `-7`)
- `--all`: show conversions for every supported base **−36…−2, 2…36**
- `--allpos`: show conversions for positive bases **2…36**

### Examples

Convert to a specific base:

```bash
# 42 in binary
python base_converter.py 42 2
# -> Number in base 10:      42
# -> Number in base 2:       101010
```

```bash
# 42 in base -2 (negabinary)
python base_converter.py 42 -2
# -> Number in base 10:      42
# -> Number in base -2:      1111110
```

```bash
# -255 in hexadecimal
python base_converter.py -255 16
# -> Number in base 10:      -255
# -> Number in base 16:      -FF
```

List all base outputs:

```bash
python base_converter.py 13 --all
```

Only positive base outputs:

```bash
python base_converter.py -13 --allpos
```

---

## Output Format

Digits `0-9` represent values 0-9, and `A-Z` represent values 10-35 (assuming your Unicode layout is the same as mine).  
For **positive bases**, negative inputs are prefixed with `-` (e.g., `-FF`).  
For **negative bases**, all digits are non-negative so there is **no leading minus** in the representation.

---

## Library API

You can import the converter and use it in your own programs:

```python
from base_converter import convert2base, convert_all_bases

# Convert a single number/base
Q, s = convert2base(42, -2)   # s == "1111110", Q is the quotient trace

# Print all bases for a number
convert_all_bases(-13, positive_only=True)  # prints bases 2..36
```