#!/bin/bash

if hash pep8-python2 2>/dev/null; then
	pep8-python2 --show-source --max-line-length=160 --ignore=W292 --exclude=plugin_upload.py,resources_rc.py,ui_vizitown.py,./cyclone/*,./zope/*,./twisted/*,./help/*,__init__.py, .
else
	pep8 --show-source --max-line-length=160 --ignore=W292 --exclude=plugin_upload.py,resources_rc.py,ui_vizitown.py,./cyclone/*,./zope/*,./twisted/*,./help/*,__init__.py, .
fi
