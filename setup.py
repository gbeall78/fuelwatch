from setuptools import find_packages, setup

setup(
    name='FuelWatch-beall',
    version='0.0.1',
    author='Glenn Beall',
    author_email='glenn@beall.id.au',
    description='FuelWatch project',
    url='https://github.com/gbeall78/fuelwatch',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'flask',
    ],
)