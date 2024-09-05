class Config:
    # SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:psql@localhost/public'
    # SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:psql@127.0.0.1:5432/public'
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:psql@localhost:5432/postgres'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'super-secret'
