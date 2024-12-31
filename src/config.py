from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

load_dotenv()


class Config(BaseSettings):
    anthropic_api_key: str = Field(alias="anthropic_api_key")
