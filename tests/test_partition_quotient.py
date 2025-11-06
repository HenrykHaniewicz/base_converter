import pytest
from base_converter import partition_quotient


class TestPartitionQuotient:
    """Test the partition_quotient function for proper division with non-negative remainders."""
    
    def test_positive_dividend_positive_divisor(self):
        """Test standard positive division."""
        q, r = partition_quotient(10, 3)
        assert q == 3
        assert r == 1
        assert 0 <= r < abs(3)
        # Verify: q * divisor + r = dividend
        assert q * 3 + r == 10
    
    def test_negative_dividend_positive_divisor(self):
        """Test negative dividend with positive divisor."""
        q, r = partition_quotient(-10, 3)
        assert q == -4
        assert r == 2
        assert 0 <= r < abs(3)
        assert q * 3 + r == -10
    
    def test_positive_dividend_negative_divisor(self):
        """Test positive dividend with negative divisor."""
        q, r = partition_quotient(10, -3)
        assert q == -3
        assert r == 1
        assert 0 <= r < abs(-3)
        assert q * (-3) + r == 10
    
    def test_negative_dividend_negative_divisor(self):
        """Test negative dividend with negative divisor."""
        q, r = partition_quotient(-10, -3)
        assert q == 4
        assert r == 2
        assert 0 <= r < abs(-3)
        assert q * (-3) + r == -10
    
    def test_zero_dividend(self):
        """Test division of zero."""
        q, r = partition_quotient(0, 5)
        assert q == 0
        assert r == 0
        assert q * 5 + r == 0
        
        q, r = partition_quotient(0, -5)
        assert q == 0
        assert r == 0
        assert q * (-5) + r == 0
    
    def test_exact_division(self):
        """Test when dividend is exactly divisible."""
        q, r = partition_quotient(12, 3)
        assert q == 4
        assert r == 0
        assert q * 3 + r == 12
        
        q, r = partition_quotient(-12, 3)
        assert q == -4
        assert r == 0
        assert q * 3 + r == -12
    
    def test_minusone_flag(self):
        """Test the minusone flag for special case handling with negative bases."""
        # The minusone flag is a fast-track optimization for when dividend is -1
        # It should only be used with negative bases
        
        # Test with negative base where dividend is -1
        q, r = partition_quotient(-1, -2, minusone=True)
        # When minusone=True: q = (-1 // -2) + 1 = 0 + 1 = 1
        # r = -1 - (1 * -2) = -1 + 2 = 1
        assert q == 1
        assert r == 1
        assert 0 <= r < abs(-2)
        assert q * (-2) + r == -1
        
        # Verify that minusone=True gives the same result as minusone=False
        # (it's just a fast-track, not a different algorithm)
        q_normal, r_normal = partition_quotient(-1, -2, minusone=False)
        q_fast, r_fast = partition_quotient(-1, -2, minusone=True)
        assert q_normal == q_fast
        assert r_normal == r_fast
        
        # Another test with different negative base
        q, r = partition_quotient(-1, -3, minusone=True)
        # When minusone=True: q = (-1 // -3) + 1 = 0 + 1 = 1  
        # r = -1 - (1 * -3) = -1 + 3 = 2
        assert q == 1
        assert r == 2
        assert 0 <= r < abs(-3)
        assert q * (-3) + r == -1
        
        # Verify same result with and without minusone flag
        q_normal, r_normal = partition_quotient(-1, -3, minusone=False)
        q_fast, r_fast = partition_quotient(-1, -3, minusone=True)
        assert q_normal == q_fast
        assert r_normal == r_fast
    
    def test_minusone_flag_with_positive_base_raises_error(self):
        """Test that using minusone flag with positive base raises an error."""
        # The minusone flag should only be used with negative bases
        # since positive bases convert negative numbers to positive first
        with pytest.raises(ValueError) as exc_info:
            partition_quotient(-1, 2, minusone=True)
        assert "minusone flag should only be used with negative bases" in str(exc_info.value)
        
        with pytest.raises(ValueError) as exc_info:
            partition_quotient(-1, 10, minusone=True)
        assert "minusone flag should only be used with negative bases" in str(exc_info.value)

    def test_minusone_flag_with_nonminusone_dividend_raises_error(self):
        """Test that using minusone flag with positive base raises an error."""
        # The minusone flag should only be used with negative bases
        # since positive bases convert negative numbers to positive first
        with pytest.raises(ValueError) as exc_info:
            partition_quotient(-10, 2, minusone=True)
        
        with pytest.raises(ValueError) as exc_info:
            partition_quotient(3, 10, minusone=True)
    
    def test_large_numbers(self):
        """Test with large numbers."""
        q, r = partition_quotient(1000000, 37)
        assert 0 <= r < 37
        assert q * 37 + r == 1000000
        
        q, r = partition_quotient(-1000000, 37)
        assert 0 <= r < 37
        assert q * 37 + r == -1000000
    
    @pytest.mark.parametrize("dividend,divisor", [
        (17, 5), (17, -5), (-17, 5), (-17, -5),
        (100, 7), (100, -7), (-100, 7), (-100, -7),
        (1, 2), (1, -2), (-1, 2), (-1, -2),
    ])
    def test_remainder_always_non_negative(self, dividend, divisor):
        """Ensure remainder is always non-negative regardless of input signs."""
        q, r = partition_quotient(dividend, divisor)
        assert 0 <= r < abs(divisor)
        assert q * divisor + r == dividend