
install:
	./bin/pip install https://github.com/Supervisor/supervisor/archive/master.zip
	./bin/pip install -r requirements.txt
	./bin/python setup.py develop

run-zeoserver:
	./bin/runzeo -a 127.0.0.1:5001 -f data.fs

run-monitor:
	./bin/run-monitor

run-server:
	./bin/run-server
