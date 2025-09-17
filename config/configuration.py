
from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    te_base_url : str = "https://api.thousandeyes.com/v7/"
    te_token : str

    org_id: int = 138579
    aid: int = 150378

    window_size: int = 30


    @property
    def te_headers(self) -> dict:
        return {'Content-Type': 'application/json', 'Authorization': f'Bearer {self.te_token}'}
    
    @property
    def te_headers_hal(self) -> dict:
        return {'Accept': 'application/hal+json', 'Authorization': f'Bearer {self.te_token}'}
    


config = Config()