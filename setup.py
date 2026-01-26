from setuptools import setup, find_packages

setup(
    name="PyVLCB",
    version="0.0.1",
    author="Stewart Watkiss (penguintutor)",
    author_email="5587863+penguintutor@users.noreply.github.com",
    description="A library for CBUS / VLCB communication",
    license="MIT",
    url="https://github.com/penguintutor/pyvlcb/",
    project_urls={
        "Documentation": "https://www.penguintutor.com/projects/pyvlcb",
        "Source": "https://github.com/penguintutor/pyvlcb/",
    },
    
    # Automatically finds the 'pyvlcb' folder because it has an __init__.py
    packages=find_packages(),

    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        # ... other classifiers ...
    ],
    
    # Python version requirement
    python_requires=">=3.6",
    
    # If your library needs other libraries (e.g., pyserial), list them here
    install_requires=[
        "pyserial",
    ],
)
