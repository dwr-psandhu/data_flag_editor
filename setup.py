from setuptools import setup
import versioneer

requirements = [
    "pandas",
    "numpy",
    "panel",
    "holoviz"
]

setup(
    name='data_flag_editor',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="DataFrame user flag field visual editor ",
    license="MIT",
    author="Nicky Sandhu",
    author_email='psandhu@water.ca.gov',
    url='https://github.com/dwr-psandhu/data_flag_editor',
    packages=['data_flag_editor'],
    entry_points={
        'console_scripts': [
            'data_flag_editor=data_flag_editor.cli:cli'
        ]
    },
    install_requires=requirements,
    keywords='data_flag_editor',
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]
)
