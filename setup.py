from setuptools import setup
from Cython.Build import cythonize


setup(name='economicsl',
      version='0.2',
      description='Colorful blue ideas live hostilely',
      url='https://github.com/rht/economicsl',
      author='rhtbot',
      author_email='rhtbot@protonmail.com',
      license='MIT',
      packages=['economicsl'],
      ext_modules=cythonize(['economicsl/%s.py' % i for i in ['contract']]),
      package_data={
          '': ['*.pxd'],
      },
      zip_safe=False)
