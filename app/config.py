from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Configuration
    API_BASE_URL: str = "https://swapi.teamontherun.com"
    CLIENT_ID: str = "31343_43lzb3vngtmokww8wcws48w4oss044s044o4gkcocks4s0k44c"
    CLIENT_SECRET: str = "64po82nnwssosgo80wo88osok4so8kc4s8cgowkcsgc80wcoss"
    USERNAME: str = "bradleycooper888@gmail.com"
    PASSWORD: str = "Not4afish1234!"
    TOKEN_TYPE: str = "sw_organization_all_data"
    SCOPE: str = "processes provisioning"
    GROUP_ID: str = "14926"

    # Database Configuration
    DB_SERVER: str = "172.31.6.34"
    DB_NAME: str = "CHILI_PROD"
    DB_USER: str = "chiliadmin"
    DB_PASSWORD: str = "h77pc0l0"
    DB_PORT: str = "1433"

    class Config:
        env_file = ".env"

settings = Settings() 