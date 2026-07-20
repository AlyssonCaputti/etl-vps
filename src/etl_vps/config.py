from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class DatabaseSettings(BaseSettings):
    # 1. Cada atributo = uma variável de ambiente esperada.
    #    O type hint (: str, : int) é a REGRA de validação.
    host: str  # obrigatório — sem default → erro se faltar
    port: int = 3306  # opcional — tem default
    user: str
    password: str
    name: str

    # 2. Config: de onde ler e como mapear nomes.
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_prefix="DB_",  # host → procura DB_HOST no .env automaticamente
    )


db_settings = DatabaseSettings()
