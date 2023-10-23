from setuptools import setup, Distribution



class BinaryDistribution(Distribution):

    def has_ext_modules(self):
        return True


setup(
    distclass=BinaryDistribution,
)
