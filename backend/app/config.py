import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = "Fraud Investigation Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # TigerGraph Settings
    TIGERGRAPH_HOST: str = os.getenv("TIGERGRAPH_HOST", "https://localhost:9000")
    TIGERGRAPH_GRAPH: str = os.getenv("TIGERGRAPH_GRAPH", "FraudInvestigation")
    TIGERGRAPH_USERNAME: str = os.getenv("TIGERGRAPH_USERNAME", "tigergraph")
    TIGERGRAPH_PASSWORD: str = os.getenv("TIGERGRAPH_PASSWORD", "tigergraph")
    TIGERGRAPH_SECRET: str = os.getenv("TIGERGRAPH_SECRET", "")

    # LLM Settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Data paths
    CASE_PACK_PATH: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "case_pack.csv"
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
