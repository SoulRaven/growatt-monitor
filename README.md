# ⚡ Growatt monitor

Growatt inverter monitor from Modbus and API server

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

## Methods and Variables

### Methods

`api.login(username, password)` Log into the growatt API. This must be done before making any request. After this you will be logged in. You will want to capture the response to get the `userId` variable.

`api.plant_list(user_id)` Get a list of plants registered to your account.

`api.plant_info(plant_id)` Get info for specified plant.

`api.plant_detail(plant_id, timespan<1=day, 2=month>, date)` Get details of a specific plant.

`api.inverter_list(plant_id)` Get a list of inverters in specified plant. (May be deprecated in the future, since it gets all devices. Use `device_list` instead).

`api.device_list(plant_id)` Get a list of devices in specified plant.

`api.inverter_data(inverter_id, date)` Get some basic data of a specific date for the inverter.

`api.inverter_detail(inverter_id)` Get detailed data on inverter.

`api.tlx_data(tlx_id, date)` Get some basic data of a specific date for the tlx type inverter.

`api.tlx_detail(tlx_id)` Get detailed data on a tlx type inverter.

`api.mix_info(mix_id, plant_id=None)` Get high level information about the Mix system including daily and overall totals. NOTE: `plant_id` is an optional parameter, it does not appear to be used by the remote API, but is used by the mobile app these calls were reverse-engineered from.

`api.mix_totals(mix_id, plant_id)` Get daily and overall total information for the Mix system (duplicates some of the information from `mix_info`).

`api.mix_system_status(mix_id, plant_id)` Get instantaneous values for Mix system e.g. current import/export, generation, charging rates etc.

`api.mix_detail(mix_id, plant_id, timespan=<0=hour, 1=day, 2=month>, date)` Get detailed values for a timespan, the API call also returns totals data for the same values in this time window

`api.dashboard_data(plant_id, timespan=<0=hour, 1=day, 2=month>, date)` Get dashboard values for a timespan, the API call also returns totals data for the same values in this time window. NOTE: Many of the values on this API call are incorrect for 'Mix' systems, however it still provides some accurate values that are unavailable on other API calls.

`api.storage_detail(storage_id)` Get detailed data on storage (battery).

`api.storage_params(storage_id)` Get a ton of info on storage (More info, more convoluted).

`api.storage_energy_overview(plant_id, storage_id)` Get the information you see in the "Generation overview".

`api.get_plant_settings(plant_id)` Get the current settings for the specified plant

`api.update_plant_settings(plant_id, changed_settings, current_settings)` Update the settings for a plant to the values specified in the dictionary, if the `current_settings` are not provided it will look them up automatically using the `get_plant_settings` function - See 'Plant settings' below for more information

`api.update_mix_inverter_setting(serial_number, setting_type, parameters)` Applies the provided parameters (dictionary or array) for the specified setting on the specified inverter - See 'Inverter settings' below for more information - Appears to be limited to "mix" systems

### Variables

Some variables you may want to set.

`api.server_url` The growatt server URL, default: 'https://server.growatt.com/'

### 🌍 Contributions

Contributions of all forms are welcome :)

## 🗒 License

This repository is licensed under the GNU General Public License, version 3 (GPLv3).

## 👀 Author

Zaharia Constantin

[View my GitHub profile 💡](https://github.com/soulraven)
