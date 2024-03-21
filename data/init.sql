CREATE TABLE IF NOT EXISTS films
(
    id TEXT NOT NULL,
    name TEXT NOT NULL,
    age INTEGER DEFAULT 12,
    duration INTEGER NOT NULL,
    preview BLOB,
    CONSTRAINT films_pk PRIMARY KEY(id),
    CONSTRAINT film_name_uq UNIQUE(name),
    CONSTRAINT film_age_chk CHECK(age > 0 AND age < 150),
    CONSTRAINT film_duration_chk CHECK(duration > 0)
);

CREATE TABLE IF NOT EXISTS genres
(
    id TEXT NOT NULL,
    name TEXT NOT NULL,
    CONSTRAINT genres_pk PRIMARY KEY(id),
    CONSTRAINT genres_name_uq UNIQUE(name)
);

CREATE TABLE IF NOT EXISTS films_genres
(
    film_id TEXT NOT NULL,
    genre_id TEXT NOT NULL,
    CONSTRAINT films_genres_pk PRIMARY KEY(film_id, genre_id)
    CONSTRAINT films_genres_films_fk FOREIGN KEY (film_id) REFERENCES films(id) ON DELETE CASCADE
    CONSTRAINT films_genres_genres_fk FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS sessions
(
    id TEXT NOT NULL,
    film_id TEXT,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    CONSTRAINT sessions_pk PRIMARY KEY(id),
    CONSTRAINT sessions_film_uq UNIQUE(film_id, date, time)
    CONSTRAINT sessions_films_fk FOREIGN KEY(film_id) REFERENCES films(id) ON DELETE SET NULL
);