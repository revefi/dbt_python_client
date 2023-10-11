import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    python_requires=">=3.8",
    name='revefi-dbt-client',
    version='0.1.1',
    author='Revefi',
    description='Package to upload dbt core files to Revefi',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/revefi/dbt_python_client',
    license='MIT',
    packages=setuptools.find_packages(
        exclude=[
            '*.tests',
            '*.tests.*',
            'tests.*',
            'tests',
        ]
    ),
    install_requires=['requests', 'dynaconf==3.2.3'],
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ]
)
