from pydantic_settings import BaseSettings


class Settings(BaseSettings):
	app_name: str = "Clinic App"
	secret_key: str = "change-me"
	access_token_expire_minutes: int = 60 * 8
	admin_username: str = "admin"
	admin_password: str = "admin123"
	cookie_name: str = "access_token"
	debug: bool = True

	class Config:
		env_file = ".env"
		env_file_encoding = "utf-8"


settings = Settings()
