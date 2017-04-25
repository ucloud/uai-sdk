#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from common_handler import common
from uai.utils.logger import uai_logger

# Condition code
NORMAL_CONDITION = 0
RETRY_CONDITION = -1
FATAL_CONDITION = -2

def get_info(ret_info):
    ret_code = ret_info['RetCode']
    ret_message = ret_info['Message']
    return ret_code, ret_message

def check_retcode(ret_info):
    ret_code, ret_message = get_info(ret_info)

    if ret_code == 0:
        return NORMAL_CONDITION
    elif ret_code in range(-1, 2000):
        uai_logger.warning("Something wrong with API Gateway.")
        try:
            common[ret_code](ret_message)
        except KeyError:
            uai_logger.error("The RetCode is not included in COMMON RetCode.")
        except Exception, e:
            uai_logger.exception(e)
            if "Time Out" in str(e):
                return RETRY_CONDITION
            else:
                return FATAL_CONDITION
        
    else:
        uai_logger.error("Unknown Error Region.")
        return FATAL_CONDITION

def assert_check(ret_info):
    ret_code, ret_message = get_info(ret_info)
    if ret_code == 0:
        uai_logger.debug("Pass API RetCode Check")
    else:
        common[ret_code](ret_message)
