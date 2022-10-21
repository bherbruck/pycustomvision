import setuptools

setuptools.setup(
    name="pycusomvision",
    version="0.0.1",
    author="bherbruck",
    description="Export Customvision dataset to YOLO format",
    url="https://github.com/bherbruck/pycusomvision",
    packages=setuptools.find_packages(),
    install_requires=[
        'requests',
        'pyyaml'
    ],
    entry_points={
        'console_scripts': [
            'pycusomvision = src.__main__:main'
        ]
    }
)
