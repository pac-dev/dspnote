#!/usr/bin/env python3

from distutils.core import setup

setup(
	name='dspnote',
	version='1.0',
	description='Static Site Generator with Interactive Figures',
	author_email='pierre@osar.fr',
	url='https://github.com/pac/dspnote',
	scripts=['bin/dspnote-gen'],
	install_requires=[
		'jinja2',
		'pyyaml',
		'markdown',
	]
)
