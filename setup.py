from setuptools import setup

version = '1.0'

install_requires = [
    # -*- Extra requirements: -*-
    "numpy",
    ]

setup(name='pymclevel',
      version=version,
      description="Python library for reading Minecraft levels",
      long_description=open("./README.txt", "r").read(),
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Environment :: Console",
          "Intended Audience :: End Users/Desktop",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2.7",
          "Topic :: Utilities",
          "License :: OSI Approved :: MIT License",
          ],
      keywords='minecraft',
      author='David Vierra',
      author_email='codewarrior0@gmail.com',
      url='https://github.com/codewarrior0/pymclevel',
      license='MIT License',
      package_dir={'pymclevel': '.'},
      packages=["pymclevel"],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      mce.py=pymclevel.mce:main
      """,
      )
