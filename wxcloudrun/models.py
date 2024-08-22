from datetime import datetime

from django.db import models


# Create your models here.
class Counters(models.Model):
    id = models.AutoField
    count = models.IntegerField(max_length=11, default=0)
    createdAt = models.DateTimeField(default=datetime.now(), )
    updatedAt = models.DateTimeField(default=datetime.now(),)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'Counters'  # 数据库表名


class MyUserModel(models.Model):
    openid = models.CharField(max_length=50, unique=False)              #记录用户openid方便获取信息操作
    nickname = models.CharField(max_length=100, null=True, blank=True) #记录用户昵称
    avatar_url = models.URLField(null=True, blank=True)                 #记录用户头像
    created_at = models.DateTimeField(auto_now_add=True)                 #记录时间
    amout=models.FloatField()                                           # 记录金额 
    def __str__(self):
        return self.openid
    

class TestModel(models.Model):
    name=models.CharField(max_length=20)

