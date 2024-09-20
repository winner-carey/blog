from django.shortcuts import render, HttpResponse, redirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
# Create your views here.
from PIL import Image, ImageDraw, ImageFont
import random
from io import BytesIO, StringIO
from django.http import JsonResponse
from mybbs import myforms
from mybbs import models
from django.db.models import Avg, Max, Min, Count
from django.db.models.functions import TruncMonth
from django.db.models import F
from bbs import settings
import os


# 随机颜色函数
def get_random_color():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


# 站点首页
# @login_required(login_url='/login/')
def index(request):
    article_list = models.Article.objects.all()
    return render(request, 'index.html', locals())


# 登录页面
def login(request):
    ret_msg = {'user': None, 'msg': None}
    if request.is_ajax():
        valid_code = request.session.get('valid_code')
        if request.POST.get('valid_code').upper() == valid_code.upper():
            user = request.POST.get('user')
            pwd = request.POST.get('pwd')
            user_obj = auth.authenticate(request, username=user, password=pwd)
            if user_obj:
                auth.login(request, user_obj)
                ret_msg['user'] = user
                ret_msg['msg'] = '登录成功'
            else:
                ret_msg['msg'] = '用户或密码错误'
        else:
            ret_msg['msg'] = '验证码错误'

        return JsonResponse(ret_msg)
    return render(request, 'login.html')


# 获取动态验证码
def get_code(request):
    # with open('static/img/xxx.png', 'rb') as f:
    #     data = f.read()

    img = Image.new('RGB', (300, 35), color=get_random_color())
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype('static/font/QingNiaoHuaGuangJianMeiHei-2.ttf', 30)

    # with open('code.png', 'wb') as f:
    #     img.save(f, 'png')
    # with open('code.png', 'rb') as f:
    #     data = f.read()

    valid_code = ''

    for i in range(5):
        random_num = str(random.randint(0, 9))
        random_upper = chr(random.randint(65, 90))
        random_lower = chr(random.randint(97, 122))
        random_chr = random.choice([random_num, random_upper, random_lower])
        draw.text((i * 30 + 60, 0), random_chr, get_random_color(), font=font)

        valid_code += random_chr

    print(valid_code)

    request.session['valid_code'] = valid_code
    f = BytesIO()
    img.save(f, 'png')
    data = f.getvalue()

    return HttpResponse(data)


# 退出登录
def logout(request):
    auth.logout(request)

    return redirect('/login/')


# 注册功能
def register(request):
    form_obj = myforms.RegisterForms()

    if request.is_ajax():
        back_msg = {'user': None, 'msg': None}
        name = request.POST.get('name')
        pwd = request.POST.get('pwd')
        re_pwd = request.POST.get('re_pwd')
        email = request.POST.get('email')
        file_obj = request.FILES.get('myfile')

        form_obj = myforms.RegisterForms({'name': name, 'pwd': pwd, 'email': email, 're_pwd': re_pwd})
        # form_obj = myforms.RegisterForms(request.POST)

        if form_obj.is_valid():
            if file_obj:
                models.UserInfo.objects.create_user(username=name, password=pwd, email=email, avator=file_obj)
            else:
                models.UserInfo.objects.create_user(username=name, password=pwd, email=email)

            back_msg['user'] = name
            back_msg['msg'] = '注册成功'
        else:
            back_msg['msg'] = form_obj.errors

        return JsonResponse(back_msg)
    return render(request, 'register.html', {'form_obj': form_obj})


# 个人首页
def home_site(request, username, **kwargs):
    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        return render(request, '404.html')

    # 子查询
    # article_list = user.article_set.all()

    # 连表查询
    article_list = models.Article.objects.filter(user=user)

    if kwargs:
        condition = kwargs.get('condition')
        param = kwargs.get('param')

        if condition == 'tag':
            article_list = models.Article.objects.filter(user=user).filter(tag__title=param)
        elif condition == 'category':
            article_list = models.Article.objects.filter(user=user).filter(category__title=param)

        elif condition == 'archive':
            year, month = param.split('-')
            article_list = models.Article.objects.filter(user=user).filter(create_date__year=year,
                                                                           create_date__month=month)
        else:
            return render(request, '404.html')

    '''
    blog = user.blog
    # 展示用户的标签以及每个标签对应的文章数
    tag_count = models.Tag.objects.filter(blog=blog).annotate(c=Count('article')).values_list('title', 'c')

    # 展示分类
    category_count = models.Category.objects.filter(blog=blog).annotate(c=Count('article')).values_list('title', 'c')

    # 展示随笔档案
    year_article_list = models.Article.objects.filter(user=user).annotate(y_m=TruncMonth('create_date')).values(
        'y_m').annotate(
        c=Count('nid')).values_list(
        'y_m', 'c')
    '''
    # 页面需要站点对象
    blog = user.blog
    return render(request, 'home_site.html', locals())


