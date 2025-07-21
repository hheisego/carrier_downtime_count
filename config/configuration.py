import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field


# Cargar las variables de entorno desde el archivo .env
load_dotenv()


class Config(BaseModel):
    
    te_base_url : str = Field("https://api.thousandeyes.com/v7/")
    te_token : str = Field(...)

    org_id: int = Field(138579)
    aid: int = Field(150378)

    window_size: int = Field(..., default=60)


    @property
    def te_headers(self) -> dict:
        return {'Content-Type': 'application/json', 'Authorization': f'Bearer {self.te_token}'}
    
    @property
    def te_headers_hal(self) -> dict:
        return {'Accept': 'application/hal+json', 'Authorization': f'Bearer {self.te_token}'}
    


config = Config()