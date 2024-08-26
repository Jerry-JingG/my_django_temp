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


class Donation(models.Model):
    id=models.AutoField(primary_key=True)
    openid = models.CharField(max_length=100)               #记录用户openid方便获取信息操作
    nickname = models.CharField(max_length=50)              #记录用户昵称
    wb_id=models.CharField(max_length=50)                   #记录用户微博id
    avatar_url = models.CharField(max_length=200)           #记录用户头像
    created_at = models.CharField(max_length=200)            #记录时间
    amount=models.FloatField()                              # 记录金额 
    def __str__(self):
        return self.openid
    class Meta:
        db_table = 'Donation'  # 数据库表名

class CheckedBill(models.Model):
    id=models.AutoField(primary_key=True)              #unique id for each bill
    recipient=models.CharField(max_length=100)
    amount=models.FloatField()
    bill_id=models.CharField(max_length=150)
    wb_id=models.CharField(max_length=100)
    payment=models.CharField(max_length=100)
    remark=models.CharField(max_length=100)
    status=models.CharField(max_length=100)
    time=models.CharField(max_length=100)

    def __str__(self):
        return self.bill_id
    class Meta:
        db_table='Checked_Bill'

    

class TestModel(models.Model):
    name=models.CharField(max_length=20)

