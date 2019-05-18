# -*- coding: utf-8 -*-
import oss2
import requests

# 阿里云主账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM账号进行API访问或日常运维，请登录 https://ram.console.aliyun.com 创建RAM账号。
auth = oss2.Auth('xxx', 'xxx')
# Endpoint以杭州为例，其它Region请按实际情况填写。
bucket = oss2.Bucket(auth, 'http://oss-cn-beijing.aliyuncs.com', 'xxx')

baseUrl = 'https://xxx.oss-cn-beijing.aliyuncs.com/'

oosSession = None


def putUrlPicToAliOss(url, pictureName):
    """
    将图片迁移到阿里oss存储
    :param url:
    :param pictureName:
    :return:
    """
    if baseUrl in url:
        return None

    global oosSession
    if oosSession is None:
        oosSession = requests.session()

    # requests.get返回的是一个可迭代对象（Iterable），此时Python SDK会通过Chunked Encoding方式上传。
    input = oosSession.get(url)
    result = bucket.put_object(pictureName, input)
    resultUrl = baseUrl + pictureName
    if result.status == 200:
        return resultUrl
    else:
        return None
