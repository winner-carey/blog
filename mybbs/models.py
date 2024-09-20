from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser


# 继承AbstractUser表，应用auth模块
class UserInfo(AbstractUser):
    nid = models.AutoField(primary_key=True)
    # 手机号
    telephone = models.CharField(max_length=32)
    # 用户头像，用FileField上传文件字段 类实例化,upload_to指定上传路径
    avator = models.FileField(upload_to='avator/', default='avator/default.png')
    # 用户创建时间, DateTime 和 Date的区别，年月日时分秒和年月日的区别
    create_date = models.DateTimeField(auto_now_add=True)
    # 用户博客--一对一对应博客表
    blog = models.OneToOneField(to='Blog', to_field='nid', null=True)


class Blog(models.Model):
    nid = models.AutoField(primary_key=True)
    # 博客名称
    title = models.CharField(max_length=32)
    # 站点名称
    site_name = models.CharField(max_length=32)
    # 博客主题样式
    theme = models.CharField(max_length=32)

    def __str__(self):
        return self.title


class Category(models.Model):
    nid = models.AutoField(primary_key=True)
    # 博客分类名称
    title = models.CharField(max_length=32)
    # 分类一对多博客
    blog = models.ForeignKey(to='Blog', to_field='nid', null=True)

    def __str__(self):
        return self.title


class Tag(models.Model):
    nid = models.AutoField(primary_key=True)
    # 博客标签名称
    title = models.CharField(max_length=32)
    # 标签一对多博客
    blog = models.ForeignKey(to='Blog', to_field='nid', null=True)

    def __str__(self):
        return self.title


class Article(models.Model):
    nid = models.AutoField(primary_key=True)
    # 文章标题
    title = models.CharField(max_length=32)
    # 文章摘要
    desc = models.CharField(max_length=255)
    # 文章内容，用TextField 类存大文本
    content = models.TextField()
    # 文章创建时间
    create_date = models.DateTimeField(auto_now_add=True)

    # 数据库优化设计，减少跨表查询次数，数据读多写少
    # 评论数
    comment_num = models.IntegerField(default=0)
    # 点赞数
    up_num = models.IntegerField(default=0)
    # 点踩数
    down_num = models.IntegerField(default=0)

    # 文章作者，跟用户一对多
    user = models.ForeignKey(to='UserInfo', to_field='nid', null=True)
    # 文章分类，跟文章一对多
    category = models.ForeignKey(to='Category', to_field='nid', null=True)
    # 文章标签，跟文章多对多（通过through指定自己写的中间表），半自动方式
    tag = models.ManyToManyField(to='Tag', through='Article2Tag',
                                 through_fields=('article', 'tag'))

    def __str__(self):
        return self.title


class Article2Tag(models.Model):
    nid = models.AutoField(primary_key=True)
    # 文章id
    article = models.ForeignKey(to='Article', to_field='nid', null=True)
    # 标签id
    tag = models.ForeignKey(to='Tag', to_field='nid', null=True)

    def __str__(self):
        return self.tag.title


class ArticleUpDown(models.Model):
    nid = models.AutoField(primary_key=True)
    # 点赞/点踩 的字段 ,跟用户一对多
    user = models.ForeignKey(to='UserInfo', to_field='nid', null=True)
    # 点赞/点踩 的字段，跟文章一对多
    article = models.ForeignKey(to='Article', to_field='nid', null=True)
    # 点赞点踩标志位，1为赞，0为踩 ,用BooleanField类实例化
    is_up = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username


class Comment(models.Model):
    nid = models.AutoField(primary_key=True)
    # 评论的用户
    user = models.ForeignKey(to='UserInfo', to_field='nid', null=True)
    # 评论的文章
    article = models.ForeignKey(to='Article', to_field='nid', null=True)
    # 评论的内容
    comm = models.CharField(max_length=255)
    # 评论的时间
    create_date = models.DateTimeField(auto_now_add=True)
    # 父评论的id，自关联，防止写脏数据
    parent_comment = models.ForeignKey(to='self', to_field='nid', null=True)
    # parent_comment = models.ForeignKey(to='Comment',to_field='nid')
