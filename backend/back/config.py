import os
from dataclasses import dataclass


@dataclass
class AppConfig:
    database_url: str = ""
    default_role: str = "researcher"

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            database_url=os.getenv("DATABASE_URL", "").strip(),
            default_role=os.getenv("DEFAULT_ROLE", "researcher").strip()
            or "researcher",
        )
