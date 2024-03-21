python -m ensurepip --upgrade
pip install pip-tools
pip install pipreqs
pipreqs --savepath=requirements.in
pip-compile
del requirements.in
pip install -r requirements.txt
cd data
.\generate_config .\config.xml.in .\config.xml .\db.db .\assets default.png
cd ..
.\main