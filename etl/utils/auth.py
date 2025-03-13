"""
Authentication utility for the Mercurios.ai ETL pipeline.
"""
import time
from datetime import datetime, timedelta

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from etl.config.config import API_CONFIG
from etl.utils.logger import logger

class TokenManager:
    """
    Manages the authentication token for the ProHandel API.
    Handles token refreshing automatically.
    """
    
    def __init__(self):
        self.api_key = API_CONFIG["api_key"]
        self.api_secret = API_CONFIG["api_secret"]
        self.auth_url = API_CONFIG["auth_url"]
        self.token = None
        self.token_expiry = None
        self.refresh_minutes = API_CONFIG["token_refresh_minutes"]
        self.server_url = None
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def authenticate(self):
        """
        Authenticate with the ProHandel API and get access token.
        Returns the token value.
        """
        try:
            auth_data = {
                "apiKey": self.api_key,
                "secret": self.api_secret
            }
            
            logger.info(f"Authenticating with ProHandel API at {self.auth_url}...")
            # Use the correct token endpoint - note that the /token part may already be included in the URL
            token_url = self.auth_url if self.auth_url.endswith("/token") else f"{self.auth_url}/token"
            logger.info(f"Using token URL: {token_url}")
            
            response = requests.post(token_url, json=auth_data)
            response.raise_for_status()
            
            auth_response = response.json()
            logger.info(f"Authentication response received: {auth_response.keys()}")
            
            # Handle different token response formats
            if "token" in auth_response and isinstance(auth_response["token"], dict):
                if "token" in auth_response["token"] and "value" in auth_response["token"]["token"]:
                    self.token = auth_response["token"]["token"]["value"]
                    self.token_expiry = datetime.now() + timedelta(seconds=auth_response["token"]["token"]["expiresIn"])
                elif "value" in auth_response["token"]:
                    self.token = auth_response["token"]["value"]
                    self.token_expiry = datetime.now() + timedelta(seconds=auth_response["token"]["expiresIn"])
                
                # Update API URL if provided in the response
                if "serverUrl" in auth_response:
                    logger.info(f"Server URL from response: {auth_response['serverUrl']}")
                    API_CONFIG["api_url"] = auth_response['serverUrl']
                    self.server_url = auth_response['serverUrl']
                    logger.info(f"Updated API URL to: {API_CONFIG['api_url']}")
                
                logger.info(f"Authentication successful. Token expires at {self.token_expiry}")
                return self.token
            elif "accessToken" in auth_response:
                self.token = auth_response["accessToken"]
                self.token_expiry = datetime.now() + timedelta(minutes=self.refresh_minutes)
                logger.info(f"Authentication successful. Token expires at {self.token_expiry}")
                return self.token
            else:
                logger.error(f"Unexpected authentication response format: {auth_response}")
                raise ValueError("Unexpected authentication response format")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Authentication failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                if e.response.content:
                    logger.error(f"Response content: {e.response.content.decode()}")
            raise
    
    def get_token(self):
        """
        Get the current token, refreshing if necessary.
        """
        # If token doesn't exist or is expired, authenticate
        if self.token is None or self.token_expiry is None or datetime.now() >= self.token_expiry:
            self.authenticate()
        return self.token
    
    def get_headers(self):
        """
        Get the headers for API requests, including the authentication token.
        """
        return {
            "Authorization": f"Bearer {self.get_token()}",
            "Content-Type": "application/json"
        }

# Create a singleton instance
token_manager = TokenManager()
