from setuptools import setup, find_packages

# To install run pip install -e PATH_TO_PACKAGE

setup(
    name='loganiaceaetraits',
    url='https://github.com/alrichardbollans/loganiaceae_traits',
    author='Adam Richard-Bollans',
    author_email='38588335+alrichardbollans@users.noreply.github.com',
    # Needed to actually package something
    packages=find_packages(include=['cleaning_plant_occurrences', 'climate_vars', 'common_name_vars',
                                    'conservation_priorities',
                                    'getting_malarial_regions',
                                    'logan_poison_vars',
                                    'manually_collected_data', 'morphological_vars',
                                    'metabolite_vars', 'medicinal_usage_vars',
                                    'wcsp_distributions',
                                    'logan_wikipedia_vars']),
    # *strongly* suggested for sharing
    version='0.1',
    license='MIT',
    description='A set of python packages for plant trait data',
    long_description=open('README.md').read(),
)
