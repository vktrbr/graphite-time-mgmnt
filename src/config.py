from pathlib import Path
from typing import Optional

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings

import dotenv

dotenv.load_dotenv()


class BaseConfig(BaseSettings):
    """
    A base config class for your DS project that:
      - Reads environment variables from .env
      - Allows overriding any field via environment variables or code
    """

    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")

    mlflow_tracking_uri: Optional[str] = Field(
        default="http://localhost:8080", alias="MLFLOW_TRACKING_URI"
    )
    mlflow_experiment_name: Optional[str] = Field(
        default="experiment", alias="MLFLOW_EXPERIMENT_NAME"
    )

    proj_root: Optional[Path] = None
    data_dir: Optional[Path] = None
    raw_data_dir: Optional[Path] = None
    interim_data_dir: Optional[Path] = None
    processed_data_dir: Optional[Path] = None
    external_data_dir: Optional[Path] = None
    models_dir: Optional[Path] = None
    reports_dir: Optional[Path] = None
    figures_dir: Optional[Path] = None
    src_dir: Optional[Path] = None

    random_state: int = Field(default=42, alias="RANDOM_STATE")
    anthropic_api_key: Optional[str] = Field(alias="ANTHROPIC_API_KEY")
    jira_api_key: Optional[str] = Field(alias="JIRA_API_KEY")
    jira_domain: Optional[str] = Field(alias="JIRA_DOMAIN")
    jira_project_key: Optional[str] = Field(alias="JIRA_PROJECT_KEY")

    @model_validator(mode="after")
    def set_default_paths(self) -> "BaseConfig":
        """
        If a path was not explicitly provided, set defaults based on proj_root.
        """
        if self.proj_root is None:
            self.proj_root = (
                Path(__file__).resolve().parent.parent
            )  # e.g., going one parent up

        self._set_data_paths()
        self._set_misc_paths()

        return self

    def _set_data_paths(self):
        if self.data_dir is None:
            self.data_dir = self.proj_root / "data"
        if self.raw_data_dir is None:
            self.raw_data_dir = self.data_dir / "raw"
        if self.interim_data_dir is None:
            self.interim_data_dir = self.data_dir / "interim"
        if self.processed_data_dir is None:
            self.processed_data_dir = self.data_dir / "processed"
        if self.external_data_dir is None:
            self.external_data_dir = self.data_dir / "external"

    def _set_misc_paths(self):
        if self.models_dir is None:
            self.models_dir = self.proj_root / "models"
        if self.reports_dir is None:
            self.reports_dir = self.proj_root / "reports"
        if self.figures_dir is None:
            self.figures_dir = self.reports_dir / "figures"
        if self.src_dir is None:
            self.src_dir = self.proj_root / "src"
