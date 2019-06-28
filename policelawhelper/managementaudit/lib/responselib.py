#!/user/bin/env python
# -*- coding: utf-8 -*-
#@Time      : 2017/12/1/001 8:57
#@Author    : jiaojianglong

from . import exceptionlib
import traceback
from django.http import JsonResponse
class ResponseData():
    result = {'code': 0, 'msg': '返回成功', 'data': {}}

    #返回数据
    @classmethod
    def data(cls,data):
        cls.result['code'] = 0
        cls.result['data']=data
        cls.result['msg'] =  '返回成功'
        return cls.result

    #返回错误提示
    @classmethod
    def errormsg(cls,msg):
        cls.result['code'] = 1
        cls.result['msg'] = str(msg)
        cls.result['data'] = {}
        return cls.result

    #返回成功提示
    @classmethod
    def successmsg(cls,msg):
        cls.result['code'] = 0
        cls.result['msg'] = str(msg)
        cls.result['data'] = {}
        return cls.result


def init_response_data():
    result = {'code': 0, 'msg': '返回成功', 'data': {}}
    return result


# 重置返回参数
def reset_response_data(info, code=1):
    result = {'code': code, 'msg': str(info), 'data': {}}
    return result

def exception_handler(func):
    def handler(self,*args,**kwargs):
        try:
            c = func(self,*args,**kwargs)
        except exceptionlib.CustomException as msg:
            code = msg.err[0]
            info = msg.err[1]
            result = reset_response_data(info, code)
            return JsonResponse(result)
        except:
            info = traceback.format_exc()
            result = reset_response_data(info)
            return JsonResponse(result)
        return c
    return handler

if __name__ == '__main__':
    print(ResponseData.data('haha'))
