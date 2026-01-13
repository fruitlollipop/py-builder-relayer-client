"""
HTTP client for API communication
"""

import json
from typing import Dict, Any, Optional
import requests
from requests import Response


# HTTP method constants
GET = "GET"
POST = "POST"
DELETE = "DELETE"
PUT = "PUT"

QueryParams = Dict[str, Any]


class RequestOptions:
    def __init__(self, headers: Optional[Dict[str, str]] = None, 
                 data: Optional[Any] = None, 
                 params: Optional[QueryParams] = None):
        self.headers = headers
        self.data = data
        self.params = params


class HttpClient:
    """HTTP client for making requests to the relayer API"""
    
    def __init__(self):
        self.session = requests.Session()
        # Set default headers for credentials
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
    
    def send(self, endpoint: str, method: str, options: Optional[RequestOptions] = None) -> Response:
        """
        Send HTTP request
        
        Args:
            endpoint: The URL endpoint
            method: HTTP method (GET, POST, etc.)
            options: Request options (headers, data, params)
            
        Returns:
            Response object
            
        Raises:
            Exception: On request errors
        """
        headers = {}
        data = None
        params = None
        
        if options:
            if options.headers:
                headers.update(options.headers)
                # Add CORS headers if needed
                headers["Access-Control-Allow-Credentials"] = "true"
            
            if options.data:
                if isinstance(options.data, dict):
                    data = json.dumps(options.data)
                else:
                    data = options.data
            
            if options.params:
                params = options.params
        
        try:
            response = self.session.request(
                method=method,
                url=endpoint,
                headers=headers,
                data=data,
                params=params
            )
            
            # Don't raise for status here, let caller handle
            return response
            
        except requests.exceptions.RequestException as err:
            if hasattr(err, 'response') and err.response is not None:
                # Response error
                error_payload = {
                    "error": "request error",
                    "status": err.response.status_code,
                    "statusText": err.response.reason,
                    "data": err.response.text,
                }
                print(f"request error: {error_payload}")
                raise Exception(json.dumps(error_payload))
            else:
                # Connection error
                error_payload = {"error": "connection error"}
                print(f"connection error: {error_payload}")
                raise Exception(json.dumps(error_payload))