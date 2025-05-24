from setuptools import setup, find_packages

setup(
    name="OBPI",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pywebview==4.0",
        "pyusb==1.2.1",
        "opencv-python==4.9.0.80",
        "psutil==5.9.8",
        "PyInstaller==6.7.0",
    ],
    entry_points={
        'console_scripts': [
            'obpi=backend.main:main',
        ],
    },
    author="OBPI Team",
    author_email="info@obpi.example.com",
    description="Operational in Browser Persisted Instance - A standalone desktop application",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/example/obpi",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
