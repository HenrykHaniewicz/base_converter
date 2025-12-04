# Convert between any bases from -36 to 36 (excluding -1, 0, 1)
# Supports decimal numbers with arbitrary precision
# For negative bases, this algorithm produces the principal value (positive remainders)

import sys
import argparse
from decimal import Decimal, getcontext, ROUND_DOWN

# Check if PyQt6 is available for GUI support
try:
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                 QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                                 QSpinBox, QCheckBox, QTextEdit, QMessageBox,
                                 QDialog, QDialogButtonBox, QScrollArea, QFrame)
    from PyQt6.QtCore import Qt, QTimer
    from PyQt6.QtGui import QFont, QFontMetrics, QPalette, QColor, QLinearGradient
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

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
    results = []
    
    # Show original number if from_base is not 10
    if from_base != 10:
        results.append(f'Number in base {from_base}: \t{original_number_str}')
    
    results.append(f'Number in base 10: \t{base10_number}\n')
    results.append('-' * 60)
    
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
        results.append(f'Number in base {base:3}: \t{display_result}')
    
    results.append('-' * 60)
    return '\n'.join(results)

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

# GUI Classes
if GUI_AVAILABLE:
    class ResultWindow(QDialog):
        """Window to display conversion results"""
        def __init__(self, output_text, parent=None):
            super().__init__(parent)
            self.setWindowTitle("Conversion Results")
            self.output_text = output_text
            self.initUI()
            
        def initUI(self):
            # Apply stylesheet for results window
            self.setStyleSheet("""
                QDialog {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                        stop:0 #2C3E50, stop:1 #34495E);
                }
                QTextEdit {
                    background-color: #1E1E2E;
                    color: #A6E3A1;
                    border: 2px solid #4A5568;
                    border-radius: 8px;
                    padding: 10px;
                    selection-background-color: #4A5568;
                }
                QPushButton {
                    background-color: #48BB78;
                    color: white;
                    border: none;
                    padding: 8px 20px;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #38A169;
                }
                QPushButton:pressed {
                    background-color: #2F855A;
                }
            """)
            
            # Calculate optimal window size
            lines = self.output_text.split('\n')
            max_line_length = max(len(line) for line in lines if line)
            
            # Start with default size
            width = 800
            min_font_size = 12
            max_font_size = 20
            
            # Test if content fits with minimum font
            font = QFont("Courier", min_font_size)
            metrics = QFontMetrics(font)
            max_width_needed = max(metrics.horizontalAdvance(line) for line in lines if line) + 50  # padding
            
            # Adjust window width if needed (up to maximum of 1000)
            if max_width_needed > width:
                width = min(max_width_needed, 1000)
            
            self.setGeometry(200, 200, width, 500)
            
            layout = QVBoxLayout()
            layout.setSpacing(10)
            layout.setContentsMargins(15, 15, 15, 15)
            
            # Title label
            title = QLabel("Conversion Results")
            title.setStyleSheet("""
                QLabel {
                    color: #A6E3A1;
                    font-size: 16px;
                    font-weight: bold;
                    padding: 5px;
                }
            """)
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title)
            
            # Create scrollable text area
            self.text_output = QTextEdit()
            self.text_output.setReadOnly(True)
            self.text_output.setPlainText(self.output_text)
            
            # Calculate optimal font size based on content and window width
            self.adjustFontSize(width)
            
            layout.addWidget(self.text_output)
            
            # Add OK button
            ok_button = QPushButton("OK")
            ok_button.clicked.connect(self.accept)
            ok_button.setCursor(Qt.CursorShape.PointingHandCursor)
            
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            button_layout.addWidget(ok_button)
            button_layout.addStretch()
            
            layout.addLayout(button_layout)
            self.setLayout(layout)
        
        def adjustFontSize(self, window_width):
            """Dynamically adjust font size to fit content width"""
            lines = self.output_text.split('\n')
            max_line_length = max(len(line) for line in lines if line)
            
            # Set font size range with minimum of 12
            font_size = 14
            max_font_size = 20
            min_font_size = 12
            
            # Available width accounting for margins, padding, and scrollbar
            available_width = window_width - 80
            
            # Binary search for optimal font size
            while max_font_size - min_font_size > 1:
                font = QFont("Courier", font_size)
                metrics = QFontMetrics(font)
                
                # Calculate the width of the longest line
                max_width = max(metrics.horizontalAdvance(line) for line in lines if line)
                
                if max_width < available_width * 0.95:  # Try to fill 95% of available space
                    min_font_size = font_size
                else:
                    max_font_size = font_size
                
                font_size = (min_font_size + max_font_size) // 2
            
            # Apply the optimal font size (never less than 12)
            final_font = QFont("Courier", max(min_font_size, 12))
            self.text_output.setFont(final_font)
    
    class CustomSpinBox(QSpinBox):
        """Custom SpinBox that allows typing invalid intermediate values"""
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setRange(-36, 36)
            self._typing = False
            self._timer = QTimer()
            self._timer.timeout.connect(self._validate_typed_value)
            self._timer.setSingleShot(True)
            
        def keyPressEvent(self, event):
            """Handle key press events to allow typing"""
            # Mark that we're typing
            self._typing = True
            super().keyPressEvent(event)
            # Start/restart timer to validate after typing stops
            self._timer.stop()
            self._timer.start(1000)  # Validate after 1 second of no typing
            
        def _validate_typed_value(self):
            """Validate the typed value after typing stops"""
            self._typing = False
            value = self.value()
            if value in [-1, 0, 1]:
                # Jump to nearest valid value
                if value == 0:
                    self.setValue(2)
                elif value == 1:
                    self.setValue(2)
                elif value == -1:
                    self.setValue(-2)
        
        def stepBy(self, steps):
            """Override stepBy to skip invalid values when using arrows"""
            current = self.value()
            new_value = current + steps
            
            # Skip invalid values
            if new_value in [-1, 0, 1]:
                if steps > 0:
                    if new_value == -1:
                        new_value = 2
                    else:
                        new_value = 2
                else:
                    if new_value == 1:
                        new_value = -2
                    else:
                        new_value = -2
            
            self.setValue(new_value)
    
    class BaseConverterGUI(QMainWindow):
        """Main GUI window for the base converter"""
        def __init__(self):
            super().__init__()
            self.initUI()
        
        def initUI(self):
            self.setWindowTitle("Base Converter")
            self.setGeometry(100, 100, 600, 450)
            
            # Apply modern stylesheet
            self.setStyleSheet("""
                QMainWindow {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                        stop:0 #667EEA, stop:1 #764BA2);
                }
                QLabel {
                    color: white;
                    font-size: 13px;
                    font-weight: 500;
                }
                QLineEdit {
                    background-color: rgba(255, 255, 255, 0.9);
                    border: 2px solid #4A5568;
                    border-radius: 5px;
                    padding: 8px;
                    font-size: 12px;
                    color: #2D3748;
                }
                QLineEdit:focus {
                    border-color: #667EEA;
                    background-color: white;
                }
                QSpinBox {
                    background-color: rgba(255, 255, 255, 0.9);
                    border: 2px solid #4A5568;
                    border-radius: 5px;
                    padding: 5px;
                    font-size: 12px;
                    color: #2D3748;
                }
                QSpinBox:focus {
                    border-color: #667EEA;
                    background-color: white;
                }
                QCheckBox {
                    color: white;
                    font-size: 12px;
                    spacing: 5px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    background-color: rgba(255, 255, 255, 0.9);
                    border: 2px solid #4A5568;
                    border-radius: 3px;
                }
                QCheckBox::indicator:checked {
                    background-color: #48BB78;
                    border-color: #48BB78;
                }
                QPushButton {
                    background-color: #48BB78;
                    color: white;
                    border: none;
                    padding: 10px 30px;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #38A169;
                }
                QPushButton:pressed {
                    background-color: #2F855A;
                }
            """)
            
            # Create central widget and layout
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            main_layout = QVBoxLayout(central_widget)
            main_layout.setSpacing(15)
            main_layout.setContentsMargins(30, 30, 30, 30)
            
            # Title with larger font
            title = QLabel("Base m → Base n Converter")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 24px;
                    font-weight: bold;
                    padding: 10px;
                    background-color: rgba(0, 0, 0, 0.2);
                    border-radius: 10px;
                }
            """)
            main_layout.addWidget(title)
            
            # Create a frame for the input fields
            input_frame = QFrame()
            input_frame.setStyleSheet("""
                QFrame {
                    background-color: rgba(255, 255, 255, 0.1);
                    border-radius: 10px;
                    padding: 10px;
                }
            """)
            input_layout = QVBoxLayout(input_frame)
            input_layout.setSpacing(12)
            
            # Input number
            number_layout = QHBoxLayout()
            number_label = QLabel("Number:")
            number_label.setMinimumWidth(100)
            self.number_input = QLineEdit()
            self.number_input.setPlaceholderText("Enter number (e.g., 42, FF, 3.14159)")
            number_layout.addWidget(number_label)
            number_layout.addWidget(self.number_input)
            input_layout.addLayout(number_layout)
            
            # From base
            from_layout = QHBoxLayout()
            from_label = QLabel("From base:")
            from_label.setMinimumWidth(100)
            self.from_base = CustomSpinBox()
            self.from_base.setValue(10)
            self.from_base.setMaximumWidth(100)
            from_layout.addWidget(from_label)
            from_layout.addWidget(self.from_base)
            from_layout.addStretch()
            input_layout.addLayout(from_layout)
            
            # To base
            to_layout = QHBoxLayout()
            to_label = QLabel("To base:")
            to_label.setMinimumWidth(100)
            self.to_base = CustomSpinBox()
            self.to_base.setValue(2)
            self.to_base.setMaximumWidth(100)
            self.to_base.valueChanged.connect(self.on_to_base_changed)
            to_layout.addWidget(to_label)
            to_layout.addWidget(self.to_base)
            to_layout.addStretch()
            input_layout.addLayout(to_layout)
            
            # Precision
            prec_layout = QHBoxLayout()
            prec_label = QLabel("Precision:")
            prec_label.setMinimumWidth(100)
            self.precision = QSpinBox()
            self.precision.setRange(1, 1000)
            self.precision.setValue(50)
            self.precision.setSuffix(" digits")
            self.precision.setMaximumWidth(150)
            prec_layout.addWidget(prec_label)
            prec_layout.addWidget(self.precision)
            prec_layout.addStretch()
            input_layout.addLayout(prec_layout)
            
            main_layout.addWidget(input_frame)
            
            # Options frame
            options_frame = QFrame()
            options_frame.setStyleSheet("""
                QFrame {
                    background-color: rgba(255, 255, 255, 0.1);
                    border-radius: 10px;
                    padding: 10px;
                }
            """)
            options_layout = QVBoxLayout(options_frame)
            
            options_label = QLabel("Options:")
            options_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            options_layout.addWidget(options_label)
            
            self.all_bases = QCheckBox("Show all bases (-36 to 36)")
            self.all_bases.toggled.connect(self.on_all_bases_toggled)
            self.all_bases.setCursor(Qt.CursorShape.PointingHandCursor)
            options_layout.addWidget(self.all_bases)
            
            self.positive_only = QCheckBox("Show positive bases only (2 to 36)")
            self.positive_only.toggled.connect(self.on_positive_only_toggled)
            self.positive_only.setCursor(Qt.CursorShape.PointingHandCursor)
            options_layout.addWidget(self.positive_only)
            
            main_layout.addWidget(options_frame)
            
            # Convert button
            main_layout.addStretch()
            self.convert_button = QPushButton("Convert")
            self.convert_button.clicked.connect(self.perform_conversion)
            self.convert_button.setDefault(True)
            self.convert_button.setCursor(Qt.CursorShape.PointingHandCursor)
            
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            button_layout.addWidget(self.convert_button)
            button_layout.addStretch()
            main_layout.addLayout(button_layout)
            
            # Status label
            self.status_label = QLabel("")
            self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.status_label.setStyleSheet("color: #FED7D7; font-weight: bold;")
            main_layout.addWidget(self.status_label)
        
        def on_to_base_changed(self, value):
            """When to_base is changed, uncheck the checkboxes"""
            if self.to_base.isEnabled():
                # User is interacting with the to_base spinbox, uncheck boxes
                self.all_bases.setChecked(False)
                self.positive_only.setChecked(False)
        
        def on_all_bases_toggled(self, checked):
            """Handle all bases checkbox toggle"""
            if checked:
                self.positive_only.setChecked(False)
                # Grey out but don't disable
                self.to_base.setStyleSheet("""
                    QSpinBox {
                        background-color: rgba(200, 200, 200, 0.5);
                        color: #888888;
                    }
                """)
            else:
                # Restore normal appearance
                self.to_base.setStyleSheet("""
                    QSpinBox {
                        background-color: rgba(255, 255, 255, 0.9);
                        border: 2px solid #4A5568;
                        border-radius: 5px;
                        padding: 5px;
                        font-size: 12px;
                        color: #2D3748;
                    }
                    QSpinBox:focus {
                        border-color: #667EEA;
                        background-color: white;
                    }
                """)
        
        def on_positive_only_toggled(self, checked):
            """Handle positive only checkbox toggle"""
            if checked:
                self.all_bases.setChecked(False)
                # Grey out but don't disable
                self.to_base.setStyleSheet("""
                    QSpinBox {
                        background-color: rgba(200, 200, 200, 0.5);
                        color: #888888;
                    }
                """)
            else:
                # Restore normal appearance
                self.to_base.setStyleSheet("""
                    QSpinBox {
                        background-color: rgba(255, 255, 255, 0.9);
                        border: 2px solid #4A5568;
                        border-radius: 5px;
                        padding: 5px;
                        font-size: 12px;
                        color: #2D3748;
                    }
                    QSpinBox:focus {
                        border-color: #667EEA;
                        background-color: white;
                    }
                """)
        
        def perform_conversion(self):
            """Perform the conversion and display results"""
            try:
                # Clear status
                self.status_label.setText("")
                
                # Get input values
                number_str = self.number_input.text().strip()
                if not number_str:
                    raise ValueError("Please enter a number")
                
                from_base = self.from_base.value()
                to_base = self.to_base.value()
                precision = self.precision.value()
                
                # Validate bases
                error = validate_base(from_base)
                if error:
                    raise ValueError(f"Invalid from-base: {error}")
                
                if not self.all_bases.isChecked() and not self.positive_only.isChecked():
                    error = validate_base(to_base)
                    if error:
                        raise ValueError(f"Invalid to-base: {error}")
                
                # Set global precision
                getcontext().prec = precision + 100
                
                # Convert to base 10
                base10_number = convert_from_base(number_str, from_base, precision)
                
                # Perform conversion
                if self.all_bases.isChecked():
                    output = convert_all_bases(number_str, from_base, base10_number, 
                                              positive_only=False, precision=precision)
                elif self.positive_only.isChecked():
                    output = convert_all_bases(number_str, from_base, base10_number, 
                                              positive_only=True, precision=precision)
                else:
                    result = convert_to_base(base10_number, to_base, precision)
                    output = f'Number in base {from_base}: \t{number_str}\n'
                    output += f'Number in base 10: \t{base10_number}\n'
                    output += f'Number in base {to_base}: \t{result}'
                
                # Display results in new window
                result_window = ResultWindow(output, self)
                result_window.exec()
                
            except ValueError as e:
                QMessageBox.critical(self, "Error", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(e)}")

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
  %(prog)s --gui                      Launch GUI interface

Notes:
  - For negative bases, numbers must be the principal (positive) value
  - Repeating decimals are shown with parentheses: 0.1(6) = 0.1666...
  - Letters A-Z represent digits 10-35 (case insensitive)
        """
    )
    
    # Add GUI flag
    parser.add_argument(
        '--gui',
        action='store_true',
        help='Launch GUI interface for conversion'
    )
    
    parser.add_argument(
        'number',
        type=str,
        nargs='?',  # Make optional when using --gui
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
    
    # Check if GUI is requested
    if args.gui:
        if not GUI_AVAILABLE:
            parser.error("GUI requires PyQt6. Please install it with: pip install PyQt6")
        return args
    
    # If not using GUI, number is required
    if not args.number:
        parser.error("the following arguments are required: number")
    
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
    
    # Launch GUI if requested
    if args.gui:
        app = QApplication(sys.argv)
        window = BaseConverterGUI()
        window.show()
        sys.exit(app.exec())
    
    # Otherwise, run command-line version
    # Set global precision
    getcontext().prec = args.precision + 100
    
    # Convert from source base to base 10
    try:
        base10_number = convert_from_base(args.number, args.from_base, args.precision)
    except ValueError as e:
        print(f"\nError: {e}\n", file=sys.stderr)
        sys.exit(1)
    
    if args.all:
        output = convert_all_bases(args.number, args.from_base, base10_number, 
                                   positive_only=False, precision=args.precision)
        print(output)
    elif args.allpos:
        output = convert_all_bases(args.number, args.from_base, base10_number, 
                                   positive_only=True, precision=args.precision)
        print(output)
    else:
        result = convert_to_base(base10_number, args.to_base, args.precision)
        print(f'\nNumber in base {args.from_base}: \t{args.number}')
        print(f'Number in base 10: \t{base10_number}')
        print(f'Number in base {args.to_base}: \t{result}\n')