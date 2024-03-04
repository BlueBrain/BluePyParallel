# Changelog

## [0.2.1](https://github.com/BlueBrain/BluePyParallel/compare/0.2.0..0.2.1)

> 4 March 2024

### New Features

- Improve doc (Alexis Arnaudon - [#2](https://github.com/BlueBrain/BluePyParallel/pull/2))

### Chores And Housekeeping

- Move to Github (Adrien Berchet - [#1](https://github.com/BlueBrain/BluePyParallel/pull/1))

### New Features

- Shuffle rows for speedup (Alexis Arnaudon - [eda54a7](https://github.com/BlueBrain/BluePyParallel/commit/eda54a7ea7bc776f6167dd034cebaf78fd14cb47))

### CI Improvements

- Bump mpi4py in Gitlab CI (Adrien Berchet - [d3d55a3](https://github.com/BlueBrain/BluePyParallel/commit/d3d55a3014248e9d9f3908a4370c5033b2bef9c7))

<!-- auto-changelog-above -->

## [0.2.0](https://github.com/BlueBrain/BluePyParallel/compare/0.1.0..0.2.0)

> 6 November 2023

### Build

- Relax ipyparallel (Adrien Berchet - [718b5d1](https://github.com/BlueBrain/BluePyParallel/commit/718b5d14893b1b74b322fa5c3303e38f190239b7))

### New Features

- Improve the ways dask can be configured (Adrien Berchet - [c16e686](https://github.com/BlueBrain/BluePyParallel/commit/c16e686aa026527f96d74d9619a120872446f637))

## [0.1.0](https://github.com/BlueBrain/BluePyParallel/compare/0.0.9..0.1.0)

> 5 October 2023

### Build

- Drop support for Python 3.7 (Adrien Berchet - [f948fb3](https://github.com/BlueBrain/BluePyParallel/commit/f948fb3871597ad140186389f1ddf1a89852917f))

### New Features

- Improve how dask can be configured (Adrien Berchet - [0aae758](https://github.com/BlueBrain/BluePyParallel/commit/0aae758294d2cda9404defadcc226b900be5b8a7))

## [0.0.9](https://github.com/BlueBrain/BluePyParallel/compare/0.0.8..0.0.9)

> 27 February 2023

### Chores And Housekeeping

- Compatibility with SQLAlchemy&gt;=2 (Adrien Berchet - [6acefdc](https://github.com/BlueBrain/BluePyParallel/commit/6acefdcaa56f55a1a39d9c926031093f19263249))

### CI Improvements

- Bump pre-commit hooks (Adrien Berchet - [e7e6229](https://github.com/BlueBrain/BluePyParallel/commit/e7e62292c36d43c9677747c0de3938e36eb55e9a))
- Fix coverage job for tox 4 (Adrien Berchet - [050d199](https://github.com/BlueBrain/BluePyParallel/commit/050d199ca548760b48dfef003fc6514588930c58))

## [0.0.8](https://github.com/BlueBrain/BluePyParallel/compare/0.0.7..0.0.8)

> 31 October 2022

### Documentation Changes

- Fix requirements for doc generation (Adrien Berchet - [52f8c53](https://github.com/BlueBrain/BluePyParallel/commit/52f8c534e2779d874a04539135cd3fcb2ee7626f))

### Refactoring and Updates

- Apply Copier template (Adrien Berchet - [fa06074](https://github.com/BlueBrain/BluePyParallel/commit/fa06074e8de5dc80545b7db8d03ea3aa726020c8))

### Changes to Test Assests

- Fix cluster creation to ignore missing Bokeh dependency (Adrien Berchet - [51eca82](https://github.com/BlueBrain/BluePyParallel/commit/51eca823bce5952cc138c05d976250d426831a46))
- Fix index name in test_evaluator.py (Adrien Berchet - [f2e7906](https://github.com/BlueBrain/BluePyParallel/commit/f2e7906c04e6d2bcf1ef758ed52cc387c34fa3e9))

### CI Improvements

- Update pre-commit hook versions (Adrien Berchet - [af662b0](https://github.com/BlueBrain/BluePyParallel/commit/af662b0fb787e99971d6ccf65f813b41dc9ff21d))

### General Changes

- Fix dict inconsistency (Alexis Arnaudon - [a7a7849](https://github.com/BlueBrain/BluePyParallel/commit/a7a7849c8cec4915b2860a6db352aa25d38f505a))
- Change name of package to be consistent with (Alexander Dietz - [c156f58](https://github.com/BlueBrain/BluePyParallel/commit/c156f5803edddc56c3ff7cc11b40b2354a5c150a))

## [0.0.7](https://github.com/BlueBrain/BluePyParallel/compare/0.0.6..0.0.7)

> 31 March 2022

### General Changes

- Use pytest template to improve tests and coverage reports (Adrien Berchet - [a088540](https://github.com/BlueBrain/BluePyParallel/commit/a088540c8a48ae2aaff77f630e1e66829a150497))
- Handle deconnections and fix requirements (Adrien Berchet - [3ca7b7d](https://github.com/BlueBrain/BluePyParallel/commit/3ca7b7db75d04aa06c62242dcd353c17dc3968f4))
- Migration from gerrit to github (Adrien Berchet - [f25bf4c](https://github.com/BlueBrain/BluePyParallel/commit/f25bf4c0e9530a67b1e8f8b0dd9c9453534112f3))
- Add auto-release job in CI (Adrien Berchet - [38cee05](https://github.com/BlueBrain/BluePyParallel/commit/38cee05378d30683cfbb0ca12722f742ca96d85e))
- Increase number of CPUs in CI (Adrien Berchet - [c58255c](https://github.com/BlueBrain/BluePyParallel/commit/c58255c13266911b9e11df4aad633f230dd75cda))
- Remove MPI module from CI (Adrien Berchet - [51c6792](https://github.com/BlueBrain/BluePyParallel/commit/51c6792106e9cd8a36994c6462fc91d6ba1a8a00))

## [0.0.6](https://github.com/BlueBrain/BluePyParallel/compare/0.0.5..0.0.6)

> 21 June 2021

### General Changes

- Improve DB inserts for dask_dataframe factory (Adrien Berchet - [d4a6767](https://github.com/BlueBrain/BluePyParallel/commit/d4a6767a1efe2e5fd6f371b05fa2b6fcf6ed308d))

## [0.0.5](https://github.com/BlueBrain/BluePyParallel/compare/0.0.4..0.0.5)

> 11 May 2021

### General Changes

- dask_dataframe (arnaudon - [df4b447](https://github.com/BlueBrain/BluePyParallel/commit/df4b4474ee1c91f5af24cdb9cf6db7f4169a0c7a))
- changelog (arnaudon - [4d90cd2](https://github.com/BlueBrain/BluePyParallel/commit/4d90cd239fe8e26a5f66862e23f609c50f89da6c))
- Add minimal python version (Adrien Berchet - [38e45d2](https://github.com/BlueBrain/BluePyParallel/commit/38e45d2960db0d7bdb3696b27e397fd6bb0f3069))
- release 0.0.5 (arnaudon - [30e3fd0](https://github.com/BlueBrain/BluePyParallel/commit/30e3fd07d8d7ec8f56e680109de37e30614449d0))

## [0.0.4](https://github.com/BlueBrain/BluePyParallel/compare/0.0.3..0.0.4)

> 24 March 2021

### General Changes

- Update doc, README and author (Adrien Berchet - [9dde38a](https://github.com/BlueBrain/BluePyParallel/commit/9dde38ab56ef77144ef938ece21b338cc1284511))

## [0.0.3](https://github.com/BlueBrain/BluePyParallel/compare/0.0.2..0.0.3)

> 24 March 2021

### General Changes

- Add wrapper to pass args and kwargs to the function and improve test coverage (Adrien Berchet - [790656b](https://github.com/BlueBrain/BluePyParallel/commit/790656bac98dcdcaee2697e2f96a767798b4d89b))
- Clean and improve the code (Adrien Berchet - [8762ada](https://github.com/BlueBrain/BluePyParallel/commit/8762ada3597dcdb662a119af87fc5106adba8b4d))
- Reduce SQL I/Os and can now pass args to the evaluation function (Adrien Berchet - [2a3e1f0](https://github.com/BlueBrain/BluePyParallel/commit/2a3e1f0367b93229710114835e505e3cf881f377))
- Add DB API using SQLAlchemy (Adrien Berchet - [c94dc94](https://github.com/BlueBrain/BluePyParallel/commit/c94dc94d16cc8cbc53e058930a9720e834b90836))
- Improve factory interfaces (Adrien Berchet - [427930e](https://github.com/BlueBrain/BluePyParallel/commit/427930ea0a6150a15ad87afccdcabc98d4573405))
- Improve performance (Adrien Berchet - [4619d24](https://github.com/BlueBrain/BluePyParallel/commit/4619d24abc49ee5e628cd5e9dab4ca9d8361ba12))
- Add PostgreSQL tests (Adrien Berchet - [ccdca61](https://github.com/BlueBrain/BluePyParallel/commit/ccdca6143ee082210bd377110469e7cf41871b1c))
- bump version (arnaudon - [592efdf](https://github.com/BlueBrain/BluePyParallel/commit/592efdf583fb1bbe71bd6036a0e08990a3b86e9d))
- fix logging (arnaudon - [626484c](https://github.com/BlueBrain/BluePyParallel/commit/626484cc4e7909586f8b3498095a6bc856488bcf))

## [0.0.2](https://github.com/BlueBrain/BluePyParallel/compare/0.0.1..0.0.2)

> 10 February 2021

### General Changes

- remove mention to combos (arnaudon - [104cf61](https://github.com/BlueBrain/BluePyParallel/commit/104cf61b10ced94bea0194f7fab3049cae1d7049))
- new release (arnaudon - [a3ebbe2](https://github.com/BlueBrain/BluePyParallel/commit/a3ebbe269ca365388ba03d2e591273b93702d1fc))

## 0.0.1

> 9 February 2021

### General Changes

- first commit (arnaudon - [e6a7274](https://github.com/BlueBrain/BluePyParallel/commit/e6a727467a50fd3c52c3d65a37f6da8287ca7467))
- first release (arnaudon - [4585e48](https://github.com/BlueBrain/BluePyParallel/commit/4585e48703c1dd1dd5c3520d968b1afa83e88231))
- Initial empty repository (Luis Pigueiras - [e94be56](https://github.com/BlueBrain/BluePyParallel/commit/e94be563ef61330fc1c452b1506dff5b8bcab90a))
