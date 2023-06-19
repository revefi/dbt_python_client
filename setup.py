import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='revefi-dbt-client',
    version='0.0.1',
    author='Revefi Team',
    description='Package to upload dbt core files to Revefi',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/revefi/dbt_python_client',
    license='MIT',
    packages=['revefi-dbt-client'],
    install_requires=['requests'],
)
