autopep8:
	autopep8 --ignore E501,E241,W690 --in-place --recursive --aggressive portfolioAnalytics/

lint:
	flake8 portfolioAnalytics

autolint: autopep8 lint

