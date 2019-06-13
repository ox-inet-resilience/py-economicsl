from setuptools import setup
try:
    from Cython.Build import cythonize
except ImportError:
    # create closure for deferred import
    def cythonize (*args, ** kwargs ):
        from Cython.Build import cythonize
        return cythonize(*args, ** kwargs)


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
          'economicsl': ['*.pxd'],
      },
      zip_safe=False)
