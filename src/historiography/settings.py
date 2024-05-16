from pydantic import BaseModel, field_validator, Field
from pathlib import Path
import os

class HistoriographyDatasetConfig(BaseModel):
    output_file_path: Path = Field(default="data/historiography.csv")
    search_queries_file: Path = Field(default="src/historiography/dataset/search_queries.txt")
    articles_per_query: int = Field(default=30, gt=0)
    wait_between_pages: float = 5

    @field_validator('output_file_path')
    def check_output_file_path(cls, file_path: Path) -> Path:
        dir_path = file_path.parent
        if not dir_path.exists():
            raise ValueError(f"The directory for output_file_path '{dir_path}' does not exist.")
        if not os.access(dir_path, os.W_OK):
            raise ValueError(f"The directory '{dir_path}' is not writable.")
        return file_path

    @field_validator('search_queries_file')
    def check_search_queries_file(cls, file_path: Path) -> Path:
        if not file_path.exists():
            raise ValueError(f"The search_queries_file '{file_path}' does not exist.")
        if file_path.stat().st_size == 0:
            raise ValueError(f"The search_queries_file '{file_path}' is empty.")
        return file_path