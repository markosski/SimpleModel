from simplemodel import __version__
from distutils.core import setup

setup(
    name='SimpleModel',
    version=__version__,
    author='Marcin Kossakowski',
    author_email='marcin.kossakowski@gmail.com',
    packages=['simplemodel'],
    scripts=[],
    url='git://github.com/martez81/SimpleModel.git',
    license='LICENSE.txt',
    description='Simple Active Record for Mysql.',
    long_description=open('README.txt').read(),
    install_requires=["pydbwrapper >= 0.1.0"]
)