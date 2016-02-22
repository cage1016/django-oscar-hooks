#!/usr/bin/env python
from setuptools import setup, find_packages

from hooks import VERSION

setup(
    name='django-oscar-hook',
    version=VERSION,
    url='https://github.com/cage1016/django-oscar-hooks',
    author="KAI CHU CHUNG",
    author_email="cage.chung@gamil.com",
    description=(
      "Managed signal for django-oscar"),
    long_description=open('README.md').read(),
    keywords="Signal, Hook, Oscar",
    license=open('LICENSE').read(),
    platforms=['Mac'],
    packages=find_packages(exclude=['sandbox*', 'tests*']),
    include_package_data=True,
    install_requires=[
      'requests>=1.0',
      'django-jsonfield>=0.9.15',
      'slugify>=0.0.1',
      'django-localflavor',
      'redis>=2.10.5',
      'django_q>=0.7.15'
    ],
    extras_require={
      'oscar': ["django-oscar>=1.1"]
    },
    # See http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
      'Development Status :: 1 - Dev',
      'Environment :: Web Environment',
      'Framework :: Django',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: BSD License',
      'Operating System :: Unix',
      'Programming Language :: Python',
      'Programming Language :: Python :: 2',
      'Programming Language :: Python :: 2.7',
      'Topic :: Other/Nonlisted Topic'],
)
