from sqlalchemy import create_engine, ColumnDefault
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import exists
from models import *
from PIL import Image
from config import Config
from datetime import datetime, time, date
import io
import os
import uuid
import sqlite3 as sq

class Repository:
    __normalized_image_width = 100

    def __init__(self, db_path) -> None:
        self.db_path = db_path
        engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(engine)
        maker = sessionmaker(autoflush=False, bind=engine)
        self.db = maker()

    @staticmethod
    def __load_image(dir, name):
        path = os.path.join(dir, name)
        with open(path, 'rb') as image:
            return image.read()
        
    @staticmethod
    def __normalize_image(image: bytes):
        tw = Repository.__normalized_image_width 
        im = Image.open(io.BytesIO(image))
        im = im.resize((tw, (tw * im.height) // im.width))
        res = io.BytesIO()
        im.save(res, format='PNG')
        return res.getvalue()

    def __load_genre(self, name):
        genre = self.db.query(Genre).filter(Genre.name == name).first()
        if not genre:
            genre = Genre(id = str(uuid.uuid4()), name = name)
            self.db.add(genre)
        return genre

    def get_film_by_id(self, id: str) -> Film | None:
        return self.db.query(Film).filter(Film.id == id).first()
    
    def get_film_by_name(self, name: str) -> Film | None:
        return self.db.query(Film).filter(Film.name == name).first()
    
    def get_sessions_by_day(self, date: date) -> list[Session]:
        return self.db.query(Session).filter(Session.date == str(date)).all()
    
    def get_films_names(self):
        return [x.name for x in self.db.query(Film.name).all()]
    
    def add_film(self, name, duration: int, 
        age: int | None = None, 
        preview: bytes | None = None, 
        genres: list[str] = []
    ) -> str:
        film = Film(
            name = name,
            duration = duration,
            genres = [self.__load_genre(nm) for nm in genres]
        )
        if age: film.age = age
        if preview: film.preview = Repository.__normalize_image(preview)
        film_obj = self.db.query(Film.id).filter(Film.name == film.name).first()
        if not film_obj:
            film.id = str(uuid.uuid4())
            self.db.add(film)
            self.db.commit()
            film_obj = film
        return str(film_obj.id)
    
    def update_film_preview(self, id: str, preview: bytes):
        film = self.get_film_by_id(id)
        if not film:
            raise ValueError('unknown film')
        film.preview = Repository.__normalize_image(preview)
        self.db.commit()

    def add_session(self, id: str, time: datetime):
        film = self.get_film_by_id(id)
        if not film:
            raise ValueError('unknown film')
        session = Session(
            film_id = film.id,
            date = str(time.date()),
            time = time.time().strftime('%H:%M')
        )
        session_obj = self.db.query(Session.id).filter(
            Session.film_id == session.film_id, 
            Session.date == session.date,
            Session.time == session.time
        ).first()
        if not session_obj:
            session.id = str(uuid.uuid4())
            self.db.add(session)
            self.db.commit()
            session_obj = session
        return str(session_obj.id)
    
    def remove_film_by_id(self, id: str):
        film = self.get_film_by_id(id)
        if not film:
            raise ValueError('unknown film')
        self.db.delete(film)
        self.db.commit()
    
    def remove_film_by_name(self, name: str):
        film = self.db.query(Film).filter(Film.name == name).first()
        if not film:
            raise ValueError('unknown film')
        self.db.delete(film)
        self.db.commit()

    def remove_session(self, id: str):
        session = self.db.query(Session).filter(Session.id == id).first()
        if not session:
            raise ValueError('unknown session')
        self.db.delete(session)
        self.db.commit()

    def upload_config(self, cfg: Config):
        Film.default_preview = Repository.__load_image(cfg.assets_dir, cfg.default_preview_name)
        films = {}
        for film in cfg.films.children:
            print(f'Film: {film.name.cdata} {[g.cdata for g in film.genres.children]}')
            name = film.name.cdata
            id = self.add_film(
                name,
                int(film.duration.cdata),
                age=int(film.age.cdata),
                preview=Repository.__load_image(cfg.assets_dir, film.preview['name']),
                genres=[g.cdata for g in film.genres.children]
            )
            films[name] = id
        
        for day in cfg.sessions.children:
            dt = date.fromisoformat(str(day['date']))
            for s in day.children:
                film_name = str(s['film'])
                h, m = map(int, str(s['time']).split(':'))
                tm = time(hour=h, minute=m)
                self.add_session(
                    films[film_name],
                    datetime.combine(dt, tm)
                )