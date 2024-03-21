#!/usr/bin/python3

from flask import Flask, jsonify
from flask import request
from config import Config
from repository import Repository
import datetime
import sys
import os

CONFIG_PATH = './data/config.xml'

repo : Repository
app = Flask(__name__)

def ok(nested: dict = {}):
    return jsonify({ **{ 'status': 0 } , **nested })

def fail(msg: str, nested: dict = {}):
    return jsonify({**{ 'status': 1, 'message': msg }, **nested })

@app.route('/api/films', methods=['GET'])
def get_films_by_date():
    date = datetime.date.fromisoformat(request.args['date'])
    sessions = repo.get_sessions_by_day(date)
    res = {}
    films = set()
    res['sessions'] = []
    for s in sessions:
        films.add(str(s.film_id))
        res['sessions'].append({
            'id': str(s.id),
            'film_id': str(s.film_id),
            'time': str(s.time)
        })
    res['films'] = {}
    for fid in films:
        film = repo.get_film_by_id(fid)
        res['films'][fid] = {
            'name': film.name,
            'age': film.age,
            'duration': film.duration,
            'genres': [g.name for g in film.genres]
        }
    return ok(res)

@app.route('/api/film/<string:id>/preview', methods=['GET'])
def get_film_preview(id: str):
    film = repo.get_film_by_id(id)
    if not film:
        return fail('unknown film')
    return ok({'data': bytes(film.preview).hex()})

@app.route('/api/film/new', methods=['POST'])
def create_film():
    film = request.json
    try:
        id = repo.add_film(
            film['name'],
            int(film['duration']),
            age=int(film['age']) if 'age' in film else None,
            genres=film['genres'] if 'genres' in film else [],
        )
    except Exception as e:
        return fail(f'failed to create new film: {e}')
    return ok({'id': id})

@app.route('/api/session/new', methods=['POST'])
def create_session():
    js = request.json
    try:
        film_id = js['film_id']
        dt = datetime.datetime.fromisoformat(js['date'])
        id = repo.add_session(film_id, dt)
    except Exception as e:
        return fail(f'failed to create new session: {e}')
    return ok({'id': id})

@app.route('/api/film/<string:id>/preview', methods=['PATCH'])
def upload_preview(id: str):
    try:
        repo.update_film_preview(id, request.data)
    except Exception as e:
        return fail(f'failed to upload preview: {e}')
    return ok()

@app.route('/api/film/<string:id>', methods=['DELETE'])
def delete_film_by_id(id: str):
    try:
        repo.remove_film(id)
    except Exception as e:
        return fail(str(e))
    return ok()

@app.route('/api/session/<string:id>', methods=['DELETE'])
def delete_session_by_id(id: str):
    try:
        repo.remove_session(id)
    except Exception as e:
        return fail(str(e))
    return ok()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        CONFIG_PATH = sys.argv[1]

    config = Config.create_from_file(CONFIG_PATH)
    if not os.path.exists(config.db_path):
        with open(config.db_path, 'w'): pass
    
    repo = Repository(config.db_path)
    repo.upload_config(config)
    app.run(port=8000)