# 文章详情页
def articles_detail(request, username, article_id):
    user = models.UserInfo.objects.filter(username=username).first()

    # 页面需要站点对象
    blog = user.blog

    article_obj = models.Article.objects.filter(pk=article_id).first()

    comment_list = models.Comment.objects.filter(article_id=article_id)

    return render(request, 'articles_detail.html', locals())


import json


# 点赞点踩逻辑视图函数
def diggit(request):
    ret = {'code': None, 'back_msg': None}
    if request.is_ajax():
        if request.user.is_authenticated:
            user = request.user
            article_id = request.POST.get('article_id')
            # 前端传给后端都是字符串类型，这里要转换成bool类型，反序列化就行
            # 前端传过来的是 'true' 或者 'false'
            is_up = json.loads(request.POST.get('is_up'))
            print(is_up)

            # 是否点了赞或踩
            up_or_down = models.ArticleUpDown.objects.filter(user=user, article__nid=article_id).first()

            if not up_or_down:

                models.ArticleUpDown.objects.create(user=user, article_id=article_id, is_up=is_up)

                if is_up:
                    models.Article.objects.filter(pk=article_id).update(up_num=F('up_num') + 1)
                    ret['back_msg'] = '点赞成功'
                else:
                    models.Article.objects.filter(pk=article_id).update(down_num=F('down_num') + 1)
                    ret['back_msg'] = '点踩成功'
                ret['code'] = 1000

            else:
                ret['back_msg'] = '你已经点过了'
        else:
            ret['back_msg'] = '请先登录'
        return JsonResponse(ret)
    return render(request, '404.html')


# 评论视图函数
def comment(request):
    ret_msg = {'status': None}

    if request.is_ajax():

        if request.user.is_authenticated:
            user = request.user
            article_id = request.POST.get('article_id')
            content = request.POST.get('content')

            parent_id = request.POST.get('parent_id')
            # 没传就是None
            print(parent_id)

            comm_obj = models.Comment.objects.create(user=user, article_id=article_id, comm=content,
                                                     parent_comment_id=parent_id)

            ret_msg['status'] = True
            ret_msg['user_name'] = user.username
            ret_msg['comm'] = content
            ret_msg['cre_date'] = comm_obj.create_date.strftime('%Y-%m-%d')

            if parent_id:
                parent_obj = models.Comment.objects.filter(pk=parent_id).first()
                ret_msg['parent_username'] = parent_obj.user.username
                ret_msg['parent_content'] = parent_obj.comm

        else:
            ret_msg['status'] = False
    else:
        return render(request, '404.html')
    return JsonResponse(ret_msg)


# 后台管理页面
@login_required(login_url='/login/')
def backend(request):
    user = request.user
    article_list = models.Article.objects.filter(user=user)
    return render(request, 'backend/backend.html', locals())


from bs4 import BeautifulSoup


# 后台管理添加文章
@login_required(login_url='/login/')
def add_article(request):
    if request.method == 'POST':

        user = request.user
        title = request.POST.get('title')
        article = request.POST.get('article')
        print(article)

        # ss = '<p>aaa</p> <script>alert(123)</script>'
        # soup = BeautifulSoup(ss, 'html.parser')

        # 用BeautifulSoup模块处理xss攻击，内部将<script>标签删除了
        soup = BeautifulSoup(article, 'html.parser')
        # print(soup)

        # soup.find_all()的结果是一个列表 [<p>aaa</p>, <script>alert(123)</script>] ,里面是一个个的标签，
        # print(soup.find_all())

        ll = soup.find_all()
        for tag in ll:
            if tag.name == 'script':
                tag.decompose()

        # print(soup, type(soup))
        # print(str(soup))

        # soup.text 取出整个文本内容，标签都去除，只取内容
        # print(soup.text)

        desc = soup.text[0:50] + '...'

        models.Article.objects.create(user=user, title=title, content=str(soup), desc=desc)
        return redirect('/backend/')

    return render(request, 'backend/add_article.html')


# 后台管理上传文件
def add_img(request):
    if request.method == 'POST':
        my_file = request.FILES.get('imgFile')
        path = os.path.join(settings.MEDIA_ROOT, 'picture', my_file.name)

        with open(path, 'wb') as f:
            for line in my_file:
                f.write(line)

        return JsonResponse({
            "error": 0,
            "url": "/media/picture/%s" % my_file.name
        })

    return render(request, '404.html')
