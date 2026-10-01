# Slurm + QRMI + Warden HPC training

Hands-on training for HPC administrators on integrating a Pasqal QPU into a Slurm cluster. You deploy a toy Slurm cluster in Docker, install the [SPANK plugin](https://github.com/qiskit-community/spank-plugins), the [QRMI](https://github.com/qiskit-community/qrmi) and the [Warden](https://github.com/pasqal-io/warden) middleware, then run quantum jobs against a mock QPU and practice the main admin tasks.

Requirements: `docker` and `git`.

## 1-Introduction 

[link](1_intro/HANDSON.md)

## 2-Solution Stack

[link](2_stack/HANDSON.md)

## 3-Admin

[link](3_admin/HANDSON.md)


# Resources

The Slurm docker cluster in [`hands-on/`](hands-on/) is based on Giovanni Torres's [slurm-docker-cluster](https://github.com/giovtorres/slurm-docker-cluster), Copyright (c) 2024 Giovanni Torres, licensed under the MIT License (see [hands-on/LICENSE.slurm-docker-cluster](hands-on/LICENSE.slurm-docker-cluster)).

Mentioned repos and documentation
- [QRMI](https://github.com/qiskit-community/qrmi)
- [Spank plugin](https://github.com/qiskit-community/spank-plugins)
- [Warden](https://github.com/pasqal-io/warden)
- [Pasqal documentation](https://docs.pasqal.com/)
    - [Pulser](https://docs.pasqal.com/pulser/)
    - [QoolQit](https://docs.pasqal.com/qoolqit/)
    - [QUBO](https://docs.pasqal.com/applicationsolvingtools/qubo/)

# License

Copyright © 2026 Pasqal.

- The training text (the `HANDSON.md` files and this README) is licensed under the [Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). You may share and adapt it for any purpose, including commercially, as long as you give appropriate credit to Pasqal, link to the license, and indicate if changes were made. See [LICENSE](LICENSE) for the full text.
- The code and configuration in [`hands-on/`](hands-on/) are licensed under the Pasqal Open-Source Software License (MIT-derived), the same license as [Warden](https://github.com/pasqal-io/warden). See [hands-on/LICENSE](hands-on/LICENSE). Parts derived from [slurm-docker-cluster](https://github.com/giovtorres/slurm-docker-cluster) remain under its MIT License, see [hands-on/LICENSE.slurm-docker-cluster](hands-on/LICENSE.slurm-docker-cluster).

The software used in the training is not part of this repository and keeps its own license:
[Warden](https://github.com/pasqal-io/warden) (Pasqal Open-Source Software License),
[QRMI](https://github.com/qiskit-community/qrmi) (Apache-2.0) and
the [SPANK plugins](https://github.com/qiskit-community/spank-plugins) (GPL-3.0, following the Slurm license).
