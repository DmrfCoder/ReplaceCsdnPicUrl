# 使用Python批量替换csdn文章的图片链接

### 前言

笔者之前的写作习惯一直是在本地(Mac+Typora+Ipac)写好之后将markdown代码粘贴到csdn，图片是Ipac自动上传到微博匿名图床上，用了大概一年多都没有问题，直到前段时间突然发现我csdn文章里面的图片无法加载了，就像下面这样：

![image-20190518194534831](http://picture-pool.oss-cn-beijing.aliyuncs.com/2019-05-18-114535.png)

本来以为是微博图床挂了，结果发现图片的链接还是可以正常访问的，本地Typora上也是可以正常显示图片的，问了一下csdn的工作人员，说是微博图床加了防盗链，所以现在csdn不能自动加载了，真是又气又无奈，没办法，谁让自己当初贪图小便宜用了免费图床了，既然问题已经出了就要想办法解决，首先是订阅了Ipac，这样可以支持自定义图床（默认的Ipac只能支持微博匿名图床），笔者选择的是阿里云Oss，有免费额度，个人图床够用。但是这样只能保证我之后写的文章不会因为图床的导致图片挂掉，那之前的怎么办….如果可以将之前文章里面的图片从图床上下载下来，然后传到我新的图床上，然后再将原文的图片链接由原来的图床链接替换为现在新的图片链接就可以完美解决了啊，但是由于文章太多，一篇一篇手动操作实在是太慢，既然是程序员，就应该用代码解决，所以有了本文，本文的主要思路如下图所示：

![image-20190518200410579](http://picture-pool.oss-cn-beijing.aliyuncs.com/2019-05-18-120411.png)

### 模拟登陆csdn

我们首先打开csdn的登陆页面，这里我们选择账号密码登陆，方便提取信息：

![image-20190518200820418](http://picture-pool.oss-cn-beijing.aliyuncs.com/2019-05-18-120820.png)

我们随便个账号和密码，看看点击登陆之后该站点会做什么：

![屏幕快照 2019-05-18 20.10.26](http://picture-pool.oss-cn-beijing.aliyuncs.com/2019-05-18-121250.png)

我们发现，这里执行了一个`doLogin`，见名知意，这个应该就是真正的登陆的请求，我们点开看看详情：

![屏幕快照 2019-05-18 20.14.33](http://picture-pool.oss-cn-beijing.aliyuncs.com/2019-05-18-121640.png)

重点在于我用红圈圈出来的那里，将我们输入的用户名和密码传进去，然后发起登陆请求，所以，我们只需要模拟这个`doLogin`就可以了，代码如下：

```python

def doLogin(userId, password):
      """
    模拟登陆，获取cookie以及username
    :param userId: 
    :param password: 
    :return: 
    """

    url = "https://passport.csdn.net/v1/register/pc/login/doLogin"

    payload = "{\"loginType\":\"1\",\"pwdOrVerifyCode\":\"" + password + "\",\"userIdentification\":\"" + userId + "\",..."

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

```

这样就完成了模拟登陆，注意这里返回的是一个`session`和 `jsonObject`，`session`是requests中的概念，返回`session`就一个目的，利用登陆成功后的`cookie`，这样才能在后面修改你的文章, `jsonObject`是登陆成功后`csdn`服务端给我们返回的信息，这里将其`jsonObject`返回的目的是获取当前`userId`对应的`username`(`userId`指的是你在`csdn`利用账号密码登录时输入的那个用户名，一般是邮箱或者手机号码，`username`是`csdn`给你分配的一个标识)。

### 爬取个人所有文章的id

这里爬取所有文章id相当于获取了当前作者的所有文章列表，我们先看看指定作者的文章列表页：

![image-20190518202629873](http://picture-pool.oss-cn-beijing.aliyuncs.com/2019-05-18-122630.png)

可以看到url是：`https://blog.csdn.net/username/article/list/index`，username就是刚才我们登录时返回的那个，`index`是页面的序号，因为大家基本都是很多页文章，所以`index`从0往上增加，我们看看这个页面的`html`代码：

![屏幕快照 2019-05-18 20.28.26](http://picture-pool.oss-cn-beijing.aliyuncs.com/2019-05-18-122907.png)

可以很容易地发现文章列表的位置，分析了一下发现每一篇文章都有一个`data-articleid`，这就是我们需要的文章id啊，所以思路就是模拟请求`https://blog.csdn.net/username/article/list/index`，拿到返回的html后使用正则表达式匹配`data-articleid`即可，注意这里有个细节就是，在我画红括弧的紧邻上一个`< div >`标签，有一个`style="display：none；"`的元素，这个不是我们需要的，但是他也有`data-articleid`属性，所以我们在使用正则表达式匹配到当前`html`页面的所有`data-articleid`属性后应该忽略第一条，代码如下：

```python

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

```

### 爬取文章

获取到文章的id列表之后我们就可以爬取文章了，我们爬取文章的目的是获取到当前文章的markdown或者是html源代码，然后在本地做图片链接的替换，那么我们肯定要去文章的编辑页面找规律，而不是在文章的详情页面，因为详情页面大概率只会返回html，不会返回markdown源代码，我们随便找一篇文章，点击"编辑"，进入编辑页面：

![image-20190518203841079](http://picture-pool.oss-cn-beijing.aliyuncs.com/2019-05-18-123841.png)

我们刷新一下页面：

![屏幕快照 2019-05-18 20.39.02](http://picture-pool.oss-cn-beijing.aliyuncs.com/2019-05-18-123925.png)

可以看到有个很显眼的getAriticle，我们看看其response：

![image-20190518204019867](http://picture-pool.oss-cn-beijing.aliyuncs.com/2019-05-18-124020.png)

可以发现这个getAriticle返回了当前文章的html代码、markdown代码等文章信息，需要的参数就是文章id，所以我们只需要模拟这个getAriticle请求即可，代码如下：

```python

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
```

### 正则表达式匹配图片链接

获取到文章的`html`和`markdown`代码之后要做的就是使用正则表达式匹配图片链接了，由于笔者对正则表达式不是很熟悉，所以只能很笨拙地使用，欢迎大家提出改进，这里直接给出代码：

```python

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
```

### 将图片上传至新图床

这个就根据每个人选择的图床不一样做法也不一样，但是思路是一样的，我使用的是阿里oss服务，使用其提供的sdk可以很方便地将图片从原来的链接迁移到现有的图床：

```python

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

```



### 使用新图片链接替换原来的图片链接

这部分直接使用python中str的replace即可，核心代码很简单：

```python
markdowncontent = markdowncontent.replace(mdUrl, resultUrl)
content = content.replace(htmlUrl, resultUrl)
```

### 保存文章

替换好图片链接后最重要的一步就是将修改后的链接保存到csdn的服务器，这里还是从csdn的文章编辑界面找信息：

![屏幕快照 2019-05-18 20.47.50](http://picture-pool.oss-cn-beijing.aliyuncs.com/2019-05-18-124809.png)

发现当我们点击发表文章之后有一个saveArticle，分析其请求体之后可以肯定这个saveArticle就是用来保存文章的，由于请求体内容过多，这里就不贴原图了，大家可以在自己的chrome上看一下，我们只需要模拟这个saveArticle即可，代码如下：

```python

def saveArticle(jsonObject, session):
    """
    保存文章到csdn的服务器
    :param jsonObject: 
    :param session: 
    """
    boundary = '------WebKitFormBoundary7MA4YWxkTrZu0gW'
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
              "{boundary}\r\nContent-Disposition: form-data; name=\"markdowncontent\"\r\n\r\n " \
              "{markdowncontent}\r\n" \
              "{boundary}\r\nContent-Disposition: form-data; name=\"content\"\r\n\r\n" \
              "{content}\r\n" \
              "{boundary}\r\nContent-Disposition: form-data; name=\"id\"\r\n\r\n " \
              "{id}\r\n" \
              "{boundary}\r\nContent-Disposition: form-data; name=\"private\"\r\n\r\n" \
              "\r\n" \
              "{boundary}\r\nContent-Disposition: form-data; name=\"read_need_vip\"\r\n\r\n " \
              "{read_need_vip}\r\n" \
              "{boundary}\r\nContent-Disposition: form-data; name=\"tags\"\r\n\r\n " \
              "{tags}\r\n" \
              "{boundary}\r\nContent-Disposition: form-data; name=\"status\"\r\n\r\n " \
              "{status}\r\n" \
              "{boundary}\r\nContent-Disposition: form-data; name=\"categories\"\r\n\r\n " \
              "{categories}\r\n" \
              "{boundary}\r\nContent-Disposition: form-data; name=\"channel\"\r\n\r\n " \
              "{channel}\r\n" \
              "{boundary}\r\nContent-Disposition: form-data; name=\"type\"\r\n\r\n" \
              "{type}\r\n" \
              "{boundary}\r\nContent-Disposition: form-data; name=\"articleedittype\"\r\n\r\n " \
              "{articleedittype}\r\n" \
              "{boundary}\r\nContent-Disposition: form-data; name=\"Description\"\r\n\r\n " \
              "{description}\r\n" \
              "{boundary}\r\nContent-Disposition: form-data; " \
              "name=\"csrf_token\"\r\n\r\n\r\n{boundary}-- ".format(boundary=boundary, title=title, id=id,markdowncontent=markdowncontent,content=content, private=private,tags=tags, status=status, categories=categories,channel=channel, read_need_vip=read_need_vip,articleedittype=articleedittype,description=description, type=type)

    headers = {
        'accept': "*/*",
        'accept-encoding': "gzip, deflate, br",
        'accept-language': "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
        'origin': "https://mp.csdn.net",
        'referer': "https://mp.csdn.net/mdeditor/90292004",
        'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36",
        'Cache-Control': "no-cache",
        'Postman-Token': "76c8f028-258f-462e-9cd4-00294e3e620d,d3e13008-b401-4d1d-ac5e-d8cb1b13901f",
        'Host': "mp.csdn.net",
        'Connection': "keep-alive",
        'cache-control': "no-cache"
    }

    response = session.request("POST", url, data=payload.encode('utf-8'), headers=headers)
    jsonObject = json.loads(bytes.decode(response.content))
    if jsonObject['status'] == True:
        print('保存' + id + '内容成功')
    else:
        print('保存' + id + '内容失败' + response.content)
```

主要做法就是将getArticle返回的内容只改变markdowncontent和content属性，然后进行保存操作。

### 代码

完整代码：[github](https://github.com/DmrfCoder/ReplaceCsdnPictureUrl)，如点击超链接无法访问，请在浏览器地址栏输入`https://github.com/DmrfCoder/ReplaceCsdnPictureUrl`后访问。

### 需要优化的地方

- 将单线程改为多线程执行
- 优化正则表达式部分

