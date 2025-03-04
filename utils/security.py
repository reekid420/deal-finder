import os
import time
import hashlib
import base64
import hmac
import secrets
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from utils.config import SECURITY

class SecurityManager:
    def __init__(self):
        """Initialize the security manager"""
        self.request_log = {}
        self.login_attempts = {}
        self._initialize_encryption_key()
    
    def _initialize_encryption_key(self):
        """Initialize or load encryption key for sensitive data"""
        key_file = ".encryption_key"
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                self.key = f.read()
        else:
            # Generate a new key
            self.key = Fernet.generate_key()
            # Save the key (in production, store this securely)
            with open(key_file, "wb") as f:
                f.write(self.key)
        
        self.cipher = Fernet(self.key)
    
    def encrypt_data(self, data):
        """Encrypt sensitive data"""
        if not SECURITY["api_key_encryption"]:
            return data
            
        if isinstance(data, str):
            data = data.encode()
        encrypted_data = self.cipher.encrypt(data)
        return encrypted_data
    
    def decrypt_data(self, encrypted_data):
        """Decrypt sensitive data"""
        if not SECURITY["api_key_encryption"]:
            return encrypted_data
            
        if isinstance(encrypted_data, str):
            encrypted_data = encrypted_data.encode()
        decrypted_data = self.cipher.decrypt(encrypted_data)
        return decrypted_data.decode()
    
    def rate_limit_check(self, ip_address):
        """
        Check if a request should be rate limited
        
        Args:
            ip_address (str): The requester's IP address
            
        Returns:
            bool: True if allowed, False if rate limited
        """
        if not SECURITY["rate_limiting"]["enabled"]:
            return True
            
        current_time = time.time()
        max_requests = SECURITY["rate_limiting"]["max_requests_per_minute"]
        
        # Initialize if this is a new IP
        if ip_address not in self.request_log:
            self.request_log[ip_address] = []
        
        # Clean up old requests (older than 1 minute)
        self.request_log[ip_address] = [t for t in self.request_log[ip_address] 
                                        if current_time - t < 60]
        
        # Check if limit exceeded
        if len(self.request_log[ip_address]) >= max_requests:
            return False
            
        # Log the request
        self.request_log[ip_address].append(current_time)
        return True
    
    def validate_login_attempt(self, username, ip_address):
        """
        Check if login should be allowed based on previous attempts
        
        Args:
            username (str): The username attempting to login
            ip_address (str): The requester's IP address
            
        Returns:
            bool: True if allowed, False if too many failed attempts
        """
        key = f"{username}:{ip_address}"
        max_attempts = SECURITY["max_login_attempts"]
        
        if key not in self.login_attempts:
            self.login_attempts[key] = {"count": 0, "lockout_until": None}
            
        # Check if currently locked out
        if (self.login_attempts[key]["lockout_until"] and 
            datetime.now() < self.login_attempts[key]["lockout_until"]):
            return False
            
        # Reset lockout if it has expired
        if (self.login_attempts[key]["lockout_until"] and 
            datetime.now() >= self.login_attempts[key]["lockout_until"]):
            self.login_attempts[key] = {"count": 0, "lockout_until": None}
            
        # Check if max attempts reached
        if self.login_attempts[key]["count"] >= max_attempts:
            # Lock for 15 minutes
            self.login_attempts[key]["lockout_until"] = datetime.now() + timedelta(minutes=15)
            return False
            
        return True
    
    def record_failed_login(self, username, ip_address):
        """Record a failed login attempt"""
        key = f"{username}:{ip_address}"
        
        if key not in self.login_attempts:
            self.login_attempts[key] = {"count": 0, "lockout_until": None}
            
        self.login_attempts[key]["count"] += 1
    
    def reset_login_attempts(self, username, ip_address):
        """Reset login attempts after successful login"""
        key = f"{username}:{ip_address}"
        
        if key in self.login_attempts:
            self.login_attempts[key] = {"count": 0, "lockout_until": None}
    
    def generate_csrf_token(self):
        """Generate a CSRF token for form protection"""
        return secrets.token_hex(32)
    
    def validate_csrf_token(self, session_token, form_token):
        """Validate a CSRF token"""
        if not session_token or not form_token:
            return False
        return hmac.compare_digest(session_token, form_token)
    
    def sanitize_input(self, user_input):
        """Basic sanitization of user input"""
        if not user_input:
            return ""
            
        # Remove potentially dangerous characters
        sanitized = user_input.replace("<", "&lt;").replace(">", "&gt;")
        sanitized = sanitized.replace("'", "&#39;").replace('"', "&quot;")
        sanitized = sanitized.replace(";", "&#59;")
        
        return sanitized
    
    def get_secure_headers(self):
        """Get security headers for responses"""
        return SECURITY["headers"]

# Initialize global security manager
security_manager = SecurityManager() 