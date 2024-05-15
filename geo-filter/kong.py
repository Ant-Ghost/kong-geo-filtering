import requests
import os
from typing import List
from pydantic import BaseModel
from db import InMemoryDatabase

KONG_ADMIN_URL = os.environ.get("KONG_ADMIN_URL")
BASE_URL = os.environ.get("BASE_URL")

if KONG_ADMIN_URL is None:
    exit(1)
    
if BASE_URL is None:
    exit(1)
    
class KongConsumer(BaseModel):
    name: str
    id: str
    
class KongService(BaseModel):
    name: str
    id: str

class KongRoutes(BaseModel):
    name: str
    id: str
    routes: List[str]

class KongApiAdmin:
    
    def __init__(self, app_name: str, routes: List[str], database: InMemoryDatabase) -> None:
        
        temp_consumer = self.create_consumer(f"{app_name}_consumer")  
        assert temp_consumer is not None, "Consumer creation failed"
        self.consumer = temp_consumer
        
        temp_service = self.create_service(f"{app_name}_service", BASE_URL)  
        assert temp_service is not None, "Service Creation failed"
        self.service = temp_service
        
        temp_routes = self.create_route( self.service.name, routes, f"{app_name}_routes")  
        assert temp_routes is not None, "Routes Creation/Update failed"
        self.routes = temp_routes
        
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
        
        res = requests.post(f'{KONG_ADMIN_URL}/services', data=data)
        
        print("Create Service:", res.status_code)
        
        if res.status_code < 300:
            return KongService(name=name, id=(res.json()).id)
        return None
    
    def check_service(self, name)-> KongService | None:
        res = requests.get(f'{KONG_ADMIN_URL}/services/{name}')
        
        if res.status_code == 404:
            return None
        return KongService(name=name, id=(res.json()).id)
        
    
    def create_route(self, service_name: str, paths: List[str], name: str)-> KongRoutes | None:
        
        check_existence = self.check_route(service_name=service_name, name=name)
        
        if(check_existence):
            data = {
                "paths":paths,
            }
            
            res = requests.patch(f'{KONG_ADMIN_URL}/services/{service_name}/routes/{name}', data=data)
            
            print("Create Route:", res.status_code)
            
            if res.status_code < 300:
                check_existence.routes = paths
            return check_existence
        else:
            data = {
                "name": name,
                "paths":paths,
            }
            
            res = requests.post(f'{KONG_ADMIN_URL}/services/{service_name}/routes', data=data)
            
            print("Create Route:", res.status_code)
            
            if res.status_code < 300:
                return KongRoutes(name=name, id=(res.json()).id, routes=paths)
            return None
        
    def check_route(self, service_name, name)-> KongRoutes | None:
        res = requests.get(f'{KONG_ADMIN_URL}/services/{service_name}/routes/{name}')
        
        if res.status_code == 404:
            return None
        return KongRoutes(name=name, id=(res.json()).id, routes=(res.json()).paths)
        
    
    def create_consumer(self, username: str)-> KongConsumer | None:
        
        check_existence = self.check_consumer(username)
        
        if(check_existence):
            return check_existence
        
        data = {
            "username": username,
        }
        
        res = requests.post(f'{KONG_ADMIN_URL}/consumers', data=data)
        
        print("Create Service:", res.status_code)
        
        if res.status_code < 300:
            return KongConsumer(name=username, id=(res.json()).id)
        else:
            return None
        
    
    def check_consumer(self, name)-> KongConsumer | None:
        res = requests.get(f'{KONG_ADMIN_URL}/consumers/{name}')
        
        if res.status_code == 404:
            return None
        return KongConsumer(name=name, id=(res.json()).id)
    
    def acitvate_plugin(self, mode: str, blacklist: List[str] = [], whitelist: List[str]=[]) -> str | None:
        
        if self.plugin_id:    
        
            check_existence = self.check_plugin(self.plugin_id)
            
            if(check_existence):
                res = requests.patch(
                    f'{KONG_ADMIN_URL}/consumers/{self.consumer.name}/plugins/{self.plugin_id}',
                    data = {
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
                    return str((res.json()).id)
                return None
            
        res = requests.post(
            f'{KONG_ADMIN_URL}/consumers/{self.consumer.name}/plugins',
            data = {
                "name": "gaius-geoip",
                "route": {
                    "id":self.routes.id
                },
                "service": {
                    "id":self.service.id
                },
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
            return str((res.json()).id)
        return None
        
    
    def check_plugin(self, plugin_id: str) -> str | None:
        
        res = requests.get(
            f'{KONG_ADMIN_URL}/consumers/{self.consumer.name}/plugins/{plugin_id}',
        )
        
        if res.status_code == 404:
            return None
        return (res.json()).id