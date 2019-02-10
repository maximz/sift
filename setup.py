from setuptools import setup

setup(name='search',
      version='0.1',
      description='',
      url='',
      author='',
      author_email='',
      packages=['search'],
      install_requires=[
          'pandas',
      ],
      entry_points={
          'console_scripts': [
              'search=search.main:main',
          ],
      },
      zip_safe=False)
