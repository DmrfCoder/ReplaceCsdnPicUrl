import json

import requests
import re


def getArticleIdList(userId, maxListPage=100):
    """
    获取指定userId用户的所有文章的iD
    :param userId:
    :param maxListPage:
    :return:
    """
    articleList = []
    count = 0
    for index in range(maxListPage):
        url = 'https://blog.csdn.net/' + userId + '/article/list/' + str(index)
        requestParm = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) ...", "Accept-Language": "en-US,en;q=0.5"}
        response = requests.get(url, params=requestParm)

        if response.status_code == 200:
            pattern = re.compile(r"data-articleid=\".*?\"")
            resultList = pattern.finditer(bytes.decode(response.content))
            flag = 0
            for result in resultList:
                if flag == 0:
                    flag = flag + 1
                    continue
                print('正在获取第{count}条文章Id'.format(count=count))
                flag = flag + 1
                count = count + 1
                item = re.search("\".*?\"", result.group())
                articleList.append(item.group().strip('\"'))
            if flag == 0:
                break
        else:
            break

    print('共获取到{count}条文章id'.format(count=len(articleList)))
    return articleList


def getArticle(articleId, session):
    """
    获取文章源码
    :param articleId:
    :param session:
    :return:
    """
    url = 'https://mp.csdn.net/mdeditor/getArticle?id=' + articleId
    requestParams = {
        'id': articleId
    }

    headers = {'accept-encoding': 'gzip, deflate, br',
               'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
               'referer': 'https://mp.csdn.net/mdeditor/90272525',
               'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'
               }

    result = session.get(url, params=requestParams, headers=headers)
    jsonObject = json.loads(bytes.decode(result.content))
    if jsonObject['status'] == True:
        print('获取' + articleId + '内容成功')
        return jsonObject['data']
    else:
        print('获取' + articleId + '内容失败：' + jsonObject['error'])
        return None


def saveArticle(jsonObject, session):
    """
    保存文章到csdn的服务器
    :param jsonObject:
    :param session:
    """
    baseBodunary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    boundary = '--' + baseBodunary
    id = jsonObject['id']
    title = jsonObject['title'].strip()
    articleedittype = jsonObject['articleedittype']
    description = jsonObject['description']
    content = jsonObject['content']
    markdowncontent = jsonObject['markdowncontent']
    if markdowncontent is not None:
        markdowncontent.strip()

    # private = jsonObject['private']
    private = '1'
    tags = jsonObject['tags']
    categories = jsonObject['categories'].replace(' ', '')
    channel = jsonObject['channel']
    type = jsonObject['type']
    # type='original'
    status = jsonObject['status']
    read_need_vip = jsonObject['read_need_vip']

    url = "https://mp.csdn.net/mdeditor/saveArticle"

    payload = "{boundary}\r\nContent-Disposition: form-data; name=\"title\"\r\n\r\n" \
              "{title}\r\n" \
              "{boundary}\r\nContent-Disposition: form-data; name=\"markdowncontent\"\r\n\r\n" \
              "{markdowncontent}\r\n" \
              "{boundary}\r\nContent-Disposition: form-data; name=\"content\"\r\n\r\n" \
              "{content}\r\n" \
              "{boundary}\r\nContent-Disposition: form-data; name=\"id\"\r\n\r\n" \
              "{id}\r\n" \
              "{boundary}\r\nContent-Disposition: form-data; name=\"private\"\r\n\r\n" \
              "\r\n" \
              "{boundary}\r\nContent-Disposition: form-data; name=\"read_need_vip\"\r\n\r\n" \
              "{read_need_vip}\r\n" \
              "{boundary}\r\nContent-Disposition: form-data; name=\"tags\"\r\n\r\n" \
              "{tags}\r\n" \
              "{boundary}\r\nContent-Disposition: form-data; name=\"status\"\r\n\r\n" \
              "{status}\r\n" \
              "{boundary}\r\nContent-Disposition: form-data; name=\"categories\"\r\n\r\n" \
              "{categories}\r\n" \
              "{boundary}\r\nContent-Disposition: form-data; name=\"channel\"\r\n\r\n" \
              "{channel}\r\n" \
              "{boundary}\r\nContent-Disposition: form-data; name=\"type\"\r\n\r\n" \
              "{type}\r\n" \
              "{boundary}\r\nContent-Disposition: form-data; name=\"articleedittype\"\r\n\r\n" \
              "{articleedittype}\r\n" \
              "{boundary}\r\nContent-Disposition: form-data; name=\"Description\"\r\n\r\n" \
              "{description}\r\n" \
              "{boundary}\r\nContent-Disposition: form-data; " \
              "name=\"csrf_token\"\r\n\r\n\r\n{boundary}-- ".format(boundary=boundary, title=title, id=id,
                                                                    markdowncontent=markdowncontent,
                                                                    content=content, private=private,
                                                                    tags=tags, status=status, categories=categories,
                                                                    channel=channel, read_need_vip=read_need_vip,
                                                                    articleedittype=articleedittype,
                                                                    description=description, type=type
                                                                    )

    headers = {
        'accept': "*/*",
        'accept-encoding': "gzip, deflate, br",
        'accept-language': "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        'content-type': "multipart/form-data; boundary={boundary}".format(boundary=baseBodunary),
        'origin': "https://mp.csdn.net",
        'referer': "https://mp.csdn.net/mdeditor/90292004",
        'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36",
    }

    response = session.request("POST", url, data=payload.encode('utf-8'), headers=headers)
    jsonObject = json.loads(bytes.decode(response.content))
    if jsonObject['status'] == True:
        print(jsonObject)
        print('保存' + id + '内容成功')
    else:
        print('保存' + id + '内容失败' + str(response.content))


