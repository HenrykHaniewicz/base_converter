# Base m to Base n Converter (±2 to ±36)

Convert numbers between any bases from **-36 to -2** and **2 to 36**.  
Supports **decimal/fractional numbers** with **arbitrary precision**.  
For **negative bases**, the algorithm ensures **non-negative** output ("principal value" representation).

---

## Features

- Converts between any bases `m` and `n` where `|m|, |n| ∈ [2, 36]`
- Supports **decimal/fractional numbers** (e.g., `3.14159`, `FF.A8`)
- **Arbitrary precision** arithmetic using Python's `decimal` module
- Handles **negative bases** (e.g., base -2) with positive remainders
- Detects and displays **repeating decimals** with parentheses notation
- Can display conversions for **all bases** or **all positive bases**
- Clean command-line interface using `argparse`
- **GUI interface** with modern styling (requires PyQt6)

---

## Requirements

- Python **3.11+**
- PyQt6 (optional, but required for GUI mode): `pip install PyQt6`

---

## Usage

### Command Line

```
python base_converter.py number [-f FROM_BASE] [-t TO_BASE] [-p PRECISION]
python base_converter.py number [-f FROM_BASE] --all [-p PRECISION]
python base_converter.py number [-f FROM_BASE] --allpos [-p PRECISION]
```

### GUI Mode

```
python base_converter.py --gui
```

Launches an interactive graphical interface with:
- Input fields for number, bases, and precision
- Options to show all bases or positive bases only
- Dynamic output window with auto-sizing fonts

### Arguments

- `number` (required in CLI mode): a number in the source base (e.g., `42`, `-13`, `3.14159`, `FF.A8`)
- `-f, --from-base BASE` (optional): base of the input number (default: `10`)
- `-t, --to-base BASE` (optional): base to convert to (default: `2`)
- `-p, --precision DIGITS` (optional): precision for fractional parts (default: `50`)
- `--all`: show conversions for every supported base **−36…−2, 2…36**
- `--allpos`: show conversions for positive bases **2…36**
- `--gui`: launch graphical user interface

### Examples

Convert to a specific base:

```
# 42 (base 10) to binary
python base_converter.py 42
# -> Number in base 10:      42
# -> Number in base 10:      42
# -> Number in base 2:       101010
```

```
# 42 (base 10) to hexadecimal
python base_converter.py 42 -t 16
# -> Number in base 10:      42
# -> Number in base 10:      42
# -> Number in base 16:      2A
```

```
# FF (base 16) to decimal
python base_converter.py FF -f 16 -t 10
# -> Number in base 16:      FF
# -> Number in base 10:      255
# -> Number in base 10:      255
```

```
# 42 (base 10) to base -2 (negabinary)
python base_converter.py 42 -t -2
# -> Number in base 10:      42
# -> Number in base 10:      42
# -> Number in base -2:      1111110
```

```
# -255 (base 10) to hexadecimal
python base_converter.py -255 -t 16
# -> Number in base 10:      -255
# -> Number in base 10:      -255
# -> Number in base 16:      -FF
```

Convert decimal/fractional numbers:

```
# Pi (base 10) to binary
python base_converter.py 3.14159 -t 2
# -> Number in base 10:      3.14159
# -> Number in base 10:      3.14159
# -> Number in base 2:       11.00100100001111110...
```

```
# Hex fraction to decimal
python base_converter.py FF.A8 -f 16 -t 10
# -> Number in base 16:      FF.A8
# -> Number in base 10:      255.65625
# -> Number in base 10:      255.65625
```

```
# High precision conversion (100 digits)
python base_converter.py 0.1 -t 3 -p 100
```

List all base outputs:

```
python base_converter.py 13 --all
```

```
# From a non-base-10 number
python base_converter.py 1A.F -f 16 --all
# Shows both the original (base 16) and base 10 representations
# before listing all conversions
```

Only positive base outputs:

```
python base_converter.py -13 --allpos
```

Launch GUI:

```
python base_converter.py --gui
# Opens interactive window with all conversion options
```

---

## Output Format

Digits `0-9` represent values 0-9, and `A-Z` represent values 10-35 (case insensitive for input).  
For **positive bases**, negative inputs are prefixed with `-` (e.g., `-FF`).  
For **negative bases**, all digits are non-negative so there is **no leading minus** in the representation.  
For **negative base inputs**, numbers must be the principal (positive) value—no leading minus allowed.

**Repeating decimals** are displayed using parentheses:
- `0.1(6)` means `0.1666...`
- `0.142857(142857)` means `0.142857142857142857...`

---

## Library API

You can import the converter and use it in your own programs:

```
from base_converter import convert_to_base, convert_from_base, convert_all_bases
from decimal import Decimal

# Convert from any base to base 10
base10_value = convert_from_base("FF.A8", 16, precision=50)
# -> Decimal('255.65625')

# Convert from base 10 to any base
result = convert_to_base(Decimal("3.14159"), 2, precision=30)
# -> '11.001001000011111100111...'

# Convert an integer
result = convert_to_base(42, -2, precision=50)
# -> '1111110'

# Print all bases for a number
convert_all_bases("FF", 16, Decimal(255), positive_only=True, precision=50)
# Shows original base 16 value, base 10 value, then all positive bases
```

---

## Technical Notes

- Uses Python's `decimal.Decimal` module for arbitrary precision arithmetic
- Precision can be set arbitrarily high (default 50 digits for fractional parts)
- Internal calculations use extra precision to avoid rounding errors
- The algorithm for negative bases ensures principal value representation (all remainders are non-negative)
- GUI features dynamic font sizing and responsive window width (up to 1000px) for optimal readability