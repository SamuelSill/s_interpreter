from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'S Compiler/Interpreter'
LONG_DESCRIPTION = 'A package that makes it easy to compile/interpret the S language'

setup(
    name="s_interpreter",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author="Muli Silman",
    author_email="mulisilman123@gmail.com",
    license='MIT',
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Intended Audience :: Developers",
        'License :: OSI Approved :: MIT License',
        "Programming Language :: Python :: 3",
    ],
    entry_points={
        'console_scripts': ['s_interpreter=interpreter:main',
                            's_compiler=compiler:main'],
    },
)
