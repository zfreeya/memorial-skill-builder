from dataclasses import dataclass


@dataclass
class Settings:
    app_name: str = "LeftMan Skill System"
    default_policy_pack: str = "default"
    default_retention_days: int = 365
    max_recall_items: int = 8
    data_dir: str = "data/runtime"
