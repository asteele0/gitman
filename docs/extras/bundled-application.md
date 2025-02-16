# Self-Contained / Portable Gitman

There are scenarios where a global Gitman installation via [pip](https://github.com/pypa/pip) or a local Gitman installation via [Poetry](https://github.com/sdispater/poetry) is not possible or difficult to manage.
For example, when a local system doesn't have the required python or pip version installed and or the global installation may produce side effects (different parallel python versions on the same machine).
Furthermore there are scenarios where a high degree of reproducibility, managing multiple different versions of Gitman on the same machine and hassle free distribution of Gitman is desired.

In these scenarios, it can be helpful to use a self contained Gitman application besides the possibility to use a virtual environment (e.g. via pyenv + Poetry or Docker).
It is possible to build a single self contained OS-specific Gitman binary using [PyInstaller](https://www.pyinstaller.org/) that can be used locally or globally.
Over this way it is possible to manage multiple different versions of Gitman on the same machine and to easily distribute the Gitman application (including all needed dependencies) by simply copying one single file.

Following this approach, the `gitman.yml` and the corresponding compatible version of the Gitman application can be managed side by side in the same repository to ensure
reproducibility and easy distribution.

## Prerequisites

### General prerequisites

The [PyInstaller](https://www.pyinstaller.org/) will encapsulate the required parts of the local installed python version and the needed modules in the self contained Gitman binary.

In this matter, ensure that the required python version and development tools are locally available (see [Gitman requirements](../index.md#Setup) and [development setup](../about/contributing.md#Setup)).

The compatible PyInstaller package will be automatically resolved by poetry. It is not necessary to explicitly install the PyInstaller via pip.

Furthermore OS-specifc prerequisites are required.
Below there are some well-known prerequisites listed.
Depending on the local system it may need further steps to do.

### Linux prerequisites

Install the corresponding python developer package.

**Debian-based distros (e.g. Mint, Ubuntu, Xubuntu)**

```sh
$ sudo apt-get install python-dev
```

In cases where multiple python versions are installed it is may
helpful to specify the concrete version of the python developer package like:

```sh
$ sudo apt-get install python3.7-dev
```

**Fedora-based distros (e.g. CentOS)**

```sh
$ yum install python-devel
```

### Windows  prerequisites

- install make via [cygwin](https://www.cygwin.com/) or [mingw](http://www.mingw.org/) (add the path to make to the PATH-Environment Variable e.g. C:\cygwin\bin)
- install [pywin32](https://github.com/mhammond/pywin32) according the used python version and system architecture (e.g. for python 3.7 and amd64-architecture use pywin32-224.win-amd64-py3.7.exe)

### macOS prerequisites

Some notes regarding macOS prerequisites can be found [here](https://pyinstaller.readthedocs.io/en/v3.3.1/installation.html#installing-in-mac-os-x).

## Binary Build

To build the self contained Gitman binary use:

```sh
$ make exe
```

By default this call installs the [PyInstaller](https://www.pyinstaller.org/) pip-Package as part of the Gitman virtual environment.

The build output is located in the `dist` folder.
