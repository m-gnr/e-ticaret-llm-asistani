from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_yaml_config(relative_path: str) -> dict[str, Any]:
    """
    Proje kök dizinine göre YAML config dosyasını okur.

    Örnek:
        load_yaml_config("config/database.yaml")
        load_yaml_config("config/model.yaml")
        load_yaml_config("config/search.yaml")
    """
    config_path = PROJECT_ROOT / relative_path

    if not config_path.exists():
        raise FileNotFoundError(f"Config dosyası bulunamadı: {config_path}")

    with config_path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if data is None:
        return {}

    return data


def get_project_root() -> Path:
    """
    Proje kök dizinini döndürür.
    """
    return PROJECT_ROOT