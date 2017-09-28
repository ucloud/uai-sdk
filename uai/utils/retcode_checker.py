from common_handler import common
from uai.utils.logger import uai_logger
from urllib import quote

# Condition code
NORMAL_CONDITION = 0
RETRY_CONDITION = -1
FATAL_CONDITION = -2


def encode_params(params):
    for k in params.keys():
        params[k] = quote(params[k])
    return params

def get_request(url, params):
    request = url + "/?"
    for k in params.keys():
        request = request + k + "=" + str(params[k]) + "&"
    return request[0:len(request) -1]

def get_response(rsp, num):
    response = ""
    tag = ""
    for i in range(0,num) :
        tag += "\t"

    if type(rsp) is dict:
        response += "\n{0}{{\n".format(tag)
        for k in rsp.keys():
            response += "{0}{1} : {2},\n".format(tag,k,get_response(rsp[k], num+1))
        if response.endswith(",\n"):
            return "{0}\n{1}}}".format(response[0:len(response) -2], tag)
        else:
            return  "{0}\n{1}}}".format(response, tag)
    if type(rsp) is list:
        response += "\n{0}[\n".format(tag)
        for v in rsp:
            response += "{0}{1},\n".format(tag, get_response(v, num + 1))
        if response.endswith(",\n"):
            return "{0}\n{1}]".format(response[0:len(response) - 2], tag)
        else:
            return "{0}\n{1}]".format(response, tag)
    if type(rsp) is int or type(rsp) is float:
        return "{0}".format(rsp)
    if not rsp:
        return ""
    else:
        return "{0}".format(rsp.encode('utf-8'))



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
        except Exception as e:
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
