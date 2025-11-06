import pytest
from base_converter import convert2base, digit_to_char


class TestConvert2Base:
    """Test the convert2base function for base conversion."""
    
    def char_to_digit(self, char):
        """Helper function to convert character back to digit."""
        if char.isdigit():
            return int(char)
        else:
            return ord(char) - ord('A') + 10
    
    def base_to_decimal(self, num_str, base):
        """Helper function to convert from any base back to decimal."""
        if num_str.startswith('-'):
            sign = -1
            num_str = num_str[1:]
        else:
            sign = 1
        
        result = 0
        for char in num_str:
            digit = self.char_to_digit(char)
            result = result * abs(base) + digit
        return sign * result
    
    def test_binary_conversion(self):
        """Test conversion to binary (base 2)."""
        quotients, result = convert2base(10, 2)
        assert result == '1010'
        # Verify by converting back
        assert self.base_to_decimal(result, 2) == 10
        
        quotients, result = convert2base(255, 2)
        assert result == '11111111'
        assert self.base_to_decimal(result, 2) == 255
    
    def test_negative_number_positive_base(self):
        """Test conversion of negative numbers with positive bases."""
        quotients, result = convert2base(-10, 2)
        assert result == '-1010'
        assert self.base_to_decimal(result, 2) == -10
        
        quotients, result = convert2base(-255, 16)
        assert result == '-FF'
        assert self.base_to_decimal(result, 16) == -255
    
    def test_hexadecimal_conversion(self):
        """Test conversion to hexadecimal (base 16)."""
        quotients, result = convert2base(255, 16)
        assert result == 'FF'
        assert self.base_to_decimal(result, 16) == 255
        
        quotients, result = convert2base(4095, 16)
        assert result == 'FFF'
        assert self.base_to_decimal(result, 16) == 4095
    
    def test_base_36_conversion(self):
        """Test conversion to maximum supported base (36)."""
        quotients, result = convert2base(1296, 36)
        assert result == '100'
        assert self.base_to_decimal(result, 36) == 1296
        
        quotients, result = convert2base(35, 36)
        assert result == 'Z'
        assert self.base_to_decimal(result, 36) == 35
    
    def test_negative_base_conversion(self):
        """Test conversion to negative bases."""
        # Negative base conversions produce positive representations
        quotients, result = convert2base(10, -2)
        # For base -2, verify the result represents 10
        decimal_value = 0
        for i, char in enumerate(reversed(result)):
            digit = self.char_to_digit(char)
            decimal_value += digit * ((-2) ** i)
        assert decimal_value == 10
        
        quotients, result = convert2base(-10, -2)
        decimal_value = 0
        for i, char in enumerate(reversed(result)):
            digit = self.char_to_digit(char)
            decimal_value += digit * ((-2) ** i)
        assert decimal_value == -10
    
    def test_zero_conversion(self):
        """Test conversion of zero to various bases."""
        for base in [2, 8, 10, 16, -2, -10]:
            quotients, result = convert2base(0, base)
            assert result == '0'
            assert quotients == [0]
    
    def test_one_conversion(self):
        """Test conversion of 1 to various bases."""
        for base in [2, 8, 10, 16, 36]:
            quotients, result = convert2base(1, base)
            assert result == '1'
            assert self.base_to_decimal(result, base) == 1
    
    @pytest.mark.parametrize("number,base,expected", [
        (8, 8, '10'),
        (7, 8, '7'),
        (64, 8, '100'),
        (10, 10, '10'),
        (100, 10, '100'),
        (10, 3, '101'),
        (26, 26, '10'),
        (27, 27, '10'),
    ])
    def test_specific_conversions(self, number, base, expected):
        """Test specific number and base combinations."""
        quotients, result = convert2base(number, base)
        assert result == expected
        if base > 0:
            assert self.base_to_decimal(result, base) == number
    
    def test_quotient_list(self):
        """Test that quotient list is correctly generated."""
        quotients, result = convert2base(10, 2)
        # Verify quotients match the division process
        assert quotients[-1] == 0  # Last quotient should be 0
        
        quotients, result = convert2base(255, 16)
        assert quotients[-1] == 0
    
    @pytest.mark.parametrize("number", [1, 10, 100, 1000, 12345])
    @pytest.mark.parametrize("base", [2, 3, 8, 10, 16, 36])
    def test_round_trip_positive_bases(self, number, base):
        """Test that conversion and back produces original number."""
        quotients, result = convert2base(number, base)
        recovered = self.base_to_decimal(result, base)
        assert recovered == number
    
    @pytest.mark.parametrize("number", [-1, -10, -100, -1000])
    @pytest.mark.parametrize("base", [2, 8, 16])
    def test_round_trip_negative_numbers(self, number, base):
        """Test negative number conversions with positive bases."""
        quotients, result = convert2base(number, base)
        assert result.startswith('-')
        recovered = self.base_to_decimal(result, base)
        assert recovered == number
    
    def test_large_numbers(self):
        """Test conversion of large numbers."""
        quotients, result = convert2base(1000000, 16)
        assert self.base_to_decimal(result, 16) == 1000000
        
        quotients, result = convert2base(999999999, 36)
        assert self.base_to_decimal(result, 36) == 999999999