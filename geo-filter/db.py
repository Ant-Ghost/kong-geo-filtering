from pydantic import BaseModel
from typing import List, Dict

class InMemoryDatabase(BaseModel):
    blacklist_countries: List[str] = []
    whitelist_countries: List[str] = []
    whitelist_ips: List[str] = []
    