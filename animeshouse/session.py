from typing import Dict
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
        print(url, end=" -> ")
        request = self.http.build_request(method, url, headers=headers, params=params, data=data)
        
        while request is not None:
            res = self.http.send(request)
            print(f"status: {res.status_code}")
            return res
        
        # with self.http as http:
        #     r = http.request(method, url, headers=headers,params=params, data=data)                
        # return r
        