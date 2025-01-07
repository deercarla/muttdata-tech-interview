from setuptools import setup, find_packages

# Function to read requirements.txt
def read_requirements():
    with open("requirements.txt", "r") as req_file:
        return req_file.readlines()

setup(
    name="Carla--de-Erausquin",
    version="0.1",
    packages=find_packages(),
    install_requires=read_requirements(),  # Add dependencies from requirements.txt
)

