#!/usr/bin/env python3
#
# Copyright 2019-present Facebook. All Rights Reserved.
#
# This program file is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program in a file named COPYING; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA
#

import json
import re
import subprocess
import syslog

import rest_libsensormon
from rest_utils import DEFAULT_TIMEOUT_SEC


#
# "SENSORS" REST API handler for Wedge400
#
# Wedge400 sensor REST API handler is unique in that,
# it uses rest-api-1, but still uses sensor-util, instead of sensor.
# We are forced to use sensor-util, as Wedge400 has too many resources
# for BMC to control. If we use conventional way of fetching sensor data
# (sensors command), it will take too long. So we use sensor-util, which
# will use the cached value. But the output format of sensor-util is quite
# different from sensors command. So we need a separate REST api handler
# for this.
#
def get_fru_sensor(fru_name: str):
    c_fru_id = rest_libsensormon.pal_get_fru_id(fru_name)
    is_fru_prsnt = rest_libsensormon.pal_is_fru_prsnt(c_fru_id)
    ret = {"Adapter": fru_name, "name": fru_name, "present": is_fru_prsnt}

    if is_fru_prsnt:

        for snr_num in rest_libsensormon.pal_get_fru_sensor_list(c_fru_id):
            sensor_name = rest_libsensormon.pal_get_sensor_name(c_fru_id.value, snr_num)
            try:
                fvalue = rest_libsensormon.sensor_read(c_fru_id, snr_num)

                # Stringify value to simulate sensor-util output
                ret[sensor_name] = "{:.2f}".format(fvalue)

            except rest_libsensormon.RestSensorReadError:
                ret[sensor_name] = "NA"

    return ret


def get_scm_sensors():
    return {"Information": get_fru_sensor("scm"), "Actions": [], "Resources": []}


def get_smb_sensors():
    return {"Information": get_fru_sensor("smb"), "Actions": [], "Resources": []}


def get_pem1_sensors():
    return {"Information": get_fru_sensor("pem1"), "Actions": [], "Resources": []}


def get_pem2_sensors():
    return {"Information": get_fru_sensor("pem2"), "Actions": [], "Resources": []}


def get_psu1_sensors():
    return {"Information": get_fru_sensor("psu1"), "Actions": [], "Resources": []}


def get_psu2_sensors():
    return {"Information": get_fru_sensor("psu2"), "Actions": [], "Resources": []}


def get_all_sensors():
    result = []
    # FRUs of /usr/local/bin/sensor-util commands
    frus = ["scm", "smb", "psu1", "psu2", "pem1", "pem2"]

    for fru in frus:
        sresult = get_fru_sensor(fru)
        result.append(sresult)

    fresult = {"Information": result, "Actions": [], "Resources": frus}
    return fresult


def get_sensors():
    return get_all_sensors()
