from setuptools import setup, Extension


setup(name='economicsl',
      version='0.4',
      description='Colorful blue ideas live hostilely',
      url='https://github.com/rht/economicsl',
      author='rhtbot',
      author_email='rhtbot@protonmail.com',
      license='MIT',
      packages=['economicsl'],
      # https://stackoverflow.com/questions/37471313/setup-requires-with-cython/38057196#38057196
      ext_modules=[
          Extension(
              'economicsl.contract',
              sources=['economicsl/contract.py']),
          Extension(
              'economicsl.accounting',
              ['economicsl/accounting.py']
          )
      ],
      setup_requires=['setuptools>=18.0', 'cython'],
      package_data={
          'economicsl': ['*.pxd'],
      },
      zip_safe=False)
