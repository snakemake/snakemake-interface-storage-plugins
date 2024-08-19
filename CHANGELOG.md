# Changelog

## [3.3.0](https://github.com/snakemake/snakemake-interface-storage-plugins/compare/v3.2.4...v3.3.0) (2024-08-19)


### Features

* add postprocess_query method for optionally modifying the query before a storage object is created ([#51](https://github.com/snakemake/snakemake-interface-storage-plugins/issues/51)) ([5590a90](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/5590a902d70aa5881212321ac1136c6c05cff51e))

## [3.2.4](https://github.com/snakemake/snakemake-interface-storage-plugins/compare/v3.2.3...v3.2.4) (2024-08-14)


### Bug Fixes

* in test suite, check that filepath exists after retrieval ([b4585df](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/b4585df9fb9b2890c5c77d41e604170bca0caee2))

## [3.2.3](https://github.com/snakemake/snakemake-interface-storage-plugins/compare/v3.2.2...v3.2.3) (2024-07-04)


### Bug Fixes

* fix name of touch operation attribute ([a0556bc](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/a0556bc06f690d0fe97b5681f243b383b1a782c3))
* return type of local_suffix ([#48](https://github.com/snakemake/snakemake-interface-storage-plugins/issues/48)) ([31ef31d](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/31ef31df6d43398d1e065fe24a17f2d162e06059))

## [3.2.2](https://github.com/snakemake/snakemake-interface-storage-plugins/compare/v3.2.1...v3.2.2) (2024-04-17)


### Bug Fixes

* improved storage tests ([#45](https://github.com/snakemake/snakemake-interface-storage-plugins/issues/45)) ([74e07a0](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/74e07a029a9434c152dcb782b15185e15e97671c))

## [3.2.1](https://github.com/snakemake/snakemake-interface-storage-plugins/compare/v3.2.0...v3.2.1) (2024-04-16)


### Bug Fixes

* rm local dir before storage test ([170a135](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/170a1359302ca8ff62a227e697e7be5b7710741a))

## [3.2.0](https://github.com/snakemake/snakemake-interface-storage-plugins/compare/v3.1.1...v3.2.0) (2024-04-15)


### Features

* add test case for directories ([#42](https://github.com/snakemake/snakemake-interface-storage-plugins/issues/42)) ([e6c4294](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/e6c42946b7f00a74c567219c875fa14e6ebe22a7))

## [3.1.1](https://github.com/snakemake/snakemake-interface-storage-plugins/compare/v3.1.0...v3.1.1) (2024-03-07)


### Bug Fixes

* test mtime in test suite ([#38](https://github.com/snakemake/snakemake-interface-storage-plugins/issues/38)) ([5cdd759](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/5cdd759c8268c38326c67fef3d477fa113fa4351))

## [3.1.0](https://github.com/snakemake/snakemake-interface-storage-plugins/compare/v3.0.0...v3.1.0) (2024-02-19)


### Features

* support for touching storage objects (updating their modification time) ([#35](https://github.com/snakemake/snakemake-interface-storage-plugins/issues/35)) ([a7db28b](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/a7db28bb01ab6019fd2819103481fd2b635b21a7))


### Bug Fixes

* improved inventory test ([a07d750](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/a07d75014174df0951526eb7645858dddd6dac5b))

## [3.0.0](https://github.com/snakemake/snakemake-interface-storage-plugins/compare/v2.1.1...v3.0.0) (2023-12-05)


### ⚠ BREAKING CHANGES

* require list of example queries (renamed method example_query into example_queries); this way, we support storage providers that need multiple examples to best explain how queries are structured

### Features

* require list of example queries (renamed method example_query into example_queries); this way, we support storage providers that need multiple examples to best explain how queries are structured ([a2c4a70](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/a2c4a701398e6b32bab27b294bf649449f26db6b))
* support checking whether plugin is read/write. ([df1f4da](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/df1f4da3299a07d889aef161accbee3b5da95921))

## [2.1.1](https://github.com/snakemake/snakemake-interface-storage-plugins/compare/v2.1.0...v2.1.1) (2023-11-26)


### Bug Fixes

* fix property name in interface ([89b48d5](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/89b48d57ddf54b489f38292c3f41f78bb22b0219))

## [2.1.0](https://github.com/snakemake/snakemake-interface-storage-plugins/compare/v2.0.1...v2.1.0) (2023-11-23)


### Features

* add argument for stripping incomplete parts of constant prefix ([d050377](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/d050377f06cb25654df2c966f0ac0557dd758483))


### Bug Fixes

* raise WorkflowError in case of failture during dir creation ([ed38962](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/ed3896267af3b2684184468e87625823d3d10f35))
* remove superfluous method ([30aeb9e](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/30aeb9ea4c258dd16341daa867f6253b40cfbda3))

## [2.0.1](https://github.com/snakemake/snakemake-interface-storage-plugins/compare/v2.0.0...v2.0.1) (2023-11-15)


### Miscellaneous Chores

* release 2.0.1 ([c0e9d30](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/c0e9d3085507fcd8bd6e8a2ceb09330fe48dfb20))

## [2.0.0](https://github.com/snakemake/snakemake-interface-storage-plugins/compare/v1.3.1...v2.0.0) (2023-11-15)


### ⚠ BREAKING CHANGES

* add tmp_path to query methods in test suite

### Features

* add tmp_path to query methods in test suite ([5cfcf62](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/5cfcf625c4f4bf5f41f742c484a449ae74b2d75a))


### Bug Fixes

* IOCache call in test suite ([00abf1b](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/00abf1b09515590c82262fd0e2621b1f86cce6d1))


### Documentation

* update readme ([63b5a4b](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/63b5a4bddf621284b63491d2a0798460d05b5c55))

## [1.3.1](https://github.com/snakemake/snakemake-interface-storage-plugins/compare/v1.3.0...v1.3.1) (2023-11-15)


### Bug Fixes

* create local storage prefix if it is not yet present ([ec5ff76](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/ec5ff76dbdaa63ed8ce41e3927ae42f3bd7145e3))

## [1.3.0](https://github.com/snakemake/snakemake-interface-storage-plugins/compare/v1.2.3...v1.3.0) (2023-11-15)


### Features

* add cache_key method ([2b571d0](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/2b571d0a5b5927a9934d7221682ee254311c5ce1))

## [1.2.3](https://github.com/snakemake/snakemake-interface-storage-plugins/compare/v1.2.2...v1.2.3) (2023-10-24)


### Bug Fixes

* adapt  test suite to changes in snakemake 8 ([a4cbefa](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/a4cbefa6d6ec7835f93d7b6ec427cb3a2ee334fb))

## [1.2.2](https://github.com/snakemake/snakemake-interface-storage-plugins/compare/v1.2.1...v1.2.2) (2023-10-24)


### Bug Fixes

* fix release process ([ec96bd2](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/ec96bd2334df5fdf03e666ade106ee6e5dd619eb))

## [1.2.1](https://github.com/snakemake/snakemake-interface-storage-plugins/compare/v1.2.0...v1.2.1) (2023-10-24)


### Bug Fixes

* update dependencies ([96df30e](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/96df30e782cf2f4fa5e341177b57178223c49953))

## [1.2.0](https://github.com/snakemake/snakemake-interface-storage-plugins/compare/v1.1.2...v1.2.0) (2023-10-17)


### Features

* migrate flagging code into main snakemake ([974f05d](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/974f05d18a180cb917bf8ca42488ac9ca566aae5))


### Bug Fixes

* add homepage ([b9846e0](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/b9846e0b607c8220bf32ec21d276188cd032d67d))

## [1.1.2](https://github.com/snakemake/snakemake-interface-storage-plugins/compare/v1.1.1...v1.1.2) (2023-10-13)


### Bug Fixes

* fix testcase for writable storage provider ([32f473a](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/32f473aee2bbb835888202654a2092297d27ffed))
* remove superfluous dependency ([12b9061](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/12b90619313ce35b2748abf1f6095fd0a0d4974b))

## [1.1.1](https://github.com/snakemake/snakemake-interface-storage-plugins/compare/v1.1.0...v1.1.1) (2023-10-11)


### Bug Fixes

* fix testcase for writable storage provider ([32f473a](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/32f473aee2bbb835888202654a2092297d27ffed))
* update deps ([856ba18](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/856ba180c6c1fa9d8b754cc4f1dbc022e01aa907))

## [1.1.0](https://github.com/snakemake/snakemake-interface-storage-plugins/compare/v1.0.2...v1.1.0) (2023-10-11)


### Features

* extend test cases ([6b49597](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/6b49597d5d96133756df28994078257bb7afb0c6))
* require example query to be provided ([f48b3f0](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/f48b3f07e1ea9fbb5fcb49890f6167d7c75a8b07))


### Bug Fixes

* adapt to changes in snakemake-interface-common ([a7da931](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/a7da9319d54284df4b9cd5e9fabd8b52098a50e3))
* update deps ([856ba18](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/856ba180c6c1fa9d8b754cc4f1dbc022e01aa907))

## [1.0.2](https://github.com/snakemake/snakemake-interface-storage-plugins/compare/v1.0.1...v1.0.2) (2023-09-28)


### Bug Fixes

* remove object after test ([b55c77c](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/b55c77c6d0f34de4c166832ea8d631becc978d96))

## [1.0.1](https://github.com/snakemake/snakemake-interface-storage-plugins/compare/v1.0.0...v1.0.1) (2023-09-27)


### Bug Fixes

* improved API ([1a5d518](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/1a5d5184a73e4c587d5ed685938b5839878300f6))

## [1.0.0](https://github.com/snakemake/snakemake-interface-storage-plugins/compare/v0.1.0...v1.0.0) (2023-09-27)


### Miscellaneous Chores

* release 1.0.0 ([522f4b6](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/522f4b6821d78e0f3b57fb0cfd1f11b9bdc92bc8))

## 0.1.0 (2023-09-26)


### Features

* add retry decorator ([30bcaf3](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/30bcaf332f8c754ebae445305f82ec9fd131d7f8))
* cleaned up and simplified API ([243177e](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/243177e1112f22559b3996eff0f604442276c040))
* support tagged settings ([1a64b4f](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/1a64b4f556e3e949411204ed533d8af161ef977d))


### Bug Fixes

* bump min version of snakemake-interface-common ([c50c9c1](https://github.com/snakemake/snakemake-interface-storage-plugins/commit/c50c9c129cfb7bc7f6c4d813ff9f8b307757a6c6))
