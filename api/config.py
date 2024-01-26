from decouple import config

class Config:
    SECRET_KEY=config('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS=config('SQLALCHEMY_TRACK_MODIFICATIONS',cast=bool)



class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI=config('DATABASE_URL')
    DEBUG=True
    SQLALCHEMY_ECHO=True
    # AUTH0_DOMAIN=config('AUTH0_DOMAIN')
    # AUTH0_CLIENT_ID=config('AUTH0_CLIENT_ID')
    # AUTH0_CLIENT_SECRET=config('AUTH0_CLIENT_SECRET')
    # AUTH0_API_AUDIENCE=config('AUTH0_API_AUDIENCE')
    

