# ⚡ Growatt monitor

Growatt inverter monitor from Modbus and API server

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![PyPI](https://img.shields.io/pypi/v/growatt-monitor?label=GrowattMonitor&style=plastic)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/soulraven/growatt-monitor?style=plastic)
[![Build status](https://img.shields.io/github/workflow/status/soulraven/growatt-monitor/merge-to-main?style=plastic)](https://img.shields.io/github/workflow/status/soulraven/growatt-monitor/merge-to-main)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/growatt-monitor?style=plastic)](https://pypi.org/project/growatt-monitor/)
[![License](https://img.shields.io/github/license/soulraven/growatt-monitor?style=plastic)](https://img.shields.io/github/license/soulraven/growatt-monitor)


### 🔧 Installation
### Growatt monitor module
Download the repository and use [pip](https://pip.pypa.io/en/stable/) to install Growatt Monitor:
```bash
git clone https://github.com/soulraven/growatt-monitor.git
cd growatt-monitor
pip install -r requirements.txt .
```
To install for all users on the system, run pip as root:
```bash
sudo pip install -r requirements.txt .
```

### Documentation

The documentation is download from [http://growatt.pl](http://growatt.pl) website, more exactly from [https://growatt.pl/wp-content/uploads/2020/01/Growatt-Server-API-Guide.pdf](https://growatt.pl/wp-content/uploads/2020/01/Growatt-Server-API-Guide.pdf)

Another documentation is provided by the Growatt email support: [https://www.showdoc.com.cn/262556420217021/](https://www.showdoc.com.cn/262556420217021/) and the password is: **123456**

- Swagger definition object generator: https://roger13.github.io/SwagDefGen/


### Variables

Some variables you may want to set.

`api.server_url` The growatt server URL, default: 'https://server.growatt.com/'

### 📚 Library used
This package uses:

- [https://github.com/indykoning/PyPi_GrowattServer](https://github.com/indykoning/PyPi_GrowattServer)

### 🌍 Contributions

Contributions of all forms are welcome :)

## 🗒 License

This repository is licensed under the GNU General Public License, version 3 (GPLv3).

## 👀 Author

Zaharia Constantin

[View my GitHub profile 💡](https://github.com/soulraven)
