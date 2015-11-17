DIR?=noteit


relise: clean
	rm -rf $(DIR)
	mkdir $(DIR)
	pyminifier --gzip client/__init__.py > $(DIR)/noteit
	cp $(DIR)/noteit $(DIR)/__init__.py


clean:
	find . -name *.pyc -delete
	rm -rf $(shell find . -name __pycache__) build *.egg-info dist