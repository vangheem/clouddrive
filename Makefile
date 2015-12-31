
install:
	./bin/pip install https://github.com/Supervisor/supervisor/archive/master.zip
	./bin/pip install -r requirements.txt
	./bin/python setup.py develop

run:
	./bin/supervisord
