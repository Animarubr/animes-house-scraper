from typing import Optional, List, Dict
from httpx import Request
import httpx

class Session:
    
    def __init__(self):
        self.http = httpx.Client(follow_redirects=True)
        # self.started = False

    def _make_request(
        self,
        method: str,
        url: str,
        headers: Dict=dict(),
        params: Dict=dict(),
        data=None
    ) -> Request:
        try:
            
            with self.http as http:
                r = http.request(method, url, headers=headers,
                params=params, data=data)
            
            return r
            
        except Exception as e:
            self.http.close()
            raise e
