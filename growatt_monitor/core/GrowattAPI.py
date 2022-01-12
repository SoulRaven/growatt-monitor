#  -*- coding: utf-8 -*-
#
#              Copyright (C) 2018-<copyright_year> ProGeek
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import datetime

from growatt_monitor.conf import settings
from growatt_monitor.utils.hashable import hash_password
from growatt_monitor.utils.decorators import session_manager
from growatt_monitor.utils.datetime import Timespan
from growatt_monitor.core.exceptions import LoginError, GrowattApiError, ImproperlyConfigured
from growatt_monitor.core.SessionFactory import SessionFactory

log = logging.getLogger('growatt_logging')


class GrowattAPI(SessionFactory):

    def __init__(self, *args, **kwargs):
        """ Init the class with specific **kwargs if you don't want to use default settings
        Without `username` or `password` field the class will search for `API_KEY`.
        If not an ex exception will be thrown

        :param kwargs:
        """

        super().__init__(*args, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.logged_in:
            self.logout()

    def _get_date_string(self, timespan=None, date=None) -> str:
        if timespan is not None:
            assert timespan in Timespan

        date_str = ""
        if date is None:
            date = datetime.datetime.now()



        return date_str

    def login(self):
        """Log in to the Growatt server, or raise an exception if this fails.
        """

        response = self.session.post(
            self.get_url("newLoginAPI.do"),
            data={"userName": self.username, "password": self.password}
        )

        try:
            result = self.process_response(response)

            # if the login is OK then update the dictionary with new data for convenience
            result.update({
                'userId': result["user"]["id"],
                'userLevel': result["user"]["rightlevel"]
            })

            # set the login flag to TRUE
            self.logged_in = True
            log.debug("User session logged in and flag set to TRUE")
            return result
        except GrowattApiError as e:
            self.logged_in = False
            log.exception("Login data is invalid, please check again username and password")
            raise LoginError("Login data is invalid, please check again username and password")

    def logout(self):
        self.session.get(self.get_url("logout.do"))
        # set the login flag to FALSE
        self.logged_in = False
        log.debug('User session logged out and flag set to FALSE!')

    def plant_list(self):
        """
        Retrieve all plants belonging to the current user.

        Return JSON object:

        'data' -- A List containing Objects containing the following
            'plantMoneyText'
            'storageStatus'
            'plantName' -- Friendly name of the plant
            'plantId'   -- The ID of the plant
            'storagePCharge'
            'storageCapacity'
            'isHaveStorage'
            'todayEnergy'
            'storagePDisCharge'
            'totalEnergy'
            'currentPower'
        'totalData' --
            'currentPowerSum'
            'storageCapacity'
            'storagePCharge'
            'CO2Sum'
            'isHaveStorage'
            'eTotalMoneyText'
            'storagePDisCharge'
            'todayEnergySum'
            'totalEnergySum'
            'storagePacToUser'
        'success'   -- True or False

        """

        response = self.session.get(
            self.get_url("PlantListAPI.do"),
            allow_redirects=False,
            headers=self.headers
        )

        return self.process_response(response)

    def plant_detail(self, plant_id, timespan, date=None):
        """
        Return amount of power generated for the given timespan.
        * Timespan.day : power on each half hour of the day.
        * Timespan.month : power on each day of the month.
        * Timespan.year: power on each month of the year.
        * Timespan.total: power on each year. `date` parameter is ignored.

        Return JSON Object:

        'plantData'
            'plantMoneyText'
            'plantName'
            'plantId'
            'currentEnergy'
        'data'
        'success'

        """
        assert timespan in Timespan
        date_str = timespan.format_date(date)

        response = self.session.get(
            self.get_url("PlantDetailAPI.do"),
            params={
                "plantId": plant_id,
                "type": timespan.value,
                "date": date_str
            },
        )

        return self.process_response(response)

    def new_plant_detail(self, plant_id, timespan, date):
        """
        Return amount of power generated for the given timespan.
        * Timespan.day : power on each five minutes of the day.
        * Timespan.month : power on each day of the month.
        * Timespan.year: power on each month of the year.
        * Timespan.total: power on each year. `date` parameter is ignored.

        Return JSON Object:

        'plantData'
            'plantMoneyText'
            'plantName'
            'plantId'
            'currentEnergy'
        'data'
        'success'

        """
        assert timespan in Timespan
        date_str = timespan.format_date(date)

        response = self.session.get(
            self.get_url("newPlantDetailAPI.do"),
            params={
                "plantId": plant_id,
                "type": timespan.value,
                "date": date_str
            },
        )

        return self.process_response(response)

    def get_user_center_energy_data(self):
        """
        Get overall data including:
        * powerValue - current power in Watt
        * todayValue - power generated today
        
        Return JSON Object:
        
        'monthProfitStr'
        'todayProfitStr'
        'plantNumber'
        'treeValue'
        'treeStr'
        'nominalPowerStr'
        'eventMessBeanList'
        'yearValue'
        'formulaCo2Vlue'
        'formulaCo2Str'
        'todayValue'
        'totalStr'
        'powerValue'
        'totalValue'
        'nominalPowerValue'
        'powerValueStr'
        'monthValue'
        'todayStr'
        'monthStr'
        'formulaCoalStr'
        'alarmValue'
        'totalProfitStr'
        'yearStr'
        'formulaCoalValue'
   
        """
        response = self.session.post(
            self.get_url("newPlantAPI.do"),
            params={
                "action": "getUserCenterEnertyData"
            },  # sic url, but is working
            data={
                "language": 1
            },
        )

        return self.process_response(response)

    def get_all_device_list(self, plant_id):
        """
        Get information on each device/inverter.
        
        Return JSON Object:
        
        'plantMoneyText
        'optimizerType'
        'ammeterType'
        'storagePgrid'
        'todayEnergy'
        'storageTodayPpv'
        'invTodayPpv'
        'totalEnergy'
        'nominalPower'
        'todayDischarge'
        'Co2Reduction'
        'isHaveOptimizer'
        'storagePuser'
        'useEnergy'
        'totalMoneyText'
        'nominal_Power'
        'deviceList'
            'lost'
            'location'
            'datalogSn
            'deviceSn
            'deviceStatus'
            'pCharge'
            'activePower'
            'deviceAilas'
            'deviceType'
            'storageType'
            'eChargeToday'
            'apparentPower'
            'capacity'
            'energy'
        'isHavePumper'
   
        """
        response = self.session.post(
            self.get_url("newTwoPlantAPI.do"),
            params={
                "op": "getAllDeviceList",
                "plantId": plant_id,
                'pageNum': 1,
                'pageSize': 1
            }
        )

        return self.process_response(response)

    def device_list(self, plant_id):
        """
        Get a list of all devices connected to plant.
        """
        return self.get_all_device_list(plant_id)['deviceList']

    def get_plant_settings(self, plant_id):
        """
        Returns a dictionary containing the settings for the specified plant

        Return JSON Object:

        'map_cityId'
        'map_countryId'
        'storage_BattoryPercentage'
        'defaultPlant'
        'peakPeriodPrice'
        'city'
        'nominalPower'
        'alarmValue'
        'currentPacTxt'
        'fixedPowerPrice'
        'plantFromBean'
        'deviceCount'
        'plantImgName'
        'etodaySo2Text'
        'companyName'
        'emonthMoneyText'
        'formulaMoney'
        'userAccount'
        'mapLat'
        'createDateTextA'
        'mapLng'
        'onLineEnvCount'
        'eventMessBeanList'
        'latitudeText'
        'plantAddress'
        'hasDeviceOnLine'
        'formulaMoneyStr'
        'etodayMoney'
        'createDate'
            'time'
            'minutes'
            'seconds'
            'hours'
            'month'
            'year'
            'timezoneOffset'
            'day'
            'date'
        'mapCity'
        'prMonth'
        'storage_TodayToGrid'
        'formulaCo2'
        'eTotal'
        'emonthSo2Text'
        'windAngle'
        'etotalCoalText'
        'windSpeed'
        'emonthCoalText'
        'etodayMoneyText'
        'EYearMoneyText'
        'plant_lng'
        'latitude_m'
        'pairViewUserAccount'
        'storage_TotalToUser'
        'latitude_d'
        'latitude_f'
        'remark'
        'treeID'
        'flatPeriodPrice'
        'longitudeText'
        'storage_eChargeToday'
        'dataLogList'
        'designCompany'
        'timezoneText'
        'formulaCoal'
        'storage_eDisChargeToday'
        'unitMap'
            'DOLLAR'
            'JPY'
            'THP'
            'LKR'
            'VND'
            'NT'
            'CAD'
            'AUD'
            'NZD'
            'ZAR'
            'GBP'
            'Euro'
            'NOK'
            'ISK'
            'CHF'
            'UAH'
            'PKR'
            'INR'
            'RMB'
            'IDR'
            'TRY'
            'REAL'
            'SGD'
            'HKD'
            'BUK'
            'KHR'
            'DKK'
            'MYR'
            'ARP'
            'SEK'
            'EUR'
            'PHP'
            'HUF'
            'PLN'
            'USD'
            'LAK'
            'BRC'
        'timezone'
        'phoneNum'
        'level'
        'formulaMoneyUnitId'
        'imgPath'
        'panelTemp'
        'locationImgName'
        'moneyUnitText'
        'storage_TotalToGrid'
        'prToday'
        'energyMonth'
        'plantName'
        'eToday'
        'status'
        'plantType'
        'country'
        'longitude_d'
        'map_areaId'
        'longitude_f'
        'createDateText'
        'longitude_m'
        'formulaSo2'
        'valleyPeriodPrice'
        'energyYear'
        'treeName'
        'plant_lat'
        'etodayCo2Text'
        'nominalPowerStr'
        'formulaTree'
        'etotalSo2Text'
        'children'
        'id'
        'etodayCoalText'
        'paramBean'
        'etotalFormulaTreeText'
        'etotalMoney'
        'envTemp'
        'logoImgName'
        'alias'
        'etotalCo2Text'
        'currentPacStr'
        'map_provinceId'
        'etotalMoneyText'
        'emonthCo2Text'
        'irradiance'
        'hasStorage'
        'parentID'
        'userBean'
        'storage_TodayToUser'
        'isShare'
        'currentPac'

        :param plant_id: The id of the plant you want the settings of
        :return: A python dictionary containing the settings for the specified plant

        """
        response = self.session.get(
            self.get_url('newPlantAPI.do'),
            params={
                'op': 'getPlant',
                'plantId': plant_id
            })

        return self.process_response(response)

    def inverter_data(self, inverter_id, date=None):
        """
        Get inverter data for specified date or today

        :param inverter_id:
        :param date:
        :return:

        """
        tiemspan = Timespan.day
        date_str = tiemspan.format_date(date)

        response = self.session.get(
            self.get_url('newInverterAPI.do'),
            params={
                'op': 'getInverterData',
                'id': inverter_id,
                'type': 1,
                'date': date_str
            })
        return self.process_response(response)

    def inverter_detail(self, inverter_id):
        """
        Get "All parameters" from PV inverter.

        Return JSON Object:

        'powerToday'
        'realOPPercent'
        'eRacTotal'
        'epv1Total'
        'wStringStatusValue'
        'vPidPvape'
        'warningValue1'
        'warningValue2'
        'temperature'
        'bigDevice':false,
        'warnCode'
        'time',
        'iPidPvbpe'
        'inverterId',
        'epv2Total'
        'timeCalendar',
        'pBusVoltage'
        'currentString5'
        'strFault'
        'currentString4'
        'currentString3'
        'currentString2'
        'status'
        'currentString8'
        'currentString7'
        'currentString6'
        'nBusVoltage'
        'again':false,
        'currentString1'
        'ipmTemperature'
        'ppv'
        'pacs'
        'pacr'
        'pf'
        'pact'
        'vpv1'
        'iPidPvape'
        'vpv3'
        'vpv2'
        'fac'
        'vPidPvbpe'
        'powerTotal'
        'epv2Today'
        'ipv3'
        'ipv2'
        'ipv1'
        'statusText',
        'timeTotal'
        'epv1Today'
        'id'
        'timeTotalText',
        'dwStringWarningValue1'
        'epvTotal'
        'pac'
        'vact'
        'vacr'
        'vacs'
        'vString1'
        'vString2'
        'vString3'
        'vString4'
        'faultType'
        'vString5'
        'vString6'
        'vString8'
        'iacs'
        'inverterBean',
        'opFullwatt'
        'pidStatus'
        'vString7'
        'iact'
        'eRacToday'
        'ppv3'
        'wPIDFaultValue'
        'ppv2'
        'ppv1'
        'iacr'
        'rac'

        :param inverter_id:
        :return:

        """
        response = self.session.get(self.get_url('newInverterAPI.do'), params={
            'op': 'getInverterDetailData',
            'inverterId': inverter_id
        })

        return self.process_response(response)

    def inverter_detail_two(self, inverter_id):
        """
        Get "All parameters" from PV inverter.

        Return JSON Object:

        'data'
            'e_today'
            'e_total'
            'vpv1'
            'ipv1'
            'ppv1'
            'vpv2'
            'ipv2'
            'ppv2'
            'vpv3'
            'ipv3'
            'ppv3'
            'ppv'
            'vacr'
            'vacs'
            'vact'
            'iacr'
            'iacs'
            'iact'
            'fac'
            'pac'
            'pacr'
            'pacs'
            'pact'
            'rac'
            'e_rac_today'
            'e_rac_total'
            't_total'
            'vstring1'
            'istring1'
            'vstring2'
            'istring2'
            'vstring3'
            'istring3'
            'vstring4'
            'istring4'
            'vstring5'
            'istring5'
            'vstring6'
            'istring6'
            'vstring7'
            'istring7'
            'vstring8
            'istring8
            'strfault'
            'strwarning'
            'strbreak'
            'pidwarning'
        'parameterName'
            'Fac(Hz)
            Pac(W)
            E_Today(kWh)
            E_Total(kWh)
            Vpv1(V)
            Ipv1(A)
            Ppv1(W)
            Vpv2(V)
            Ipv2(A)
            Ppv2(W)
            Vpv3(V)
            Ipv3(A)
            Ppv3(W)
            Ppv(W)
            VacR(V)
            VacS(V)
            VacT(V)
            IacR(A)
            IacS(A)
            IacT(A)
            PacR(W)
            PacS(W)
            PacT(W)
            Rac(W)
            E_Rac_Today(W)
            E_Rac_Total(W)
            T_Total(H)
            Vstring1(V)
            Istring1(A)
            Vstring2(V)
            Istring2(A)
            Vstring3(V)
            Istring3(A)
            Vstring4(V)
            Istring4(A)
            Vstring5(V)
            Istring5(A)
            Vstring6(V)
            Istring6(A)
            Vstring7(V)
            Istring7(A)
            Vstring8(V)
            Istring8(A)
            StrFault
            StrWarning
            StrBreak
            PIDWarning

        """
        response = self.session.get(self.get_url('newInverterAPI.do'), params={
            'op': 'getInverterDetailData_two',
            'inverterId': inverter_id
        })

        return self.process_response(response)

    def tlx_data(self, tlx_id, date=None):
        """
        Get some basic data of a specific date for the tlx type inverter.

        :param tlx_id:
        :param date:
        :return:
        """

        tiemspan = Timespan.day
        date_str = tiemspan.format_date(date)

        response = self.session.get(self.get_url('newTlxApi.do'), params={
            'op': 'getTlxData',
            'id': tlx_id,
            'type': 1,
            'date': date_str
        })

        return self.process_response(response)

    def tlx_detail(self, tlx_id):
        """
        Get "All parameters" from PV inverter.
        """
        response = self.session.get(self.get_url('newTlxApi.do'), params={
            'op': 'getTlxDetailData',
            'id': tlx_id
        })

        return self.process_response(response)

    def mix_info(self, mix_id, plant_id=None):
        """
        Returns high level values from Mix device

        :param mix_id: The serial number (device_sn) of the inverter
        :param plant_id: The ID of the plant (the mobile app uses this but it does not appear to be necessary) (default None)
        :return:

            'acChargeEnergyToday' -- ??? 2.7
            'acChargeEnergyTotal' -- ??? 25.3
            'acChargePower' -- ??? 0
            'capacity': '45' -- The current remaining capacity of the batteries (same as soc but without the % sign)
            'eBatChargeToday' -- Battery charged today in kWh
            'eBatChargeTotal' -- Battery charged total (all time) in kWh
            'eBatDisChargeToday' -- Battery discharged today in kWh
            'eBatDisChargeTotal' -- Battery discharged total (all time) in kWh
            'epvToday' -- Energy generated from PVs today in kWh
            'epvTotal' -- Energy generated from PVs total (all time) in kWh
            'isCharge'-- ??? 0 - Possible a 0/1 based on whether or not the battery is charging
            'pCharge1' -- ??? 0
            'pDischarge1' -- Battery discharging rate in W
            'soc' -- Statement of charge including % symbol
            'upsPac1' -- ??? 0
            'upsPac2' -- ??? 0
            'upsPac3' -- ??? 0
            'vbat' -- Battery Voltage
            'vbatdsp' -- ??? 51.8
            'vpv1' -- Voltage PV1
            'vpv2' -- Voltage PV2

        """

        request_params = {
            'op': 'getMixInfo',
            'mixId': mix_id
        }

        if plant_id:
            request_params['plantId'] = plant_id

        response = self.session.get(self.get_url('newMixApi.do'), params=request_params)

        return self.process_response(response).get('obj')

    def mix_totals(self, mix_id, plant_id):
        """
        Returns "Totals" values from Mix device

        :param mix_id: The serial number (device_sn) of the inverter
        :param plant_id: The ID of the plant
        :return:

            'echargetoday' -- Battery charged today in kWh (same as eBatChargeToday from mix_info)
            'echargetotal' -- Battery charged total (all time) in kWh (same as eBatChargeTotal from mix_info)
            'edischarge1Today' -- Battery discharged today in kWh (same as eBatDisChargeToday from mix_info)
            'edischarge1Total' -- Battery discharged total (all time) in kWh (same as eBatDisChargeTotal from mix_info)
            'elocalLoadToday' -- Load consumption today in kWh
            'elocalLoadTotal' -- Load consumption total (all time) in kWh
            'epvToday' -- Energy generated from PVs today in kWh (same as epvToday from mix_info)
            'epvTotal' -- Energy generated from PVs total (all time) in kWh (same as epvTotal from mix_info)
            'etoGridToday' -- Energy exported to the grid today in kWh
            'etogridTotal' -- Energy exported to the grid total (all time) in kWh
            'photovoltaicRevenueToday' -- Revenue earned from PV today in 'unit' currency
            'photovoltaicRevenueTotal' -- Revenue earned from PV total (all time) in 'unit' currency
            'unit' -- Unit of currency for 'Revenue'

        """
        response = self.session.post(self.get_url('newMixApi.do'), params={
            'op': 'getEnergyOverview',
            'mixId': mix_id,
            'plantId': plant_id
        })

        return self.process_response(response).get('obj')

    def mix_system_status(self, mix_id, plant_id):
        """
        Returns current "Status" from Mix device

        :param mix_id: The serial number (device_sn) of the inverter
        :param plant_id: The ID of the plant
        :return:

            'SOC' -- Statement of charge (remaining battery %)
            'chargePower' -- Battery charging rate in kw
            'fAc' -- Frequency (Hz)
            'lost' -- System status e.g. 'mix.status.normal'
            'pLocalLoad' -- Load conumption in kW
            'pPv1' -- PV1 Wattage in W
            'pPv2' -- PV2 Wattage in W
            'pactogrid' -- Export to grid rate in kW
            'pactouser' -- Import from grid rate in kW
            'pdisCharge1' -- Discharging batteries rate in kW
            'pmax' -- ??? 6 ??? PV Maximum kW ??
            'ppv' -- PV combined Wattage in kW
            'priorityChoose' -- Priority setting - 0=Local load
            'status' -- System statue - ENUM - Unknown values
            'unit' -- Unit of measurement e.g. 'kW'
            'upsFac' -- ??? 0
            'upsVac1' -- ??? 0
            'uwSysWorkMode' -- ??? 6
            'vAc1' -- Grid voltage in V
            'vBat' -- Battery voltage in V
            'vPv1' -- PV1 voltage in V
            'vPv2' -- PV2 voltage in V
            'vac1' -- Grid voltage in V (same as vAc1)
            'wBatteryType' -- ??? 1

        """
        response = self.session.post(self.get_url('newMixApi.do'), params={
            'op': 'getSystemStatus_KW',
            'mixId': mix_id,
            'plantId': plant_id
        })

        return self.process_response(response).get('obj')

    def mix_detail(self, mix_id, plant_id, timespan=Timespan.hour, date=None):
        """ Get Mix details for specified timespan

        'chartData': {   '00:05': {   'pacToGrid' -- Export rate to grid in kW
                                          'pacToUser' -- Import rate from grid in kW
                                          'pdischarge' -- Battery discharge in kW
                                          'ppv' -- Solar generation in kW
                                          'sysOut' -- Load consumption in kW
                                      },
                             '00:10': {   'pacToGrid': '0',
                                          'pacToUser': '0.93',
                                          'pdischarge': '0',
                                          'ppv': '0',
                                          'sysOut': '0.93'},
                              ......
                         }
            'eAcCharge' -- Exported to grid in kWh
            'eCharge' -- System production in kWh = Self-consumption + Exported to Grid
            'eChargeToday' -- Load consumption from solar in kWh
            'eChargeToday1' -- Self-consumption in kWh
            'eChargeToday2' -- Self-consumption in kWh (eChargeToday + echarge1)
            'echarge1' -- Load consumption from battery in kWh
            'echargeToat' -- Total battery discharged (all time) in kWh
            'elocalLoad' -- Load consumption in kW (battery + solar + imported)
            'etouser' -- Load consumption imported from grid in kWh
            'photovoltaic' -- Load consumption from solar in kWh (same as eChargeToday)
            'ratio1' -- % of system production that is self-consumed
            'ratio2' -- % of system production that is exported
            'ratio3' -- % of Load consumption that is "self consumption"
            'ratio4' -- % of Load consumption that is "imported from grid"
            'ratio5' -- % of Self consumption that is directly from Solar
            'ratio6' -- % of Self consumption that is from batteries
            'unit' -- Unit of measurement e.g kWh
            'unit2' -- Unit of measurement e.g kW

            NOTE - It is possible to calculate the PV generation that went into charging the batteries by performing the
            following calculation:
            Solar to Battery = Solar Generation - Export to Grid - Load consumption from solar
                               epvToday (from mix_info) - eAcCharge - eChargeToday

        :param mix_id: The serial number (device_sn) of the inverter
        :param plant_id: The ID of the plant
        :param timespan: The ENUM value conforming to the time window you want e.g. hours from today, days,
        or months (Default Timespan.hour)
        :param date: The date you are interested in (Default datetime.datetime.now())
        :return: A chartData object where each entry is for a specific 5 minute window
                e.g. 00:05 and 00:10 respectively (below)
        """

        date_str = tiemspan.format_date(date)

        response = self.session.post(self.get_url('newMixApi.do'), params={
            'op': 'getEnergyProdAndCons_KW',
            'plantId': plant_id,
            'mixId': mix_id,
            'type': timespan.value,
            'date': date_str
        })

        return self.process_response(response).get('obj')


