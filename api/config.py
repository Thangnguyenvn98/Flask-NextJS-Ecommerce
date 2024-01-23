from decouple import config

class Config:
    SECRET_KEY=config('SECRET_KEY')
    SQLALCHEMY_TRACk_MODIFICATIONS=config('SQLALCHEMY_TRACk_MODIFICATIONS',cast=bool)


class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI=config('CONNECTION')
    DEBUG=True
    SQLALCHEMY_ECHO=True

