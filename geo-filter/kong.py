import requests
import os
from typing import List
from pydantic import BaseModel
from db import InMemoryDatabase
import random

KONG_ADMIN_URL = os.environ.get("KONG_ADMIN_URL")
BASE_URL = os.environ.get("BASE_URL")

assert KONG_ADMIN_URL is not None, "Please, set KONG_ADMIN_URL env"
    
assert BASE_URL is not None, "Please, set BASE_URL env"

print("BASE_URLS:", KONG_ADMIN_URL, BASE_URL)
    
class KongService(BaseModel):
    name: str
    id: str

class KongRoutes(BaseModel):
    name: str
    id: str
    routes: List[str]

class KongApiAdmin:
    
    def __init__(self, app_name: str, routes: List[str], database: InMemoryDatabase) -> None:
        
        temp_service = self.create_service(f"{app_name}_service_{random.randint(10,1000)}", BASE_URL)  
        assert temp_service is not None, "Service Creation failed"
        self.service = temp_service
        
        temp_routes = self.create_route( self.service.name, routes, f"{app_name}_routes_{random.randint(10,1000)}")  
        assert temp_routes is not None, "Routes Creation/Update failed"
        self.routes = temp_routes
        
        self.plugin_id : str | None = None
        temp_plugin_id = self.acitvate_plugin(database.mode, database.blacklist_countries, database.whitelist_countries)
        assert temp_plugin_id is not None, "Plugin Creation failed"
        self.plugin_id = temp_plugin_id


    def create_service(self, name: str, url: str) -> KongService | None:
        
        check_existence = self.check_service(name)
        
        if(check_existence):
            return check_existence
        
        data = {
            "name": name,
            "url":url,
        }
        
        res = requests.post(f'{KONG_ADMIN_URL}/services', json=data)
        
        print("Creation Service:", res.status_code, res.json(), );
        
        if res.status_code < 300:
            return KongService(name=name, id=(res.json()).get("id"))
        return None
    
    def check_service(self, name)-> KongService | None:
        res = requests.get(f'{KONG_ADMIN_URL}/services/{name}')
        
        if res.status_code == 404:
            return None
        return KongService(name=name, id=(res.json()).get("id"))
        
    
    def create_route(self, service_name: str, paths: List[str], name: str)-> KongRoutes | None:
        
        check_existence = self.check_route(service_name=service_name, name=name)
        
        if(check_existence):
            data = {
                "paths":paths,
            }
            
            res = requests.patch(f'{KONG_ADMIN_URL}/services/{service_name}/routes/{name}', json=data)
            
            if res.status_code < 300:
                check_existence.routes = paths
            return check_existence
        else:
            data = {
                "name": name,
                "paths":paths,
            }
            
            res = requests.post(f'{KONG_ADMIN_URL}/services/{service_name}/routes', json=data)
            
            if res.status_code < 300:
                return KongRoutes(name=name, id=(res.json()).get("id"), routes=paths)
            return None
        
    def check_route(self, service_name, name)-> KongRoutes | None:
        res = requests.get(f'{KONG_ADMIN_URL}/services/{service_name}/routes/{name}')
        
        if res.status_code == 404:
            return None
        return KongRoutes(name=name, id=(res.json()).get("id"), routes=(res.json()).get("paths"))
        
    
    def acitvate_plugin(self, mode: str, blacklist: List[str] = [], whitelist: List[str]=[]) -> str | None:
        
        if self.plugin_id:
            print("Plugin Present")
        
            check_existence = self.check_plugin(self.plugin_id)
            
            if(check_existence):
                res = requests.patch(
                    f'{KONG_ADMIN_URL}/routes/{self.routes.name}/plugins/{self.plugin_id}',
                    json = {
                        "config": {
                            "inject_country_header": "X-COUNTRY",
                            "whitelist_countries": whitelist,
                            "blacklist_countries": blacklist,
                            "mode": mode,
                            "whitelist_ips": []
                        }
                    }
                )
                
                if res.status_code < 300:
                    return str((res.json()).get("id"))
                return None
        
        res = requests.post(
            f'{KONG_ADMIN_URL}/routes/{self.routes.name}/plugins',
            json = {
                "name": "gaius-geoip",
                "config": {
                    "inject_country_header": "X-COUNTRY",
                    "whitelist_countries": whitelist,
                    "blacklist_countries": blacklist,
                    "mode": mode,
                    "whitelist_ips": []
                }
            }
        )
        
        print(res.status_code, res.json())
        
        if res.status_code < 300:
            return str((res.json()).get("id"))
        return None
        
    
    def check_plugin(self, plugin_id: str) -> str | None:
        
        res = requests.get(
            f'{KONG_ADMIN_URL}/routes/{self.routes.name}/plugins/{plugin_id}',
        )
        
        if res.status_code == 404:
            return None
        return (res.json()).get("id")