from setuptools import setup

setup(name='sift',
      version='0.1',
      description='',
      url='',
      author='',
      author_email='',
      packages=['sift'],
      install_requires=[
          'pandas',
      ],
      entry_points={
          'console_scripts': [
              'sift=sift.main:main',
          ],
      },
      zip_safe=False)
