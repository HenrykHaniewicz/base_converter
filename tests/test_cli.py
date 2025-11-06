import pytest
import sys
from unittest.mock import patch, MagicMock
from base_converter import parse_args, print_usage


class TestParseArgs:
    """Test command line argument parsing."""
    
    def test_no_arguments(self):
        """Test behavior when no arguments are provided."""
        with patch.object(sys, 'argv', ['base_converter.py']):
            with pytest.raises(SystemExit) as exc_info:
                parse_args()
            assert exc_info.value.code == None or exc_info.value.code == 0
    
    def test_too_many_arguments(self):
        """Test behavior with too many arguments."""
        with patch.object(sys, 'argv', ['base_converter.py', '10', '2', 'extra']):
            with pytest.raises(SystemExit) as exc_info:
                parse_args()
            assert exc_info.value.code == 1
    
    def test_invalid_number(self):
        """Test behavior with invalid number input."""
        with patch.object(sys, 'argv', ['base_converter.py', 'not_a_number']):
            with pytest.raises(SystemExit) as exc_info:
                parse_args()
            assert exc_info.value.code == 1
    
    def test_valid_number_only(self):
        """Test parsing with just a number (default base 2)."""
        with patch.object(sys, 'argv', ['base_converter.py', '42']):
            number, base = parse_args()
            assert number == 42
            assert base == 2
    
    def test_valid_number_and_base(self):
        """Test parsing with number and base."""
        with patch.object(sys, 'argv', ['base_converter.py', '100', '16']):
            number, base = parse_args()
            assert number == 100
            assert base == 16
    
    def test_negative_number(self):
        """Test parsing negative numbers."""
        with patch.object(sys, 'argv', ['base_converter.py', '-42', '8']):
            number, base = parse_args()
            assert number == -42
            assert base == 8
    
    def test_negative_base(self):
        """Test parsing negative bases."""
        with patch.object(sys, 'argv', ['base_converter.py', '42', '-10']):
            number, base = parse_args()
            assert number == 42
            assert base == -10
    
    def test_all_flag(self):
        """Test --all flag."""
        with patch.object(sys, 'argv', ['base_converter.py', '42', '--all']):
            number, flag = parse_args()
            assert number == 42
            assert flag == 'all'
    
    def test_allpos_flag(self):
        """Test --allpos flag."""
        with patch.object(sys, 'argv', ['base_converter.py', '42', '--allpos']):
            number, flag = parse_args()
            assert number == 42
            assert flag == 'allpos'
    
    def test_invalid_base_zero(self):
        """Test that base 0 is rejected."""
        with patch.object(sys, 'argv', ['base_converter.py', '42', '0']):
            with pytest.raises(SystemExit) as exc_info:
                parse_args()
            assert exc_info.value.code == 1
    
    def test_invalid_base_one(self):
        """Test that base 1 is rejected."""
        with patch.object(sys, 'argv', ['base_converter.py', '42', '1']):
            with pytest.raises(SystemExit) as exc_info:
                parse_args()
            assert exc_info.value.code == 1
    
    def test_invalid_base_minus_one(self):
        """Test that base -1 is rejected."""
        with patch.object(sys, 'argv', ['base_converter.py', '42', '-1']):
            with pytest.raises(SystemExit) as exc_info:
                parse_args()
            assert exc_info.value.code == 1
    
    def test_base_out_of_range(self):
        """Test that bases outside ±36 are rejected."""
        with patch.object(sys, 'argv', ['base_converter.py', '42', '37']):
            with pytest.raises(SystemExit) as exc_info:
                parse_args()
            assert exc_info.value.code == 1
        
        with patch.object(sys, 'argv', ['base_converter.py', '42', '-37']):
            with pytest.raises(SystemExit) as exc_info:
                parse_args()
            assert exc_info.value.code == 1
    
    def test_invalid_option(self):
        """Test invalid command line option."""
        with patch.object(sys, 'argv', ['base_converter.py', '42', '--invalid']):
            with pytest.raises(SystemExit) as exc_info:
                parse_args()
            assert exc_info.value.code == 1


class TestPrintUsage:
    """Test the print_usage function."""
    
    def test_print_usage_output(self, capsys):
        """Test that print_usage produces output."""
        print_usage()
        captured = capsys.readouterr()
        assert "Base 10 --> Base n converter" in captured.out
        assert "Usage:" in captured.out
        assert "--all" in captured.out
        assert "--allpos" in captured.out