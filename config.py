class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:psql@localhost:5432/postgres'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'super-secret'
