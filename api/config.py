from decouple import config

class Config:
    SECRET_KEY=config('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS=config('SQLALCHEMY_TRACK_MODIFICATIONS',cast=bool)



class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI=config('DATABASE_URL')
    DEBUG=True
    SQLALCHEMY_ECHO=True
    

