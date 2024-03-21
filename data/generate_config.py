import sys

if __name__ == "__main__":
    if len(sys.argv) < 6:
        raise RuntimeError("not enough arguments")
    
    input_config_path   = sys.argv[1]
    output_config_path  = sys.argv[2]
    db_path             = sys.argv[3]
    assets_path         = sys.argv[4]
    default_preview     = sys.argv[5]

    with open(input_config_path, encoding='utf-8') as cfg:
        content = cfg.read()
    upd = content.format(db_path, assets_path, default_preview)

    with open(output_config_path, 'w', encoding='utf-8') as cfg:
        cfg.write(upd)