def requestAriticle(session, articleId):
    url = "https://blog.csdn.net/qq_36982160/article/details/" + articleId

    headers = {
        'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        'Accept-Encoding': "gzip, deflate, br",
        'Accept-Language': "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        'Cache-Control': "max-age=0",
        'Connection': "keep-alive",
        'Host': "blog.csdn.net",
        'Referer': "https://blog.csdn.net/qq_36982160/article/list/4?",
        'Upgrade-Insecure-Requests': "1",
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
    }

    response = session.request("GET", url, headers=headers)

    return session


def doLogin(userId, password):
    """
    模拟登陆，获取cookie以及username
    :param userId:
    :param password:
    :return:
    """
    url = "https://passport.csdn.net/v1/register/pc/login/doLogin"

    payload = "{\"loginType\":\"1\",\"pwdOrVerifyCode\":\"" + password + "\",\"userIdentification\":\"" + userId + "\"," \
                                                                                                                   "\"fkid\":\"WC39ZUyXRgdEmBjvCFSctoY6vrVvsDfh15Z4BzLQiK1hZR3sL4FbnJri5bTVNP+q9j7ydk" \
                                                                                                                   "+4yyfbiV913nOtn5Nea4SElaSKblt3vtKq07lcxt9O15UJ+qkzA0CtbXuWTNaLm3yCn+LvYy5u242L" \
                                                                                                                   "+jCSorZ0dmOnLuYX5szM3JkLC5gbCcjwBtab28wt5K3kDhRPb6hlhgscke1HsJOdFJNtWVc3kNzPbCzo1sDYYIq1vuZMfmcZOtLS" \
                                                                                                                   "/1pqz9k2rorqPWdjc5uE=1487577677129\"," \
                                                                                                                   "\"uaToken\":\"117#9SEW6O9lFVzKrKohdO1OncycTEIjj2uP4" \
                                                                                                                   "+ZgBnFoEtuBZNFOmcjWOgl1dB44Fdb7ApgGOBFqB0zJZpMQRYI8AzHpMtvfB+wDApyGWa2zBBd2MbvFRErKAkOpmtdFB" \
                                                                                                                   "+VtApCpDij6BzjuZQKVCEfRKkx2dAPPBEfuCngpOBfx1zcuZQM9OdVRAkGGmt498" \
                                                                                                                   "+fDAQmGOBFCBSUQclrisEVRAvENqJCVSaVpbbciF7526buiICVOBxS8iXtCI" \
                                                                                                                   "+SvEpSi0C3Y8rwNmAhAVMsR8N9X0zInMdFLTMNi0RHgW2xPvGUFP+uhKNpxiPtnIYfpTKF9ie32W+5263PhVLuRoxQR0OWf7" \
                                                                                                                   "+2LTMNDiCmnBk886WPhILVRocQx00tnI+fUTMvh0CICBSM06WP" \
                                                                                                                   "/Iiydol32YQwkDgIJ0OUHuOaaOKl3Qb1vBlMBdFmVUJcaoWMzMk62htkAB172Sf8SRq6gMcLZ0IzQ22lfEXsCUt0T" \
                                                                                                                   "/4QoltnUBjLqtCx0tB6VR/hEtdmuwpXhNNuCdtq002eRN/Yqe4ps/FTXzPzevttqGTq153UD1XCeZpxt4h0oRBaaV1yIS4" \
                                                                                                                   "+WXjhGjjDUEmcWpBKN1hc2wEbAEppJ" \
                                                                                                                   "/9fgvA32cUGajfIFlwlqhggozBHnAxLFrlfB0B5FiJDqztBLGJ2CBjADSu9nnaLmEk6Jh3quIa4tm4mvxlWQvCKnU4BQc" \
                                                                                                                   "+E0DRbREu0SyTpU7ON2wlXXZAUOzquuJrlrKi8Dn1oql8um6b2yv6M0diNTuXL2ldtnPlJsrihZok+syTZMFsyIFdAdGky" \
                                                                                                                   "/3szAZlPMTKAGABdmAJzW6WhJwBkXR/WElMga8mdL/f+heRFsYTpplrrR5OKz3s" \
                                                                                                                   "/XsGJ9gyB7eTYbazdL6iyMewhUVOCtKbNMDSNoS2Mu4XaXl8eIjXnqwS5VDCg" \
                                                                                                                   "/gi8KMFDbj1wwLBlK1fw39vv8BGDHepd1XxRV5KtlbOVwu+BhpZKQMY1/QfnMnhdbVtVeCU6hnrrUPG6ZMclUiHRjLNgxFt" \
                                                                                                                   "/KhAcaveTa4rWs2/hP5LKA5hTO8Zn/D7kQsZIKeIATBFZEu6iqcgGOE1Yl6D2lypIGD1LlQmH" \
                                                                                                                   "+iglcb0UmwFCEVZ9V9XmddoVCmc7sz04HZxTcQ89f+dLxDnep1Zw6hiB95QUVUWGg6JT3VCdhNBLEJ3zKNEbAtsFMwyVHFB" \
                                                                                                                   "+L65wAstHxu3bpBkIQtuvBDw49nK8XIcKpkafWyORmNRIQFEA7XomuNVOgqQNi4/ZBoSbNGfq4w7CQKQOXXrt+yrv" \
                                                                                                                   "+SjqNJchgHW4PIH2kNiDPvEEuDz8XRAjU6RS9zrSglLs" \
                                                                                                                   "+kE1niU3yI3ISKcLZKStxs28CsY8yTYfOnJU3lCJkFeaKL0oDHDw4xzETc01D3yAbDZAS0ArAlctpDdL5YEF9YRFXCnw6nuk5d" \
                                                                                                                   "+DnYYfzYCA3fRYolx23EAocCmnvi5TcIa+gz3391v4FPMiZ0X/3i4avn8f2xJFIQWnALGJtjYDL5l+eWpajW" \
                                                                                                                   "+qsWw4M4cDthMgchOvRzZpuyHQujA7nbAd6OuC05yY7Sz9zHYJvAITik0thQQCKnr0KiwiIwc+B7QrK6I9L4vLd4g==\"," \
                                                                                                                   "\"webUmidToken\":\"T333DD7B4D1A7F316670169EA74E41777B42C801C83BE10C67A14CBC7C8\"} "

    headers = {
        'accept': "application/json, text/plain, */*",
        'accept-encoding': "gzip, deflate, br",
        'accept-language': "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        'content-type': "application/json;charset=UTF-8",
        'origin': "https://passport.csdn.net",
        'referer': "https://passport.csdn.net/login",
        'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36",
        'x-requested-with': "XMLHttpRequest",
        'Cache-Control': "no-cache",
        'Postman-Token': "407dbd4f-90ba-494c-994f-2de739d73a96,b506b3e0-b247-40af-b52b-2622c2148687",
        'Host': "passport.csdn.net",
        'Connection': "keep-alive",
        'cache-control': "no-cache"
    }

    session = requests.session()

    response = session.request("POST", url, data=payload.encode('utf-8'), headers=headers)
    jsonObject = json.loads(bytes.decode(response.content))
    if jsonObject['message'] == 'success':
        print('登录:{userId}成功'.format(userId=userId))
        return session, jsonObject
    else:
        print('登录:{userId}失败：'.format(userId=userId) + jsonObject['message'])
        return None
