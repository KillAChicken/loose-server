import os.path
import setuptools


if __name__ == "__main__":
    dir_path = os.path.dirname(__file__)
    readme_path = os.path.abspath(os.path.join(dir_path, "README.rst"))
    with open(readme_path) as readme_file:
        long_description = readme_file.read()

    setuptools.setup(
        name="loose-server",
        version="0.1",
        author="KillAChicken",
        author_email="KillAChicken@yandex.ru",
        description="Dynamically configurable server",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/KillAChicken/loose-server",
        packages=setuptools.find_packages(include=("looseserver*", )),
        classifiers=[
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 3",
            "Topic :: Software Development :: Testing",
            "Topic :: Software Development :: Testing :: Mocking",
            ],
        )
