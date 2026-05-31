# CHANGELOG

<!-- version list -->

## v1.3.6 (2026-05-31)

### Bug Fixes

- Improve asyncio lifecycle and signal handling
  ([`e356b33`](https://github.com/EHylands/QolsysController/commit/e356b33d321c2ac7601a6bc3b577d233f3d54e13))


## v1.3.5 (2026-05-31)

### Bug Fixes

- Use TaskGroup for concurrent task management
  ([`fbdc0a1`](https://github.com/EHylands/QolsysController/commit/fbdc0a188e4c7def2b62e06edae7f42fe23cae4c))


## v1.3.4 (2026-05-28)

### Bug Fixes

- Prevent cli.py from shutting down on startup
  ([`72a1820`](https://github.com/EHylands/QolsysController/commit/72a1820a0528b91ef243e21226aeae5affed0672))


## v1.3.3 (2026-05-28)

### Bug Fixes

- Prevent cli.py from shutting down on startup
  ([`58ec1ce`](https://github.com/EHylands/QolsysController/commit/58ec1ce30e99de9c75912eb70949644e64f60c30))

### Chores

- **deps**: Bump zeroconf from 0.149.4 to 0.149.16
  ([#49](https://github.com/EHylands/QolsysController/pull/49),
  [`113e0b0`](https://github.com/EHylands/QolsysController/commit/113e0b0f91db8638c35a401118637ebdee376a77))


## v1.3.2 (2026-05-27)

### Bug Fixes

- **deps**: Bump cryptography to v48.0.0
  ([`2f5dd70`](https://github.com/EHylands/QolsysController/commit/2f5dd706bbaeaf65d0db16213fcaeb9c12938be4))

### Chores

- **deps**: Update cryptography requirement
  ([#47](https://github.com/EHylands/QolsysController/pull/47),
  [`502e953`](https://github.com/EHylands/QolsysController/commit/502e95389cb15977bbdd8d48f92b3d4f6f30286e))


## v1.3.1 (2026-05-25)

### Bug Fixes

- Allow stopped to connecting state transition
  ([`838b7a9`](https://github.com/EHylands/QolsysController/commit/838b7a9a363e72f4dd1e1c61253991fc193b74d4))


## v1.3.0 (2026-05-25)

### Features

- Updated pairing_server and reconnection logic
  ([`d4f2664`](https://github.com/EHylands/QolsysController/commit/d4f26644fdc4f177829614fd5950cfdd2c0fa418))


## v1.2.1 (2026-05-23)

### Bug Fixes

- Hardening key exchange for special characters
  ([`59463dd`](https://github.com/EHylands/QolsysController/commit/59463dd6961e4784dcb1b75b6cc6a2c71f95b2c3))

### Chores

- Use personnal token
  ([`5948f8d`](https://github.com/EHylands/QolsysController/commit/5948f8dd0114ffb63604e44f55b1d443763bbe47))


## v1.2.0 (2026-05-18)

### Chores

- Publish to pypi on tag creation
  ([`fe27318`](https://github.com/EHylands/QolsysController/commit/fe27318f799d7d353fb09d1c6a85e21e1eec35a1))

- **deps**: Bump zeroconf from 0.148.0 to 0.149.4
  ([#48](https://github.com/EHylands/QolsysController/pull/48),
  [`3006907`](https://github.com/EHylands/QolsysController/commit/3006907f63b63f02f3fb9088a7436f0b55d2d7e7))

### Features

- Now allow external zeroconf instance as ha requirement
  ([`5b3a178`](https://github.com/EHylands/QolsysController/commit/5b3a1786d884572790f17ae9e985ed729a1680dc))


## v1.1.2 (2026-05-18)

### Bug Fixes

- Stop_operation on ssl error
  ([`d9e504e`](https://github.com/EHylands/QolsysController/commit/d9e504efc902723aed18c176c219ef154299a353))

### Chores

- Publish to pypi on new release
  ([`4373195`](https://github.com/EHylands/QolsysController/commit/4373195f355720632d69763e0e699e09f2a4604e))


## v1.1.1 (2026-05-18)

### Bug Fixes

- Stop reconnect loop on configuration error
  ([`e200e3c`](https://github.com/EHylands/QolsysController/commit/e200e3c4706728c45fcce25587cd2ebb1a45fe59))

- Stop reconnect loop on configuration error
  ([`53cf5bd`](https://github.com/EHylands/QolsysController/commit/53cf5bdd2dc3b7938fb4734b57c8e31fe6ac3686))

### Chores

- Publish new pypi version on new tag
  ([`d68fdc8`](https://github.com/EHylands/QolsysController/commit/d68fdc810fa1a90a03adaa13d9307b5a4acfb5f1))


## v1.1.0 (2026-05-16)

### Features

- Partion last_error
  ([`549c09e`](https://github.com/EHylands/QolsysController/commit/549c09e58739fde6ac29372652c19138a2f1baad))


## v1.0.24 (2026-05-16)

### Bug Fixes

- Mqtt publish queue and operation error management
  ([`13fff28`](https://github.com/EHylands/QolsysController/commit/13fff28b511658d03355bd100edad8af4a70a15f))

- Mqtt publish queue and operation error management
  ([`ad0860d`](https://github.com/EHylands/QolsysController/commit/ad0860d969b51360a2522e6207f5c0d7fb85f576))


## v1.0.23 (2026-05-11)

### Bug Fixes

- Cryptography>=44.0.1,<=47.0.0 requirement
  ([`04d3520`](https://github.com/EHylands/QolsysController/commit/04d352072c92371932fe17663e10120803460c66))


## v1.0.22 (2026-05-11)

### Bug Fixes

- Fix Brooker typo and reset cryptography dependency
  ([`c70c8b6`](https://github.com/EHylands/QolsysController/commit/c70c8b6cb45fa82c56c8249106b4301fc6e43a25))

### Chores

- Broker typo
  ([`00712b6`](https://github.com/EHylands/QolsysController/commit/00712b6400fe2a83e69578fce7bb0b6fc6113e50))

- Fix "brooker" typo to "broker"
  ([`c7991b1`](https://github.com/EHylands/QolsysController/commit/c7991b1e2fdfae6a482a7420426dffceccf0a5c1))

- Fix "brooker" typo to "broker"
  ([`5769d4c`](https://github.com/EHylands/QolsysController/commit/5769d4cf61b145334d6ee36d2a66ec4170559d62))

- Reset cryptography dependency to older versio
  ([`42386e5`](https://github.com/EHylands/QolsysController/commit/42386e5d5517bee30b2c2c11cbd6f91ed5b7a014))

- Update CI-CD job names
  ([`976d4f4`](https://github.com/EHylands/QolsysController/commit/976d4f4f55bcc87f542858634053292dd4b5e807))

- **deps**: Bump actions/checkout from 4 to 6
  ([#45](https://github.com/EHylands/QolsysController/pull/45),
  [`a4b9299`](https://github.com/EHylands/QolsysController/commit/a4b9299d54037c0fd6925dc23a991a24ac0f29e3))

- **deps**: Bump actions/setup-python from 5 to 6
  ([#44](https://github.com/EHylands/QolsysController/pull/44),
  [`04e5bb6`](https://github.com/EHylands/QolsysController/commit/04e5bb6c0c41b2a540557c0e21e39c038a94f4cb))

- **deps**: Bump cryptography from 47.0.0 to 48.0.0
  ([#42](https://github.com/EHylands/QolsysController/pull/42),
  [`9d9755b`](https://github.com/EHylands/QolsysController/commit/9d9755b7c5ac00c3b8e5a67e2c915921e7afb4c2))

- **deps**: Bump wagoid/commitlint-github-action from 5 to 6
  ([#43](https://github.com/EHylands/QolsysController/pull/43),
  [`f206016`](https://github.com/EHylands/QolsysController/commit/f206016d51d83b921c8c106ad3c00368ed061ee7))


## v1.0.21 (2026-05-08)

### Bug Fixes

- Resolve issue where panel failed to reconnect after stop_operation() was called
  ([`bd0169c`](https://github.com/EHylands/QolsysController/commit/bd0169c08e5f352b1b5b57ccebccf0c2e6ff1d0d))

### Chores

- Update Readme.md
  ([`7110813`](https://github.com/EHylands/QolsysController/commit/71108131750d36d1c82881c1871cb1ac72c266ea))


## v1.0.20 (2026-05-07)

### Bug Fixes

- Removing break from final statement
  ([`c03c034`](https://github.com/EHylands/QolsysController/commit/c03c034e40b1eafacd7b85e49160b75b57a4f7d3))


## v1.0.19 (2026-05-06)

### Bug Fixes

- Ci-cd last try
  ([`74eb86b`](https://github.com/EHylands/QolsysController/commit/74eb86b7c591a52938f1ec67713480d5e8501b33))


## v1.0.18 (2026-05-06)

### Bug Fixes

- Trigger CI rebuild
  ([`c34f4e1`](https://github.com/EHylands/QolsysController/commit/c34f4e141d8ee06e97573d3adea6bb3dae8d8f82))

- Trigger ci-cd
  ([`16d254c`](https://github.com/EHylands/QolsysController/commit/16d254ced6eefdbd579bf13940b990ea30f61143))


## v1.0.17 (2026-05-06)

### Bug Fixes

- Ci-cd push tags
  ([`ccab9ea`](https://github.com/EHylands/QolsysController/commit/ccab9eac37aa4bcd92a8a9d8b5e8ccadf1c6629f))


## v1.0.16 (2026-05-06)

### Bug Fixes

- Ci-cd pypi on tag
  ([`1904ec0`](https://github.com/EHylands/QolsysController/commit/1904ec042c932b5b0c14bd579d2686b695a5ce2a))


## v1.0.15 (2026-05-06)

### Bug Fixes

- Ci-cd publish
  ([`cadc771`](https://github.com/EHylands/QolsysController/commit/cadc771af75a6ebe88b2ca3da0214ba8851c08ea))


## v1.0.14 (2026-05-06)

### Bug Fixes

- Ci-cd
  ([`a493a31`](https://github.com/EHylands/QolsysController/commit/a493a3189622833bc0b18bceccc8c867e6b1dd6d))


## v1.0.13 (2026-05-06)

### Bug Fixes

- Ci-cd release on new tag
  ([`9e342a2`](https://github.com/EHylands/QolsysController/commit/9e342a2005deab36b6e41bffb04f35d798a83ca3))


## v1.0.12 (2026-05-06)

### Bug Fixes

- Ci-cd pipeline
  ([`dbfc83d`](https://github.com/EHylands/QolsysController/commit/dbfc83deac253a62a3d4d6750a040214cb1d41d8))


## v1.0.11 (2026-05-06)

### Bug Fixes

- Ci-cd
  ([`39613be`](https://github.com/EHylands/QolsysController/commit/39613be208cfa7fe9ce0bdc4ab498ed6940a90dd))


## v1.0.10 (2026-05-06)

### Bug Fixes

- Ci-cd 3 pipeline
  ([`9d8dac0`](https://github.com/EHylands/QolsysController/commit/9d8dac0c3afb414e3100e775476ed9aae864be19))

### Chores

- Save local changes
  ([`74784ad`](https://github.com/EHylands/QolsysController/commit/74784adb0fa7249a583f332915ed51074c5a3cf4))


## v1.0.9 (2026-05-06)

### Bug Fixes

- Ci-cd
  ([`53c3b6c`](https://github.com/EHylands/QolsysController/commit/53c3b6c0ad0f035678962cc238b1d7b902228c56))


## v1.0.8 (2026-05-06)

### Bug Fixes

- Ci-cd (separate in 2 files)
  ([`c8f3250`](https://github.com/EHylands/QolsysController/commit/c8f32501516e4714e09d4be290168c1f3bdd079a))


## v1.0.7 (2026-05-06)

### Bug Fixes

- (ci-cd) publish.yml
  ([`f061a52`](https://github.com/EHylands/QolsysController/commit/f061a52f005a26373e22e73ca6cb9e2ba6ef475f))

- Ci-cd
  ([`a5d4cb8`](https://github.com/EHylands/QolsysController/commit/a5d4cb802ba2a3ffffa87de904255c24d6d455bc))


## v1.0.4 (2026-05-05)

### Bug Fixes

- Ci-cd
  ([`a40a417`](https://github.com/EHylands/QolsysController/commit/a40a417b5b9c07039c7810da20333104a0fa3221))

- Ci-cd
  ([`4bafdff`](https://github.com/EHylands/QolsysController/commit/4bafdff12c5612a1e8f62f4dbd8f4d2fa0ead059))

- Zone sensor group takeovermodule and nightmotion
  ([#38](https://github.com/EHylands/QolsysController/pull/38),
  [`25e6784`](https://github.com/EHylands/QolsysController/commit/25e6784af955f90dc269d145dd0340de62d94435))

### Chores

- Ci-cd
  ([`3d7f2ad`](https://github.com/EHylands/QolsysController/commit/3d7f2ad9b59ad5a6999057ddca84bd3726f9d384))


## v1.0.3 (2026-05-05)


## v1.0.2 (2026-05-05)

### Bug Fixes

- Ci-cd pipeline
  ([`a3cd266`](https://github.com/EHylands/QolsysController/commit/a3cd26611747d5bca2bc561d3828c6683c30285e))


## v1.0.1 (2026-05-04)

### Bug Fixes

- Ci-cd pipeline
  ([`50c322f`](https://github.com/EHylands/QolsysController/commit/50c322f7286ff65f66dd079b5a1d78e6c27bc014))

- Trigger 1.0.1 release
  ([`8a27882`](https://github.com/EHylands/QolsysController/commit/8a278825f898315a04517a97218e8d4a97813930))

- Trigger next release
  ([`1559963`](https://github.com/EHylands/QolsysController/commit/1559963dc197c41271f7df6dab4a968f7c334ecf))


## v1.0.0 (2026-05-04)


## v0.5.8 (2026-05-02)


## v0.5.7 (2026-04-27)


## v0.5.6 (2026-04-20)


## v0.5.5 (2026-04-13)


## v0.5.4 (2026-04-13)


## v0.5.3 (2026-04-13)


## v0.5.2 (2026-04-12)


## v0.5.1 (2026-04-12)


## v0.5.0 (2026-04-12)


## v0.4.37 (2026-03-28)


## v0.4.36 (2026-03-27)


## v0.4.35 (2026-03-27)


## v0.4.34 (2026-03-24)


## v0.4.33 (2026-03-22)


## v0.4.32 (2026-03-22)


## v0.4.31 (2026-03-22)


## v0.4.30 (2026-03-20)


## v0.4.29 (2026-03-20)


## v0.4.28 (2026-03-10)


## v0.4.27 (2026-03-08)


## v0.4.26 (2026-03-07)


## v0.4.25 (2026-03-07)


## v0.4.24 (2026-03-07)


## v0.4.23 (2026-03-07)


## v0.4.22 (2026-03-07)


## v0.4.21 (2026-03-06)


## v0.4.20 (2026-03-04)


## v0.4.19 (2026-03-02)


## v0.4.18 (2026-02-28)


## v0.4.17 (2026-02-25)


## v0.4.16 (2026-02-24)


## v0.4.15 (2026-02-24)


## v0.4.14 (2026-02-23)


## v0.4.13 (2026-02-23)


## v0.4.12 (2026-02-23)


## v0.4.11 (2026-02-23)


## v0.4.10 (2026-02-22)


## v0.4.9 (2026-02-20)


## v0.4.8 (2026-02-20)


## v0.4.7 (2026-02-19)


## v0.4.6 (2026-02-15)


## v0.4.5 (2026-02-14)


## v0.4.4 (2026-02-05)


## v0.4.3 (2026-02-03)


## v0.4.2 (2026-02-02)


## v0.4.1 (2026-02-02)


## v0.4.0 (2026-02-02)


## v0.3.12 (2026-02-01)


## v0.3.11 (2026-01-28)


## v0.3.10 (2026-01-25)


## v0.3.9 (2026-01-25)


## v0.3.8 (2026-01-24)


## v0.3.7 (2026-01-24)


## v0.3.6 (2026-01-19)


## v0.3.4 (2026-01-18)


## v0.3.3 (2026-01-18)


## v0.3.2 (2026-01-18)


## v0.3.1 (2026-01-17)


## v0.3.0 (2026-01-17)


## v0.3.5 (2026-01-17)


## v0.2.9 (2026-01-15)


## v0.2.7 (2026-01-14)


## v0.2.5 (2026-01-11)


## v0.2.4 (2026-01-11)


## v0.2.3 (2026-01-10)


## v0.2.2 (2026-01-09)


## v0.2.0 (2026-01-09)


## v0.2.6 (2026-01-11)


## v0.1.1 (2026-01-08)


## v0.1.0 (2026-01-08)


## v0.0.90 (2026-01-05)


## v0.0.89 (2026-01-05)


## v0.0.88 (2026-01-05)


## v0.0.87 (2026-01-04)


## v0.0.86 (2026-01-03)


## v0.0.85 (2026-01-02)


## v0.0.84 (2026-01-02)


## v0.0.83 (2026-01-02)


## v0.0.82 (2026-01-02)


## v0.0.81 (2026-01-01)


## v0.0.80 (2026-01-01)


## v0.0.79 (2025-12-30)


## v0.0.78 (2025-12-30)


## v0.0.77 (2025-12-28)


## v0.0.76 (2025-12-26)


## v0.0.75 (2025-12-25)


## v0.0.74 (2025-12-24)


## v0.0.73 (2025-12-24)


## v0.0.72 (2025-12-23)


## v0.0.71 (2025-12-23)


## v0.0.70 (2025-12-21)


## v0.0.69 (2025-12-21)


## v0.0.68 (2025-12-21)


## v0.0.67 (2025-12-13)


## v0.0.66 (2025-12-13)


## v0.0.65 (2025-12-10)


## v0.0.64 (2025-12-09)


## v0.0.63 (2025-12-08)


## v0.0.62 (2025-12-05)


## v0.0.61 (2025-12-05)


## v0.0.60 (2025-11-20)


## v0.0.59 (2025-11-20)


## v0.0.58 (2025-11-19)


## v0.0.57 (2025-11-19)


## v0.0.56 (2025-11-12)


## v0.0.55 (2025-11-12)


## v0.0.54 (2025-11-11)


## v0.0.53 (2025-11-10)


## v0.0.52 (2025-11-09)


## v0.0.51 (2025-11-09)


## v0.0.50 (2025-11-08)


## v0.0.49 (2025-11-08)


## v0.0.48 (2025-11-04)


## v0.0.47 (2025-10-28)


## v0.0.46 (2025-10-28)


## v0.0.45 (2025-10-28)


## v0.0.44 (2025-10-27)


## v0.0.43 (2025-10-27)


## v0.0.42 (2025-10-27)


## v0.0.41 (2025-10-27)


## v0.0.40 (2025-10-21)


## v0.0.39 (2025-10-21)


## v0.0.38 (2025-10-21)


## v0.0.37 (2025-10-20)


## v0.0.36 (2025-10-19)


## v0.0.35 (2025-10-19)


## v0.0.34 (2025-10-15)


## v0.0.33 (2025-10-15)


## v0.0.32 (2025-10-15)


## v0.0.31 (2025-10-13)


## v0.0.30 (2025-10-13)


## v0.0.29 (2025-10-13)


## v0.0.27 (2025-10-13)


## v0.0.26 (2025-10-13)


## v0.0.25 (2025-10-13)


## v0.0.24 (2025-10-12)


## v0.0.23 (2025-10-12)


## v0.0.22 (2025-10-12)


## v0.0.21 (2025-10-12)


## v0.0.20 (2025-10-12)


## v0.0.19 (2025-10-11)


## v0.0.18 (2025-10-10)


## v0.0.17 (2025-10-10)


## v0.0.16 (2025-10-08)


## v0.0.15 (2025-10-08)


## v0.0.14 (2025-10-08)


## v0.0.13 (2025-10-08)


## v0.0.12 (2025-10-08)


## v0.0.10 (2025-10-08)


## v0.0.9 (2025-10-05)


## v0.0.8 (2025-09-29)


## v0.0.7 (2025-09-29)


## v0.0.6 (2025-09-29)


## v0.0.5 (2025-09-28)


## v0.0.4 (2025-09-28)


## v0.0.3 (2025-09-28)

- Initial Release
