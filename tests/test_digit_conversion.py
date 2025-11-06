import pytest
from base_converter import digit_to_char


class TestDigitToChar:
    """Test the digit_to_char function for converting digits to character representation."""
    
    def test_single_digits(self):
        """Test conversion of single digits 0-9."""
        for digit in range(10):
            assert digit_to_char(digit) == str(digit)
    
    def test_letter_digits(self):
        """Test conversion of digits 10-35 to letters A-Z."""
        expected_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        for i, expected in enumerate(expected_chars):
            assert digit_to_char(i + 10) == expected
    
    def test_all_valid_digits(self):
        """Test all valid digit values 0-35."""
        expected = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        for i, expected_char in enumerate(expected):
            assert digit_to_char(i) == expected_char
    
    @pytest.mark.parametrize("digit,expected", [
        (0, '0'), (9, '9'),
        (10, 'A'), (15, 'F'),
        (20, 'K'), (25, 'P'),
        (30, 'U'), (35, 'Z'),
    ])
    def test_specific_conversions(self, digit, expected):
        """Test specific digit to character conversions."""
        assert digit_to_char(digit) == expected