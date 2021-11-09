from typing import Any
from typing import Dict


class Meta:
    count: int
    newest_id: int
    oldest_id: int
    next_token: str

    @classmethod
    def build_obj(cls, obj: Dict[str, Any]) -> "Meta":
        """Build object"""
        new = cls()
        new.count = obj["count"]
        new.newest_id = obj["newest_id"]
        new.oldest_id = obj["oldest_id"]
        new.next_token = obj.get("next_token", "")
        return new
