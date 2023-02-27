# Changelog

## [bluepyparallel-v0.0.9](https://bbpgitlab.epfl.ch/neuromath/bluepyparallel/compare/bluepyparallel-v0.0.8...bluepyparallel-v0.0.9)

> 27 February 2023

### Chores And Housekeeping

- Compatibility with SQLAlchemy&gt;=2 (Adrien Berchet - [6acefdc](https://bbpgitlab.epfl.ch/neuromath/bluepyparallel/commit/6acefdcaa56f55a1a39d9c926031093f19263249))

### CI Improvements

- Bump pre-commit hooks (Adrien Berchet - [e7e6229](https://bbpgitlab.epfl.ch/neuromath/bluepyparallel/commit/e7e62292c36d43c9677747c0de3938e36eb55e9a))
- Fix coverage job for tox 4 (Adrien Berchet - [050d199](https://bbpgitlab.epfl.ch/neuromath/bluepyparallel/commit/050d199ca548760b48dfef003fc6514588930c58))

## bluepyparallel-v0.0.8

> 31 October 2022

### Documentation Changes

- Fix requirements for doc generation (Adrien Berchet - [52f8c53](https://bbpgitlab.epfl.ch/neuromath/bluepyparallel/commit/52f8c534e2779d874a04539135cd3fcb2ee7626f))

### Refactoring and Updates

- Apply Copier template (Adrien Berchet - [fa06074](https://bbpgitlab.epfl.ch/neuromath/bluepyparallel/commit/fa06074e8de5dc80545b7db8d03ea3aa726020c8))

### Changes to Test Assests

- Fix cluster creation to ignore missing Bokeh dependency (Adrien Berchet - [51eca82](https://bbpgitlab.epfl.ch/neuromath/bluepyparallel/commit/51eca823bce5952cc138c05d976250d426831a46))
- Fix index name in test_evaluator.py (Adrien Berchet - [f2e7906](https://bbpgitlab.epfl.ch/neuromath/bluepyparallel/commit/f2e7906c04e6d2bcf1ef758ed52cc387c34fa3e9))

### CI Improvements

- Update pre-commit hook versions (Adrien Berchet - [af662b0](https://bbpgitlab.epfl.ch/neuromath/bluepyparallel/commit/af662b0fb787e99971d6ccf65f813b41dc9ff21d))

### General Changes

- first commit (arnaudon - [e6a7274](https://bbpgitlab.epfl.ch/neuromath/bluepyparallel/commit/e6a727467a50fd3c52c3d65a37f6da8287ca7467))
- Add wrapper to pass args and kwargs to the function and improve test coverage (Adrien Berchet - [790656b](https://bbpgitlab.epfl.ch/neuromath/bluepyparallel/commit/790656bac98dcdcaee2697e2f96a767798b4d89b))
- Clean and improve the code (Adrien Berchet - [8762ada](https://bbpgitlab.epfl.ch/neuromath/bluepyparallel/commit/8762ada3597dcdb662a119af87fc5106adba8b4d))
- Reduce SQL I/Os and can now pass args to the evaluation function (Adrien Berchet - [2a3e1f0](https://bbpgitlab.epfl.ch/neuromath/bluepyparallel/commit/2a3e1f0367b93229710114835e505e3cf881f377))
- dask_dataframe (arnaudon - [df4b447](https://bbpgitlab.epfl.ch/neuromath/bluepyparallel/commit/df4b4474ee1c91f5af24cdb9cf6db7f4169a0c7a))
- Add DB API using SQLAlchemy (Adrien Berchet - [c94dc94](https://bbpgitlab.epfl.ch/neuromath/bluepyparallel/commit/c94dc94d16cc8cbc53e058930a9720e834b90836))
- Use pytest template to improve tests and coverage reports (Adrien Berchet - [a088540](https://bbpgitlab.epfl.ch/neuromath/bluepyparallel/commit/a088540c8a48ae2aaff77f630e1e66829a150497))
- Update doc, README and author (Adrien Berchet - [9dde38a](https://bbpgitlab.epfl.ch/neuromath/bluepyparallel/commit/9dde38ab56ef77144ef938ece21b338cc1284511))
- Improve factory interfaces (Adrien Berchet - [427930e](https://bbpgitlab.epfl.ch/neuromath/bluepyparallel/commit/427930ea0a6150a15ad87afccdcabc98d4573405))
- Improve performance (Adrien Berchet - [4619d24](https://bbpgitlab.epfl.ch/neuromath/bluepyparallel/commit/4619d24abc49ee5e628cd5e9dab4ca9d8361ba12))
- remove mention to combos (arnaudon - [104cf61](https://bbpgitlab.epfl.ch/neuromath/bluepyparallel/commit/104cf61b10ced94bea0194f7fab3049cae1d7049))
- Improve DB inserts for dask_dataframe factory (Adrien Berchet - [d4a6767](https://bbpgitlab.epfl.ch/neuromath/bluepyparallel/commit/d4a6767a1efe2e5fd6f371b05fa2b6fcf6ed308d))
- Handle deconnections and fix requirements (Adrien Berchet - [3ca7b7d](https://bbpgitlab.epfl.ch/neuromath/bluepyparallel/commit/3ca7b7db75d04aa06c62242dcd353c17dc3968f4))
- Migration from gerrit to github (Adrien Berchet - [f25bf4c](https://bbpgitlab.epfl.ch/neuromath/bluepyparallel/commit/f25bf4c0e9530a67b1e8f8b0dd9c9453534112f3))
- Add auto-release job in CI (Adrien Berchet - [38cee05](https://bbpgitlab.epfl.ch/neuromath/bluepyparallel/commit/38cee05378d30683cfbb0ca12722f742ca96d85e))
- Add PostgreSQL tests (Adrien Berchet - [ccdca61](https://bbpgitlab.epfl.ch/neuromath/bluepyparallel/commit/ccdca6143ee082210bd377110469e7cf41871b1c))
- Increase number of CPUs in CI (Adrien Berchet - [c58255c](https://bbpgitlab.epfl.ch/neuromath/bluepyparallel/commit/c58255c13266911b9e11df4aad633f230dd75cda))
- changelog (arnaudon - [4d90cd2](https://bbpgitlab.epfl.ch/neuromath/bluepyparallel/commit/4d90cd239fe8e26a5f66862e23f609c50f89da6c))
- Add minimal python version (Adrien Berchet - [38e45d2](https://bbpgitlab.epfl.ch/neuromath/bluepyparallel/commit/38e45d2960db0d7bdb3696b27e397fd6bb0f3069))
- Remove MPI module from CI (Adrien Berchet - [51c6792](https://bbpgitlab.epfl.ch/neuromath/bluepyparallel/commit/51c6792106e9cd8a36994c6462fc91d6ba1a8a00))
- Fix dict inconsistency (Alexis Arnaudon - [a7a7849](https://bbpgitlab.epfl.ch/neuromath/bluepyparallel/commit/a7a7849c8cec4915b2860a6db352aa25d38f505a))
- Change name of package to be consistent with (Alexander Dietz - [c156f58](https://bbpgitlab.epfl.ch/neuromath/bluepyparallel/commit/c156f5803edddc56c3ff7cc11b40b2354a5c150a))
- release 0.0.5 (arnaudon - [30e3fd0](https://bbpgitlab.epfl.ch/neuromath/bluepyparallel/commit/30e3fd07d8d7ec8f56e680109de37e30614449d0))
- bump version (arnaudon - [592efdf](https://bbpgitlab.epfl.ch/neuromath/bluepyparallel/commit/592efdf583fb1bbe71bd6036a0e08990a3b86e9d))
- fix logging (arnaudon - [626484c](https://bbpgitlab.epfl.ch/neuromath/bluepyparallel/commit/626484cc4e7909586f8b3498095a6bc856488bcf))
- new release (arnaudon - [a3ebbe2](https://bbpgitlab.epfl.ch/neuromath/bluepyparallel/commit/a3ebbe269ca365388ba03d2e591273b93702d1fc))
- first release (arnaudon - [4585e48](https://bbpgitlab.epfl.ch/neuromath/bluepyparallel/commit/4585e48703c1dd1dd5c3520d968b1afa83e88231))
- Initial empty repository (Luis Pigueiras - [e94be56](https://bbpgitlab.epfl.ch/neuromath/bluepyparallel/commit/e94be563ef61330fc1c452b1506dff5b8bcab90a))
