from setuptools import setup, find_packages

print(find_packages(where='src'))

setup(name='predictit-public',
      version='0.1',
      description='An automatic scraper and gambler for predictit.com',
      # long_description=open('README.txt').read(),
      url='https://github.com/zlex7/PredictIt-Public',
      author='zlex7, alexdai186',
      author_email='a.wlezien@gmail.com',
      license='MIT',
      install_requires = ['selenium', 'redis', 'pytz', 'python-dateutil', 'tweepy', 'setuptools', 'mechanicalsoup'],
      package_dir={'':'src'},
      packages=find_packages(where='src'),
      zip_safe=False)
