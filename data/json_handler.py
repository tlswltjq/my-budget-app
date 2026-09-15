import json
import os
from typing import Dict, Any, List, Union

class JsonHandler:
    
    @staticmethod
    def read_json(file_path: str) -> Union[Dict[str, Any], List[Any]]:
        if not os.path.exists(file_path):
            return []
        
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except (json.JSONDecodeError, ValueError):
                return []

    @staticmethod
    def write_json(file_path: str, data: Union[Dict[str, Any], List[Any]]) -> None:
        dir_name = os.path.dirname(file_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)