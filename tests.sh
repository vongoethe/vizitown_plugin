#!/bin/bash

if hash python2 2>/dev/null; then
	python2 vt_test_converter.py
	python2 vt_test_parser.py
	python2 vt_test_providers.py
	python2 vt_test_tiler.py
else
	python vt_test_converter.py
	python vt_test_parser.py
	python vt_test_providers.py
	python vt_test_tiler.py
fi
