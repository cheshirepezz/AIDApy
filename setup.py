import os, sys
from setuptools import setup, find_packages, Command
from setuptools.extension import Extension


here = os.path.abspath(os.path.dirname(__file__))

with open("README.rst", "r") as fh:
    long_description = fh.read()

#with open('requirements.txt', 'r') as req_file:
#    install_reqs = [line.strip() for line in req_file.readlines()]

try:
    from sphinx.setup_command import BuildDoc
    cmdclass = {'build_sphinx': BuildDoc}
except ModuleNotFoundError:
    cmdclass = {'empty': None}

#['setup.py', '-b', 'html', './doc/source', './doc/_build/html'])

## Uncommend to wrap C/C++/Fortran codes
#from Cython.Build import cythonize
#extensions = [Extension(
#        name="aidapy.basicc",
#        sources_backup=["src/aidapy/basicc/cython/pycfunc.pyx"],
#        libraries=["mycfunc"],
#        language=["c"],
#        include_dirs=["src/aidapy/basicc/include"],
#        library_dirs=["src/aidapy/basicc/lib"],
#    ), Extension(
#        name="aidapy.basicf",
#        sources_backup=["src/aidapy/basicf/cython/pyffunc.pyx"],
#        libraries=["myffunc"],
#        language=["c"],
#        include_dirs=["src/aidapy/basicf/include"],
#        library_dirs=["src/aidapy/basicf/lib"],
#    ),
#]

setup(
    name="aidapy",
    version="0.0.2",
    author="AIDA Consortium",
    author_email="coordinator.aida@kuleuven.be",
    description="AI package for heliophysics",
    long_description=long_description,
    url="https://gitlab.com/aidaspace/aidapy",
    license='MIT',
    python_requires='>=3.5',
    install_requires=[
         'numpy',
         'matplotlib',
         'xarray',
         'astropy',
         'heliopy>=0.12.0',
         'heliopy-multid',
         'sunpy',
         'cdflib',
         'requests',
         'more_itertools',
         'extension',
         'bottleneck'
    ],
     dependency_links=[
        'https://github.com/hbreuill/heliopy/archive/0074817.zip#egg=heliopy'
    ],
    tests_require=[
        'pytest',
        'pylint',
        'pytest-cov',
        'coverage'
    ],
    extras_require={
        'doc': ['sphinx_rtd_theme', 'sphinx>=1.4', 'ipython', 'ipykernel', 'nbsphinx', 'sphinxcontrib-apidoc'],
        'ml': ['torch>=1.3', 'skorch', 'h5py', 'joblib'], #'sklearn', 'mpi4py',
        'vdf_cub': ['tricubic']
    },
    cmdclass=cmdclass,
    classifier=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Astronomy',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Physics'
    ],
    packages=find_packages(exclude=['doc*', 'example*',
                                    'test*', '*egg-info*']),
    data_files=None,
    zip_safe=False,
    include_package_data=True,
    setup_requires=['pytest-runner'],
    test_suite = 'tests',
    command_options={
        'build_sphinx': {
            'source_dir': ('setup.py', 'doc/source'),
            'build_dir': ('setup.py',  './doc/_build'),
            'builder': ('setup.py', 'html')
        }
    }
    ## Uncommend to wrap C/C++/Fortran codes
    #ext_modules=cythonize(extensions),
)
