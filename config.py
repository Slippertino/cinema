import os
import untangle

class Config:
    def __init__(self) -> None:
        self.db_path = ''
        self.db_script = ''
        self.assets_dir = ''
        self.default_preview_name = ''
        self.films = {}
        self.sessions = {}
    
    @classmethod
    def create_from_file(cls, cfg_path: str):
        cfg_dir = os.path.dirname(cfg_path)
        config = untangle.parse(cfg_path).config
        cfg = cls()
        cfg.db_path = os.path.abspath(os.path.join(cfg_dir, config.db['connection_string']))
        cfg.assets_dir = os.path.abspath(os.path.join(cfg_dir, config.films['assets_directory']))
        cfg.default_preview_name = config.films['default_preview']
        cfg.films = config.films
        cfg.sessions = config.schedule
        return cfg