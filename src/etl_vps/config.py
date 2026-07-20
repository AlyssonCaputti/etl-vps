from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class PathSettings(BaseModel):
    base_path: Path = Path(
        r"P:\Marketing\Marketing 2026\Dados - Dashboards\dados integração\Y - Dados que vão para a VPS"
    )
    backup_dir: Path = Path(
        r"P:\Marketing\Marketing 2026\Dados - Dashboards\dados integração\_backup"
    )


class DatabaseSettings(BaseSettings):
    # 1. Cada atributo = uma variável de ambiente esperada.
    #    O type hint (: str, : int) é a REGRA de validação.
    host: str  # obrigatório — sem default → erro se faltar
    port: int = 3306
    user: str
    password: str
    name: str

    # 2. Config: de onde ler e como mapear nomes.
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_prefix="DB_",  # host → procura DB_HOST no .env automaticamente
    )


db_settings = DatabaseSettings()
paths = PathSettings()
