"""Setup script for Git Workflow Enforcer"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / 'README.md'
long_description = readme_file.read_text() if readme_file.exists() else ''

setup(
    name='git-workflow-enforcer',
    version='1.0.0',
    description='Automated Git Workflow Enforcer - Validate branch names and commit messages',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='DevOps Team',
    author_email='devops@example.com',
    url='https://github.com/reetikesh17/devops-project-Automated-Git-Workflow-Enforcer',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    package_data={
        'config': ['rules.json'],
    },
    include_package_data=True,
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'git-enforcer=main.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Version Control :: Git',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    keywords='git workflow validation commit branch devops',
)
