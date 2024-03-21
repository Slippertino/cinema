from sqlalchemy import Column, Integer, String, ForeignKey, Table, BLOB, UniqueConstraint, PrimaryKeyConstraint
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import validates
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

film_genre = Table(
    'films_genres',
    Base.metadata,
    Column('film_id', String, ForeignKey('films.id', ondelete='cascade')),
    Column('genre_id', String, ForeignKey('genres.id', ondelete='cascade')),
    PrimaryKeyConstraint('film_id', 'genre_id')
)

class Film(Base):
    default_preview = bytes()
    
    __tablename__ = 'films'
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    age = Column(Integer, nullable=True, default=12)
    duration = Column(Integer, nullable=False)
    preview = Column(BLOB, nullable=False, default=lambda: Film.default_preview)
    sessions = relationship('Session', backref=backref('films'))
    genres = relationship('Genre', secondary=film_genre, back_populates='films', cascade='delete')

    @validates('age')
    def validate_age(self, key, value):
        if value < 0 or value > 150:
            raise ValueError('invalid age limit')
        return value
    
    @validates('duration')
    def validate_duration(self, key, value):
        if value <= 0:
            raise ValueError('invalid duration')
        return value

class Genre(Base):
    __tablename__ = 'genres'
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    films = relationship('Film', secondary=film_genre, back_populates='genres', cascade='delete')

class Session(Base):
    __tablename__ = 'sessions'
   
    id = Column(String, primary_key=True)
    film_id = Column(String, ForeignKey('films.id'), nullable=False)
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)

    __table_args__ = (UniqueConstraint(film_id, date, time),)