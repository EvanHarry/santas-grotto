# Santa's Grotto

## About
**Author** - Evan Harry  
**Project** - Tidings Stock Database  
**Created** - 08/12/2018  
**Description** - Authentication and data handling.

## Installation
First download and install the application:
```bash
git clone git@github.com/evanharry/santas-grotto.git
cd santas-grotto
pip install -e .
```

Then initialise the database:
```bash
SET/EXPORT FLASK_APP=grotto
SET/EXPORT FLASK_ENV=development
flask init-db
```

If there is seed data this can be added:
```bash
SET/EXPORT FLASK_APP=grotto
SET/EXPORT FLASK_ENV=development
flask seed-db
```

## Usage
On Windows you can use the ```run.bat``` file, otherwise run:
```bash
EXPORT FLASK_APP=grotto
/EXPORT FLASK_ENV=development
flask run
```

## Release
To release a new version, change the tag in ```setup.py``` then run:
```bash
python setup.py bdist_wheel
```