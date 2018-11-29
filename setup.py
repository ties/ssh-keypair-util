import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ssh_keypair_util",
    version="0.3.0",
    author="Ties de Kock",
    author_email="author@example.com",
    description="Utility to generate ssh keys and add them to ssh config",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ties/ssh-keypair-util",
    packages=setuptools.find_packages(),
    install_required=['python-augeas'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            'sshkey = ssh_keypair_util.sshkey:main_func',
        ],
    },
)
