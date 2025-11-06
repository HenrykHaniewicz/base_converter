# Convert base ten to -36 to 36
# If the base is negative, this algorithm will produce the principle value (positive remainders)

import sys

def partition_quotient( dividend, divisor, minusone = False ):
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
    while (remainder < 0):
        quotient += 1
        remainder += abs(divisor)

    return quotient, remainder

def digit_to_char( digit ):
    """Convert a digit (0-35) to its character representation (0-9, A-Z)"""
    if digit < 10:
        return str(digit)
    else:
        return chr(ord('A') + digit - 10)

def convert2base( n, base ):
    """
    Convert a base-10 integer n to the specified base.
    Returns a tuple of (quotient_list, result_string).
    """
    # Handle sign for positive bases
    is_negative = n < 0
    if base > 0 and is_negative:
        n = abs(n)
    
    Q, R = [], []
    q, r = partition_quotient( n, base )
    Q.append(q)
    R.append(r)
    while ( q != 0 ):
        if q == -1:
            q, r = partition_quotient( q, base, True )
        else:
            q, r = partition_quotient( q, base )
        Q.append(q)
        R.append(r)

    out = ''
    for digit in reversed(R):
        out += digit_to_char(int(digit))
    
    # Restore sign for positive bases
    if base > 0 and is_negative:
        out = '-' + out
    
    return Q, out

def convert_all_bases(base10_number, positive_only=False):
    """Convert to all available bases and display results"""
    print(f'\nOriginal number in base 10: {base10_number}\n')
    print('-' * 40)
    
    if positive_only:
        # Only positive bases from 2 to 36
        bases_to_try = range(2, 37)
    else:
        # All bases from -36 to 36, excluding -1, 0, 1
        bases_to_try = list(range(-36, -1)) + list(range(2, 37))
    
    for base in bases_to_try:
        _, result = convert2base(base10_number, base)
        print(f'Number in base {base:3}: \t{result}')
    
    print('-' * 40)

def print_usage():
    print("""                       ------------------------------
                        Base 10 --> Base n converter
                       ------------------------------

        Usage: base_converter.py number [base]
               base_converter.py number --all
               base_converter.py number --allpos

        Input can be a positive or negative integer.
        Optional base (default = 2) should have magnitude between 2-36.
        
        Options:
          --all     Display conversions to all supported bases (-36 to 36)
          --allpos  Display conversions to all positive bases (2 to 36)
        
        Output in base n will be positive for negative bases.\n""")

def parse_args():
    """
    Parse command line arguments and validate input.
    Returns tuple of (base10_number, base_or_flag).
    """
    # Check for no arguments
    if len(sys.argv) == 1:
        print_usage()
        sys.exit()
    
    # Check for too many arguments
    if len(sys.argv) > 3:
        print(f"\nError: Too many arguments provided (got {len(sys.argv) - 1}, expected at most 2).\n")
        print_usage()
        sys.exit(1)

    # Parse the number
    try:
        base10_number = int(sys.argv[1])
    except ValueError:
        print(f"\nError: '{sys.argv[1]}' is not a valid integer.\n")
        print_usage()
        sys.exit(1)

    # Parse optional second argument
    if len(sys.argv) == 3:
        if sys.argv[2] == '--all':
            return base10_number, 'all'
        elif sys.argv[2] == '--allpos':
            return base10_number, 'allpos'
        else:
            # Try to parse as base number
            try:
                base = int(sys.argv[2])
            except ValueError:
                print(f"\nError: '{sys.argv[2]}' is not a valid base or option.\n")
                print_usage()
                sys.exit(1)
    else:
        base = 2

    # If not in --all or --allpos mode, validate the base
    if len(sys.argv) < 3 or sys.argv[2] not in ['--all', '--allpos']:
        # Validate base
        if base == 0:
            print("\nError: Base cannot be 0. Division by zero is undefined.")
            print("Please choose a base with magnitude between 2 and 36.\n")
            sys.exit(1)
        
        if base == 1 or base == -1:
            print(f"\nError: Base {base} is not supported.")
            print("Base 1 and -1 don't provide unique representations.")
            print("Please choose a base with magnitude between 2 and 36.\n")
            sys.exit(1)
        
        if abs(base) > 36:
            print(f"\nError: Base {base} is outside supported range.")
            print("This implementation supports bases with magnitude between 2 and 36.\n")
            sys.exit(1)

    return base10_number, base



if __name__ == "__main__":

    base10_number, base_or_flag = parse_args()

    if base_or_flag == 'all':
        convert_all_bases(base10_number, positive_only=False)
    elif base_or_flag == 'allpos':
        convert_all_bases(base10_number, positive_only=True)
    else:
        quo, rem = convert2base(base10_number, base_or_flag)
        print(f'\nNumber in base 10: \t{base10_number}')
        print(f'Number in base {base_or_flag}: \t{rem}\n')