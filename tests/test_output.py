import pytest
from unittest.mock import patch
from base_converter import convert_all_bases


class TestConvertAllBases:
    """Test the convert_all_bases function."""
    
    def test_all_bases_output(self, capsys):
        """Test output for all bases."""
        convert_all_bases(10, positive_only=False)
        captured = capsys.readouterr()
        
        # Check header
        assert "Original number in base 10: 10" in captured.out
        
        # Check that negative bases are included (with proper spacing)
        assert "base -36:" in captured.out or "base -36 :" in captured.out
        assert "base -2:" in captured.out or "base  -2:" in captured.out
        
        # Check that positive bases are included (note the spacing)
        assert "base   2:" in captured.out or "base  2:" in captured.out
        assert "base  36:" in captured.out
        
        # Verify bases -1, 0, 1 are excluded
        # These bases should not appear in the output at all
        lines = captured.out.split('\n')
        for line in lines:
            if 'Number in base' in line:
                # Extract the base number from the line
                if ':' in line:
                    base_part = line.split(':')[0]
                    if 'base' in base_part:
                        # Get the number after 'base'
                        base_str = base_part.split('base')[1].strip()
                        try:
                            base_num = int(base_str)
                            assert base_num not in [-1, 0, 1], f"Base {base_num} should not be in output"
                        except ValueError:
                            pass  # Skip if can't parse
    
    def test_positive_only_output(self, capsys):
        """Test output for positive bases only."""
        convert_all_bases(10, positive_only=True)
        captured = capsys.readouterr()
        
        # Check header
        assert "Original number in base 10: 10" in captured.out
        
        # Check that positive bases are included with proper formatting
        assert "base   2:" in captured.out
        assert "base  36:" in captured.out
        
        # Check that negative bases are NOT included
        lines = captured.out.split('\n')
        for line in lines:
            if 'Number in base' in line and ':' in line:
                # Should not have any negative sign before the colon
                base_part = line.split(':')[0]
                assert '-' not in base_part, f"Negative base found in positive-only mode: {line}"
    
    def test_zero_all_bases(self, capsys):
        """Test converting zero to all bases."""
        convert_all_bases(0, positive_only=False)
        captured = capsys.readouterr()
        
        # Zero should be '0' in all bases
        lines = captured.out.split('\n')
        for line in lines:
            if 'Number in base' in line and ':' in line:
                # Extract the result after the colon
                result = line.split(':')[-1].strip()
                if result:  # Skip empty lines
                    assert result == '0'
    
    def test_negative_number_all_bases(self, capsys):
        """Test converting negative number to various bases."""
        convert_all_bases(-10, positive_only=False)
        captured = capsys.readouterr()
        
        assert "Original number in base 10: -10" in captured.out
        # For positive bases, should have negative sign
        # Check for -10 in base 2 and base 16
        lines = captured.out.split('\n')
        found_base2 = False
        found_base16 = False
        
        for line in lines:
            if 'base   2:' in line:
                assert '-1010' in line
                found_base2 = True
            elif 'base  16:' in line:
                assert '-A' in line
                found_base16 = True
        
        assert found_base2, "Base 2 conversion not found"
        assert found_base16, "Base 16 conversion not found"
    
    @pytest.mark.parametrize("number", [1, 42, 100, -1, -42, -100])
    def test_output_format(self, number, capsys):
        """Test that output format is consistent."""
        convert_all_bases(number, positive_only=True)
        captured = capsys.readouterr()
        
        lines = captured.out.split('\n')
        # Check for consistent formatting
        base_lines = [l for l in lines if 'Number in base' in l and ':' in l]
        
        # Should have conversions for bases 2-36 (35 bases total)
        assert len(base_lines) == 35
        
        # Each line should have proper formatting
        for line in base_lines:
            assert ':' in line
            assert '\t' in line
            
        # Also check that the header line appears but is not counted
        assert f"Original number in base 10: {number}" in captured.out
    
    def test_formatting_consistency(self, capsys):
        """Test that formatting is consistent across different numbers."""
        convert_all_bases(42, positive_only=True)
        captured = capsys.readouterr()
        
        lines = [l for l in captured.out.split('\n') if 'Number in base' in l and ':' in l]
        
        # Check alignment - all should have consistent spacing
        for line in lines:
            # The format should be "Number in base XXX: \tRESULT"
            assert '\t' in line, f"Tab character missing in: {line}"
            
            # Extract base number to verify formatting
            if ':' in line:
                base_part = line.split(':')[0]
                # Base numbers should be right-aligned in a field of width 3
                # e.g., "base   2", "base  10", "base  36"