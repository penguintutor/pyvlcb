from setuptools import setup, find_packages

setup(
    name="pyvlcb",
    version="0.1.0",
    author="Stewart Watkiss (penguintutor)",
    author_email="5587863+penguintutor@users.noreply.github.com",
    description="A library for CBUS / VLCB communication",
    url="https://github.com/penguintutor/pyvlcb/",
    project_urls={
        "Documentation": "https://www.penguintutor.com/projects/pyvlcb",
        "Source": "https://github.com/penguintutor/pyvlcb/",
    },
    
    # Automatically finds the 'pyvlcb' folder because it has an __init__.py
    packages=find_packages(),
    
    # Python version requirement
    python_requires=">=3.6",
    
    # If your library needs other libraries (e.g., pyserial), list them here
    install_requires=[
        "pyserial",
    ],
)
