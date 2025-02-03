from setuptools import setup

setup(
    name = 'Standard Works',
    version = '0.1',
    description = 'Read, search, and anotate the Bible, Book of Mormon, Doctrine and Covenants, and the Pearl of Great Price.',
    author = 'Carson Buttars',
    author_email = 'carsonbuttars13@gmail.com',
    packages = ['std_works'],
    scripts = ['src/std-works'],
    package_dir = {"": "src"},
    include_package_data = True,
    package_data = {"": ["*.sql"]}
)

