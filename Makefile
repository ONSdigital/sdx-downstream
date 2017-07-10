dev: check-env
	cd .. && pip3 uninstall -y sdx-common && pip3 install -I ./sdx-common
<<<<<<< HEAD
	pip3 install -r requirements.txt

build:
	git clone https://github.com/ONSdigital/sdx-common.git
	pip3 install ./sdx-common
=======
>>>>>>> addings common functionality and updating timezoning
	pip3 install -r requirements.txt
	rm -rf sdx-common

build:
	pip3 install -I -r requirements.txt
	git clone https://github.com/ONSdigital/sdx-common.git
	pip3 install ./sdx-common
	rm -rf sdx-common

test:
	pip3 install -r test_requirements.txt
	flake8 --exclude ./lib/*
	python3 -m unittest tests/*.py

check-env:
	ifeq ($(SDX_HOME),)
		$(error SDX_HOME is not set)
	endif
