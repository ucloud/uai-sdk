# Copyright 2017 The UAI-SDK Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

# COMMON ERROR CODE
RETCODE_UNEXIST = -1
VERIFY_FAIL = 100
TIME_OUT = 110
DATA_FAIL = 120
SERVICE_ERROR = 130
USER_PERMISSION = 140
SERVICE_UNAVAIABLE = 150
MISSING_ACTION = 160
MISSING_SIGNATURE = 170
SIGNATURE_VERIFY_ERROR = 171
MISSING_API_VESION = 180
API_VERSION_ERROR = 190
GET_NAMES_ERROR = 200
PARAMS_VALUE_ERROR = 210
MISSING_PARAM = 220
PARAMS_UNAVAILABLE = 230
PERMISSION_ERROR = 240
DEDUCTION_ERROR = 260 
SETTLEMENT_ERROR = 270
PARAMS_SET_ERROR = 300
LACK_BALANCE = 520
SERVICE_UNOPEN = 999

def common_log(ret_message):
    log_info = '[COMMON ERROR]: ' + ret_message
    raise Exception(log_info)

def retcode_unexist_handle(ret_message):
    common_log(ret_message)
    #return -1

def verify_fail_handle(ret_message):
    common_log(ret_message)
    #return -1

def timeout_handle(ret_message):
    log_info = common_log(ret_message)
    #return 1

def data_fail_handle(ret_message):
    common_log(ret_message)
    #return -1

def service_error_handle(ret_message):
    common_log(ret_message)
    #return -1

def user_permission_handle(ret_message):
    common_log(ret_message)
    #return -1

def service_unavaiable_handle(ret_message):
    common_log(ret_message)
    #return -1

def missing_action_handle(ret_message):
    common_log(ret_message)
    #return -1

def missing_signature_handle(ret_message):
    common_log(ret_message)
    #return -1

def signature_verify_error_handle(ret_message):
    common_log(ret_message)
    #return -1

def missing_api_version_handle(ret_message):
    common_log(ret_message)
    #return -1

def api_version_error_handle(ret_message):
    common_log(ret_message)
    #return -1

def get_names_error_handle(ret_message):
    common_log(ret_message)
    #return -1

def params_value_error_handle(ret_message):
    common_log(ret_message)
    #return -1

def missing_params_handle(ret_message):
    common_log(ret_message)
    #return -1

def params_unavailable_handle(ret_message):
    common_log(ret_message)
    #return -1

def permission_error_handle(ret_message):
    common_log(ret_message)
    #return -1

def deduction_error_handle(ret_message):
    common_log(ret_message)
    #return -1

def settlement_error_handle(ret_message):
    common_log(ret_message)
    #return -1

def params_set_error_handle(ret_message):
    common_log(ret_message)
    #return -1

def lack_balance_handle(ret_message):
    common_log(ret_message)
    #return -1

def service_unopen_handle(ret_message):
    common_log(ret_message)
    #return -1

common = {}
common[RETCODE_UNEXIST] = retcode_unexist_handle
common[VERIFY_FAIL] = verify_fail_handle
common[TIME_OUT] = timeout_handle
common[DATA_FAIL] = data_fail_handle
common[SERVICE_ERROR] = service_error_handle
common[USER_PERMISSION] = user_permission_handle
common[SERVICE_UNAVAIABLE] = service_unavaiable_handle
common[MISSING_ACTION] = missing_action_handle
common[MISSING_SIGNATURE] = missing_signature_handle
common[SIGNATURE_VERIFY_ERROR] = signature_verify_error_handle
common[MISSING_API_VESION] = missing_api_version_handle
common[API_VERSION_ERROR] = api_version_error_handle
common[GET_NAMES_ERROR] = get_names_error_handle
common[PARAMS_VALUE_ERROR] = params_value_error_handle
common[MISSING_PARAM] = missing_params_handle
common[PARAMS_UNAVAILABLE] = params_unavailable_handle
common[PERMISSION_ERROR] = permission_error_handle
common[DEDUCTION_ERROR] = deduction_error_handle
common[SETTLEMENT_ERROR] = settlement_error_handle
common[PARAMS_SET_ERROR] = params_set_error_handle
common[LACK_BALANCE] = lack_balance_handle
common[SERVICE_UNOPEN] = service_unopen_handle
