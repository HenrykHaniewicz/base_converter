import pytest
from base_converter import convert2base, partition_quotient, digit_to_char


class TestIntegration:
    """Integration tests to verify the complete conversion process."""
    
    def verify_conversion(self, decimal, base):
        """Helper to verify conversion is mathematically correct."""
        _, result = convert2base(decimal, base)
        
        # Handle negative numbers with positive bases
        if result.startswith('-'):
            sign = -1
            result = result[1:]
        else:
            sign = 1
        
        # Convert back to decimal
        reconstructed = 0
        for i, char in enumerate(reversed(result)):
            if char.isdigit():
                digit = int(char)
            else:
                digit = ord(char) - ord('A') + 10
            
            if base > 0:
                reconstructed += digit * (base ** i)
            else:
                reconstructed += digit * (base ** i)
        
        return sign * reconstructed == decimal
    
    @pytest.mark.parametrize("decimal,base", [
        (42, 2), (42, 8), (42, 16), (42, 36),
        (100, 2), (100, 10), (100, 16),
        (1000, 2), (1000, 8), (1000, 16), (1000, 36),
        (-42, 2), (-42, 8), (-42, 16),
        (0, 2), (0, 16), (0, 36),
        (1, 2), (1, 16), (1, 36),
    ])
    def test_positive_base_conversions(self, decimal, base):
        """Test that conversions with positive bases are correct."""
        assert self.verify_conversion(decimal, base)
    
    def test_known_conversions(self):
        """Test specific known conversions."""
        test_cases = [
            (255, 16, 'FF'),
            (256, 16, '100'),
            (10, 2, '1010'),
            (8, 8, '10'),
            (1000, 10, '1000'),
            (35, 36, 'Z'),
            (36, 36, '10'),
            (-10, 2, '-1010'),
            (-255, 16, '-FF'),
        ]
        
        for decimal, base, expected in test_cases:
            _, result = convert2base(decimal, base)
            assert result == expected
    
    def test_negative_base_property(self):
        """Test that negative bases produce valid representations."""
        # For negative bases, the result should still represent the original number
        for number in [1, 10, -1, -10, 42, -42]:
            for base in [-2, -3, -10, -16]:
                _, result = convert2base(number, base)
                
                # Verify by reconstructing
                reconstructed = 0
                for i, char in enumerate(reversed(result)):
                    if char.isdigit():
                        digit = int(char)
                    else:
                        digit = ord(char) - ord('A') + 10
                    reconstructed += digit * (base ** i)
                
                assert reconstructed == number, f"Failed for {number} in base {base}"
    
    def test_chain_conversions(self):
        """Test that partition_quotient, digit_to_char, and convert2base work together."""
        # Manually compute 42 in base 16
        quotients = []
        remainders = []
        
        n = 42
        base = 16
        
        while n != 0:
            if n == -1:
                q, r = partition_quotient(n, base, minusone=True)
            else:
                q, r = partition_quotient(n, base)
            quotients.append(q)
            remainders.append(r)
            n = q
        
        # Convert remainders to string
        result = ''
        for r in reversed(remainders):
            result += digit_to_char(r)
        
        # Compare with convert2base
        _, automatic_result = convert2base(42, 16)
        assert result == automatic_result == '2A'
    
    @pytest.mark.parametrize("base", [2, 3, 5, 7, 11, 13, 16, 20, 36])
    def test_powers_of_base(self, base):
        """Test conversion of powers of the base."""
        for power in range(5):
            number = abs(base) ** power
            _, result = convert2base(number, base)
            
            if base > 0:
                # Should be '1' followed by 'power' zeros
                expected = '1' + '0' * power
                assert result == expected