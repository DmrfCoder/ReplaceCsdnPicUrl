from CsdnUtil import *
from ReplaceLinkInItemFile import *


def main(session, logInJsonObject):
    if session is not None:
        articleIdList = getArticleIdList(logInJsonObject['username'])
        articleCount = len(articleIdList)
        index = 1
        for articleId in articleIdList:
            try:
                articleObject = getArticle(articleId, session)
                jsonObject = handleArticle(articleObject)
                saveArticle(jsonObject, session)
                print('完成--' + str(index) + '/' + str(articleCount) + '--:' + articleId)
                index += 1
                print()
            except BaseException as e:
                print('--------Exception:' + articleId + str(e))


def doSingle(session, logInJsonObject, articleId):
    articleObject = getArticle(articleId, session)
    jsonObject = handleArticle(articleObject)
    f = open('content.html', 'w', encoding='utf-8')
    f.write(jsonObject['content'])
    f.close()
    print('完成：' + articleId)


if __name__ == '__main__':
    userId = 'username'
    password = 'password'
    session, logInObject = doLogin(userId, password)
    main(session, logInObject)
