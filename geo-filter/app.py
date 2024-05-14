from flask import Flask, request, Response
from flask_cors import CORS
from db import InMemoryDatabase
from typing import List, Dict
import json

database = InMemoryDatabase()

app = Flask(__name__)
CORS(app, origins=["http://localhost:8080"])

@app.route("/", methods=["GET"])
def hello():
    return "Hello World"

@app.route("/restriction/<mode>", methods=["GET", "PATCH"])
def fetch_or_update_website_configuration(mode: str):
    
    if request.method == "GET":
        valid_list = []
        
        if(mode == "blacklist"):
            valid_list = database.blacklist_countries
        elif(mode == "whitelist"):
            valid_list = database.whitelist_countries
            
        res = { "list": valid_list }
        
        return Response( json.dumps(res), 200 )
    else:
        body : Dict[str, List[str]] = request.get_json()
        valid_list: List[str] | None = body.get("valid_list")
        
        if valid_list is None:
            return Response("valid_list required", 400)
        
        if(mode == "blacklist"):
            database.blacklist_countries = valid_list
        elif(mode == "whitelist"):
            database.whitelist_countries = valid_list
            
        return Response( None, 204 )
        
    