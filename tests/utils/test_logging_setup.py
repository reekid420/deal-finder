"""
Tests for the logging_setup module
"""

import os
import sys
import pytest
import logging
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from loguru import logger

from utils.logging_setup import setup_logging, SCREENSHOT_PATH, HTML_PATH


class TestLoggingSetup:
    
    @pytest.fixture
    def setup_temp_dir(self):
        """Set up temporary directory for logs"""
        # Create temp directory
        temp_dir = tempfile.mkdtemp()
        log_dir = Path(temp_dir) / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # Save original path
        original_dir = os.getcwd()
        
        # Patch Path to use the temp directory
        with patch('utils.logging_setup.Path', autospec=True) as mock_path:
            mock_path.return_value.mkdir.return_value = None
            mock_path.return_value.__truediv__.return_value = log_dir
            yield temp_dir
            
        # Clean up
        os.chdir(original_dir)
        shutil.rmtree(temp_dir)
    
    def test_setup_logging_creates_directories(self):
        """Test that setup_logging creates necessary directories"""
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            setup_logging()
            
            # Verify directories were created
            assert mock_mkdir.call_count >= 2  # Should create at least logs and screenshots dirs
    
    def test_setup_logging_configures_logger(self):
        """Test that setup_logging configures the logger correctly"""
        with patch('loguru.logger.add') as mock_add:
            with patch('pathlib.Path.mkdir'):
                setup_logging()
                
                # Verify logger.add was called at least 3 times (stderr, main log, error log)
                assert mock_add.call_count >= 3
                
                # Verify the calls to logger.add include expected parameters
                for call_args in mock_add.call_args_list:
                    args, kwargs = call_args
                    
                    # Check console handler
                    if len(args) > 0 and args[0] == sys.stderr:
                        assert 'level' in kwargs
                        assert 'colorize' in kwargs
                        assert kwargs['colorize'] is True
                    
                    # Check file handlers
                    if len(args) > 0 and isinstance(args[0], str):
                        if 'errors.log' in args[0]:
                            assert kwargs.get('level') == 'WARNING'
                            assert 'filter' in kwargs
                        else:
                            assert 'level' in kwargs
                            assert 'rotation' in kwargs
                            assert 'compression' in kwargs
    
    def test_setup_logging_registers_exception_handler(self):
        """Test that setup_logging registers an exception handler"""
        original_excepthook = sys.excepthook
        
        try:
            with patch('pathlib.Path.mkdir'):
                setup_logging()
                
                # Verify excepthook was changed
                assert sys.excepthook != original_excepthook
                
                # Test the exception handler with a test exception
                try:
                    with patch('loguru.logger.opt') as mock_logger_opt:
                        mock_error = MagicMock()
                        mock_logger_opt.return_value.error = mock_error
                        
                        # Trigger the exception handler with a test exception
                        test_exception = ValueError("Test exception")
                        sys.excepthook(ValueError, test_exception, None)
                        
                        # Verify logger.opt().error was called
                        mock_error.assert_called_once()
                except Exception as e:
                    pytest.fail(f"Exception handler test failed: {e}")
        finally:
            # Restore original excepthook
            sys.excepthook = original_excepthook
    
    def test_setup_logging_handles_keyboard_interrupt(self):
        """Test that setup_logging exception handler handles KeyboardInterrupt"""
        original_excepthook = sys.excepthook
        original_sys_excepthook = sys.__excepthook__
        
        mock_sys_excepthook = MagicMock()
        sys.__excepthook__ = mock_sys_excepthook
        
        try:
            with patch('pathlib.Path.mkdir'):
                setup_logging()
                
                # Trigger the exception handler with KeyboardInterrupt
                sys.excepthook(KeyboardInterrupt, KeyboardInterrupt(), None)
                
                # Verify sys.__excepthook__ was called
                mock_sys_excepthook.assert_called_once()
        finally:
            # Restore original hooks
            sys.excepthook = original_excepthook
            sys.__excepthook__ = original_sys_excepthook
    
    def test_intercept_handler(self):
        """Test the InterceptHandler class"""
        with patch('pathlib.Path.mkdir'):
            with patch('loguru.logger.opt') as mock_logger_opt:
                mock_log = MagicMock()
                mock_logger_opt.return_value.log = mock_log
                
                setup_logging()
                
                # Create a standard logging record
                record = logging.LogRecord(
                    name="test_logger",
                    level=logging.ERROR,
                    pathname=__file__,
                    lineno=42,
                    msg="Test log message",
                    args=(),
                    exc_info=None
                )
                
                # Get the InterceptHandler instance
                intercept_handler = None
                for handler in logging.getLogger().handlers:
                    if handler.__class__.__name__ == 'InterceptHandler':
                        intercept_handler = handler
                        break
                
                assert intercept_handler is not None, "InterceptHandler not found"
                
                # Emit the record through the handler
                intercept_handler.emit(record)
                
                # Verify logger.opt().log was called
                mock_logger_opt.assert_called_once()
                mock_log.assert_called_once()
    
    def test_constants(self):
        """Test that the module-level constants are defined correctly"""
        assert SCREENSHOT_PATH is not None
        assert HTML_PATH is not None
        
        # Verify paths use the correct directory structure
        assert "logs/screenshots" in SCREENSHOT_PATH
        assert "logs" in HTML_PATH
    
    def test_setup_logging_with_custom_config(self):
        """Test setup_logging with custom configuration"""
        # Mock the LOGGING config
        mock_config = {
            "log_level": "DEBUG",
            "log_format": "CUSTOM FORMAT {message}",
            "max_log_size": 5242880,  # 5MB
            "backup_count": 3
        }
        
        with patch('utils.logging_setup.LOGGING', mock_config):
            with patch('loguru.logger.add') as mock_add:
                with patch('pathlib.Path.mkdir'):
                    setup_logging()
                    
                    # Verify logger was configured with custom settings
                    for call_args in mock_add.call_args_list:
                        args, kwargs = call_args
                        if 'level' in kwargs:
                            # The console and main log should use DEBUG level
                            if args[0] == sys.stderr or 'crawler.log' in args[0]:
                                assert kwargs['level'] == 'DEBUG'
                        
                        if 'format' in kwargs:
                            assert kwargs['format'] == "CUSTOM FORMAT {message}"
                        
                        if 'rotation' in kwargs:
                            assert kwargs['rotation'] == 5242880
                        
                        if 'retention' in kwargs:
                            assert kwargs['retention'] == 3 