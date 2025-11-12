# Convert between any bases from -36 to 36 (excluding -1, 0, 1)
# Supports decimal numbers with arbitrary precision
# For negative bases, this algorithm produces the principal value (positive remainders)

import sys
import argparse
from decimal import Decimal, getcontext, ROUND_DOWN

def partition_quotient(dividend, divisor, minusone=False):
    """
    Perform division ensuring non-negative remainders.
    Returns quotient and remainder where 0 <= remainder < |divisor|.
    """
    if minusone and divisor > 0:
        raise ValueError(f"minusone flag should only be used with negative bases, got base {divisor}")
    elif minusone and dividend != -1:
        raise ValueError(f"minusone flag should only be used with a dividend of -1, got dividend {dividend}")
    
    if not minusone:
        quotient = dividend // divisor
    else:
        quotient = (-1 // divisor) + 1
    remainder = dividend - (quotient * divisor)
    while remainder < 0:
        quotient += 1
        remainder += abs(divisor)

    return quotient, remainder

def digit_to_char(digit):
    """Convert a digit (0-35) to its character representation (0-9, A-Z)"""
    if digit < 10:
        return str(digit)
    else:
        return chr(ord('A') + digit - 10)

def char_to_digit(char):
    """Convert a character (0-9, A-Z, a-z) to its digit value (0-35)"""
    if char.isdigit():
        return int(char)
    elif char.upper() in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        return ord(char.upper()) - ord('A') + 10
    else:
        raise ValueError(f"Invalid character '{char}' in number")

def convert_from_base(number_str, base, precision=100):
    """
    Convert a number string from the specified base to base 10.
    Returns the base-10 Decimal value.
    """
    # Set precision high enough for calculations
    getcontext().prec = precision + 50
    
    # Handle negative sign for positive bases
    is_negative = False
    if number_str.startswith('-'):
        if base < 0:
            raise ValueError("Negative base numbers must be the principal (positive) value.\nNumbers in negative bases should not start with '-'")
        is_negative = True
        number_str = number_str[1:]
    
    if not number_str:
        raise ValueError("Empty number string")
    
    # Split into integer and fractional parts
    if '.' in number_str:
        parts = number_str.split('.')
        if len(parts) != 2:
            raise ValueError("Invalid number format: multiple decimal points")
        int_part, frac_part = parts
    else:
        int_part = number_str
        frac_part = ''
    
    # Convert integer part
    int_result = Decimal(0)
    base_decimal = Decimal(base)
    
    for char in int_part:
        digit = char_to_digit(char)
        if digit >= abs(base):
            raise ValueError(f"Digit '{char}' (value {digit}) is invalid for base {base}")
        int_result = int_result * base_decimal + digit
    
    # Convert fractional part
    frac_result = Decimal(0)
    if frac_part:
        base_power = Decimal(1) / base_decimal
        for char in frac_part:
            digit = char_to_digit(char)
            if digit >= abs(base):
                raise ValueError(f"Digit '{char}' (value {digit}) is invalid for base {base}")
            frac_result += digit * base_power
            base_power /= base_decimal
    
    result = int_result + frac_result
    
    if is_negative:
        result = -result
    
    return result

def convert_integer_to_base(n, base):
    """
    Convert a base-10 integer n to the specified base.
    Returns the result string.
    """
    if n == 0:
        return '0'
    
    # Handle sign for positive bases
    is_negative = n < 0
    if base > 0 and is_negative:
        n = abs(n)
    
    R = []
    q = int(n)
    while q != 0:
        if q == -1:
            q, r = partition_quotient(q, base, True)
        else:
            q, r = partition_quotient(q, base)
        R.append(r)

    out = ''
    for digit in reversed(R):
        out += digit_to_char(int(digit))
    
    # Restore sign for positive bases
    if base > 0 and is_negative:
        out = '-' + out
    
    return out if out else '0'

def convert_fraction_to_base(frac, base, precision):
    """
    Convert a fractional part (0 <= frac < 1) to the specified base.
    Returns the fractional digits as a string (without leading '0.').
    """
    if frac == 0:
        return ''
    
    getcontext().prec = precision + 50
    
    result = ''
    seen_states = {}
    base_decimal = Decimal(abs(base))
    
    # For negative bases, fractional conversion is more complex
    if base < 0:
        for i in range(precision):
            frac *= base_decimal
            digit = int(frac)
            frac -= digit
            
            # Normalize to ensure proper representation
            while frac < 0:
                digit -= 1
                frac += 1
            while frac >= 1:
                digit += 1
                frac -= 1
            
            if digit < 0 or digit >= abs(base):
                break
            
            result += digit_to_char(digit)
            
            if frac == 0:
                break
            
            # Check for repeating pattern
            state = str(frac)
            if state in seen_states:
                repeat_start = seen_states[state]
                non_repeat = result[:repeat_start]
                repeat = result[repeat_start:]
                return f"{non_repeat}({repeat})"
            seen_states[state] = len(result)
    else:
        # Standard algorithm for positive bases
        for i in range(precision):
            frac *= base_decimal
            digit = int(frac)
            frac -= digit
            result += digit_to_char(digit)
            
            if frac == 0:
                break
            
            # Check for repeating pattern
            state = str(frac)
            if state in seen_states:
                repeat_start = seen_states[state]
                non_repeat = result[:repeat_start]
                repeat = result[repeat_start:]
                return f"{non_repeat}({repeat})"
            seen_states[state] = len(result)
    
    return result

def convert_to_base(n, base, precision=50):
    """
    Convert a base-10 number (integer or Decimal) to the specified base.
    Returns the result string.
    """
    getcontext().prec = precision + 50
    
    if not isinstance(n, Decimal):
        n = Decimal(str(n))
    
    # Handle sign for positive bases
    is_negative = n < 0
    if base > 0 and is_negative:
        n = abs(n)
    
    # Separate integer and fractional parts
    int_part = int(n)
    frac_part = n - int_part
    
    # Handle negative base with negative number
    if base < 0 and is_negative:
        int_str = convert_integer_to_base(int_part, base)
        if frac_part != 0:
            frac_str = convert_fraction_to_base(abs(frac_part), base, precision)
            if frac_str:
                return f"{int_str}.{frac_str}"
        return int_str
    
    # Convert integer part
    int_str = convert_integer_to_base(int_part, base)
    
    # Convert fractional part
    if frac_part != 0:
        frac_str = convert_fraction_to_base(frac_part, base, precision)
        if frac_str:
            result = f"{int_str}.{frac_str}"
        else:
            result = int_str
    else:
        result = int_str
    
    # Restore sign for positive bases
    if base > 0 and is_negative:
        if not result.startswith('-'):
            result = '-' + result
    
    return result

def convert_all_bases(original_number_str, from_base, base10_number, positive_only=False, precision=50):
    """Convert to all available bases and display results"""
    print()
    
    # Show original number if from_base is not 10
    if from_base != 10:
        print(f'Number in base {from_base}: \t{original_number_str}')
    
    print(f'Number in base 10: \t{base10_number}\n')
    print('-' * 60)
    
    if positive_only:
        bases_to_try = range(2, 37)
    else:
        bases_to_try = list(range(-36, -1)) + list(range(2, 37))
    
    for base in bases_to_try:
        result = convert_to_base(base10_number, base, precision)
        # Truncate very long results for display
        if len(result) > 50:
            display_result = result[:47] + "..."
        else:
            display_result = result
        print(f'Number in base {base:3}: \t{display_result}')
    
    print('-' * 60)

def validate_base(base):
    """Validate that a base is within supported range. Returns error message or None."""
    if base == 0:
        return "Base cannot be 0. Division by zero is undefined."
    
    if base == 1 or base == -1:
        return f"Base {base} is not supported. Base 1 and -1 don't provide unique representations."
    
    if abs(base) > 36:
        return f"Base {base} is outside supported range (magnitude must be between 2 and 36)."
    
    return None

class CustomFormatter(argparse.RawDescriptionHelpFormatter):
    """Custom formatter to add centered header to help text"""
    def add_usage(self, usage, actions, groups, prefix=None):
        if prefix is None:
            prefix = ''
        return super(CustomFormatter, self).add_usage(usage, actions, groups, prefix)

def parse_args():
    """Parse command line arguments using argparse."""
    # Create centered header
    header = """
              ------------------------------
               Base m --> Base n converter
              ------------------------------
"""
    
    parser = argparse.ArgumentParser(
        description=header,
        formatter_class=CustomFormatter,
        epilog="""
Examples:
  %(prog)s 42                         Convert 42 from base 10 to base 2
  %(prog)s 42 -t 16                   Convert 42 from base 10 to base 16
  %(prog)s FF -f 16 -t 10             Convert FF from base 16 to base 10
  %(prog)s 3.14159 -t 2               Convert 3.14159 from base 10 to base 2
  %(prog)s 0.1 -t 3 -p 100            Convert with 100 digits precision
  %(prog)s 255 --all                  Show 255 in all bases (-36 to 36)
  %(prog)s 255 --allpos               Show 255 in all positive bases (2 to 36)
  %(prog)s 1A.F -f 16 --all           Convert hex 1A.F and show in all bases

Notes:
  - For negative bases, numbers must be the principal (positive) value
  - Repeating decimals are shown with parentheses: 0.1(6) = 0.1666...
  - Letters A-Z represent digits 10-35 (case insensitive)
        """
    )
    
    parser.add_argument(
        'number',
        type=str,
        help='The number to convert (can include decimals, e.g., 3.14159 or FF.A8)'
    )
    
    parser.add_argument(
        '-f', '--from-base',
        type=int,
        default=10,
        metavar='BASE',
        help='Base of the input number (default: 10)'
    )
    
    parser.add_argument(
        '-t', '--to-base',
        type=int,
        default=2,
        metavar='BASE',
        help='Base to convert to (default: 2)'
    )
    
    parser.add_argument(
        '-p', '--precision',
        type=int,
        default=50,
        metavar='DIGITS',
        help='Precision for fractional part (default: 50 digits)'
    )
    
    # Mutually exclusive group for --all and --allpos
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--all',
        action='store_true',
        help='Display conversions to all supported bases (-36 to 36)'
    )
    group.add_argument(
        '--allpos',
        action='store_true',
        help='Display conversions to all positive bases (2 to 36)'
    )
    
    args = parser.parse_args()
    
    # Validate precision
    if args.precision < 1:
        parser.error("Precision must be at least 1")
    
    # Validate from_base
    error = validate_base(args.from_base)
    if error:
        parser.error(f"Invalid from-base: {error}")
    
    # Validate to_base (only if not using --all or --allpos)
    if not args.all and not args.allpos:
        error = validate_base(args.to_base)
        if error:
            parser.error(f"Invalid to-base: {error}")
    
    return args


if __name__ == "__main__":
    args = parse_args()
    
    # Set global precision
    getcontext().prec = args.precision + 100
    
    # Convert from source base to base 10
    try:
        base10_number = convert_from_base(args.number, args.from_base, args.precision)
    except ValueError as e:
        print(f"\nError: {e}\n", file=sys.stderr)
        sys.exit(1)
    
    if args.all:
        convert_all_bases(args.number, args.from_base, base10_number, positive_only=False, precision=args.precision)
    elif args.allpos:
        convert_all_bases(args.number, args.from_base, base10_number, positive_only=True, precision=args.precision)
    else:
        result = convert_to_base(base10_number, args.to_base, args.precision)
        print(f'\nNumber in base {args.from_base}: \t{args.number}')
        print(f'Number in base 10: \t{base10_number}')
        print(f'Number in base {args.to_base}: \t{result}\n')