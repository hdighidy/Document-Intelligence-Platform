from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Document Intelligence Platform"
    max_file_size_mb: int = 50
    allowed_extensions: tuple[str, ...] = (".pdf",)



    # Create a base data directory for storing raw, metadata, and processed files from main.py
    base_data_dir: Path = Path("data") # Create a base data directory for storing raw, metadata, and processed files

    raw_dir: Path = base_data_dir / "raw" # Create a subdirectory for storing raw files
    metadata_dir: Path = base_data_dir / "metadata" # Create a subdirectory for storing metadata files
    processed_dir: Path = base_data_dir / "processed" # Create a subdirectory for storing processed files


    def create_directories(self) -> None:
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()

settings.create_directories()