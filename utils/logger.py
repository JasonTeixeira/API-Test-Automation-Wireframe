"""
Custom logging configuration for API test automation framework.

Provides colored console output and structured file logging with request/response sanitization.
"""
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import colorlog


class APILogger:
    """
    Custom logger for API testing with color-coded output and request/response tracking.
    """
    
    def __init__(
        self,
        name: str = "API-Tests",
        level: str = "INFO",
        log_to_file: bool = True,
        log_dir: str = "logs"
    ):
        """
        Initialize the API logger.
        
        Args:
            name: Logger name
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_to_file: Whether to log to file
            log_dir: Directory for log files
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        self.logger.handlers = []  # Clear existing handlers
        
        # Console handler with colors
        console_handler = colorlog.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        
        console_format = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s [%(levelname)8s] %(name)s - %(message)s%(reset)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            }
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # File handler (if enabled)
        if log_to_file:
            log_path = Path(log_dir)
            log_path.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = log_path / f"api_tests_{timestamp}.log"
            
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)
            
            file_format = logging.Formatter(
                "%(asctime)s [%(levelname)8s] %(name)s - %(message)s\n"
                "  File: %(pathname)s:%(lineno)d\n"
                "  Function: %(funcName)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            file_handler.setFormatter(file_format)
            self.logger.addHandler(file_handler)
            
            self.logger.info(f"Logging to file: {log_file}")
    
    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        self.logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""
        self.logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs: Any) -> None:
        """Log critical message."""
        self.logger.critical(message, **kwargs)
    
    def log_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log HTTP request details with sanitization.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            headers: Request headers
            body: Request body
        """
        sanitized_headers = self._sanitize_dict(headers) if headers else {}
        sanitized_body = self._sanitize_dict(body) if body else {}
        
        self.logger.info(f"→ REQUEST: {method} {url}")
        if sanitized_headers:
            self.logger.debug(f"  Headers: {sanitized_headers}")
        if sanitized_body:
            self.logger.debug(f"  Body: {sanitized_body}")
    
    def log_response(
        self,
        status_code: int,
        response_time: float,
        headers: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log HTTP response details.
        
        Args:
            status_code: HTTP status code
            response_time: Response time in seconds
            headers: Response headers
            body: Response body
        """
        color = self._get_status_color(status_code)
        self.logger.info(f"← RESPONSE: {status_code} ({response_time:.3f}s)")
        
        if headers:
            self.logger.debug(f"  Headers: {dict(headers)}")
        if body:
            self.logger.debug(f"  Body: {body}")
    
    def log_test_start(self, test_name: str) -> None:
        """Log the start of a test."""
        self.logger.info(f"{'='*80}")
        self.logger.info(f"▶ Starting test: {test_name}")
        self.logger.info(f"{'='*80}")
    
    def log_test_end(self, test_name: str, status: str = "PASSED") -> None:
        """Log the end of a test."""
        symbol = "✓" if status == "PASSED" else "✗"
        self.logger.info(f"{symbol} Test {status}: {test_name}")
        self.logger.info(f"{'='*80}\n")
    
    def _sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize dictionary by masking sensitive values.
        
        Args:
            data: Dictionary to sanitize
            
        Returns:
            Sanitized dictionary
        """
        sensitive_keys = {"password", "token", "api_key", "secret", "authorization"}
        sanitized = {}
        
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "***REDACTED***"
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _get_status_color(self, status_code: int) -> str:
        """Get color based on HTTP status code."""
        if 200 <= status_code < 300:
            return "green"
        elif 300 <= status_code < 400:
            return "yellow"
        elif 400 <= status_code < 500:
            return "red"
        else:
            return "red"


# Global logger instance
logger = APILogger()
