from app.config import settings

def test_settings():
    print("API Settings:")
    print(f"API_BASE_URL: {settings.API_BASE_URL}")
    print(f"CLIENT_ID: {settings.CLIENT_ID}")
    print(f"TOKEN_TYPE: {settings.TOKEN_TYPE}")
    print(f"SCOPE: {settings.SCOPE}")
    print("\nDatabase Settings:")
    print(f"DB_SERVER: {settings.DB_SERVER}")
    print(f"DB_NAME: {settings.DB_NAME}")
    print(f"API Token URL: {settings.api_token_url}")

if __name__ == "__main__":
    test_settings() 