"""
Flask-Messenger

'Messenger api integration for flask.'
"""
from setuptools import setup


setup(
    name='Flask-Messenger',
    version='1.0.0',
    url='http://github.com/cRyp70s/flask-messenger',
    license='MIT',
    author='Matthew Wisdom',
    author_email='matthewwisdom11@gmail.com',
    description='Messenger api integration for Flask.',
    long_description=__doc__,
    py_modules=['flask_messenger'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'requests',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
