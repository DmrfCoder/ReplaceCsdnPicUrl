import re

from UploadTargetPicToAliOss import putUrlPicToAliOss


def readFile(path):
    with open(path, encoding='utf-8') as f:
        lines = f.readlines()
    data = ''
    for line in lines:
        data = data + line
    return data


def lambdaToGetMarkdownPicturePosition(content):
    """
    从markdownd代码中提取图片链接
    :param content:
    :return:
    """
    pattern = re.compile(r"!\[.*?\]\(http.*?\)")
    resultList = pattern.finditer(content)
    urlList = []
    for item in resultList:
        curStr = item.group()
        curStr = curStr.split('(')[1]
        curStr = curStr.strip(')')
        urlList.append(curStr)
        print(curStr)

    return urlList


'''
<img alt="" class="has" src="https://ws4.sinaimg.cn/large/006tNc79gy1g315jycls2j324u0u0aly.jpg" />
'''


def lambdaToGetHtmlPicturePosition(content):
    """
    从html代码中提取图片链接
    :param content:
    :return:
    """
    pattern = re.compile(r"<img.*?>")

    resultList = pattern.finditer(content)

    urlList = []

    for item in resultList:
        searchObject = re.search(r'src=".*?"', item.group())
        curStr = searchObject.group()
        curStr = curStr.split('"')[1]
        curStr = curStr.strip('"')
        urlList.append(curStr)

    return urlList


def getPicNameFromPicUrl(url):
    s = url.split('/')[-1]
    return s


def handleArticle(articleObject):
    content = articleObject['content']
    markdowncontent = articleObject['markdowncontent']

    oldAndNewDict = {}
    if markdowncontent is not None:
        mdUrlList = lambdaToGetHtmlPicturePosition(markdowncontent)
        for mdUrl in mdUrlList:
            if mdUrl not in oldAndNewDict.keys():
                resultUrl = putUrlPicToAliOss(mdUrl, getPicNameFromPicUrl(mdUrl))
                if resultUrl is not None:
                    markdowncontent = markdowncontent.replace(mdUrl, resultUrl)
                    oldAndNewDict[mdUrl] = resultUrl
            else:
                markdowncontent = markdowncontent.replace(mdUrl, oldAndNewDict.get(mdUrl))

    if content is not None:
        htmlUrlList = lambdaToGetHtmlPicturePosition(content)
        for htmlUrl in htmlUrlList:
            if htmlUrl not in oldAndNewDict.keys():
                resultUrl = putUrlPicToAliOss(htmlUrl, getPicNameFromPicUrl(htmlUrl))
                if resultUrl is not None:
                    content = content.replace(htmlUrl, resultUrl)
                    oldAndNewDict[htmlUrl] = resultUrl
            else:
                content = content.replace(htmlUrl, oldAndNewDict.get(htmlUrl))

    articleObject['content'] = content
    articleObject['markdowncontent'] = markdowncontent

    return articleObject
