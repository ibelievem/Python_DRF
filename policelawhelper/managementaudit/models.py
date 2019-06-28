from django.db import models
import datetime
# Create your models here.

class UserLogin(models.Model):
    id = models.AutoField(primary_key=True)
    phone = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=50)
    Police_code = models.CharField(max_length=50)
    Group_name = models.CharField(max_length=50)
    type = models.CharField(max_length=50)
    grade = models.CharField(max_length=50,null=True,blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class Question(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.CharField(max_length=255)
    A = models.CharField(max_length=100)
    B = models.CharField(max_length=100)
    C = models.CharField(max_length=100)
    D = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    answer = models.CharField(max_length=50)
    is_enable = models.CharField(max_length=5,default="1")
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('create_time',)


class Passnum(models.Model):
    id = models.AutoField(primary_key=True)
    num = models.IntegerField(default=20)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class ActionAnalyze(models.Model):
    id = models.AutoField(primary_key=True)
    phone = models.CharField(max_length=50, unique=True, db_index=True)
    stay_time = models.IntegerField(default=0)
    use_num = models.IntegerField(default=0)
    create_time = models.DateTimeField(auto_now_add=True)


class ClickRecord(models.Model):
    id = models.AutoField(primary_key=True)
    module_name = models.CharField(max_length=50)
    click_num = models.IntegerField(default=0)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class MixCode(models.Model):
    id = models.AutoField(primary_key=True)
    mix_code = models.IntegerField(default=0)
    content = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)


class Charge(models.Model):
    id = models.AutoField(primary_key=True)
    charge = models.CharField(max_length=50)
    create_time = models.DateTimeField(auto_now_add=True)


class HelperData(models.Model):
    id = models.AutoField(primary_key=True)
    charge_id = models.IntegerField(default=0)
    kind_name = models.CharField(max_length=50)
    title = models.CharField(max_length=50)
    content = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)


class Picture(models.Model):
    id = models.AutoField(primary_key=True)
    charge_id = models.IntegerField(default=0)
    kind_name = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    content =models.ImageField(upload_to='media/images', null=True)
    create_time = models.DateTimeField(auto_now_add=True)


class PlotLabel(models.Model):
    id = models.AutoField(primary_key=True)
    tag_name = models.CharField(max_length=50)
    tag_id = models.CharField(max_length=50)


class Collection(models.Model):
    id = models.AutoField(primary_key=True)
    phone = models.CharField(max_length=50, unique=True, db_index=True)
    type = models.CharField(max_length=50)
    article_id = models.CharField(max_length=255)
    create_time = models.DateTimeField(auto_now_add=True)


class UploadFile(models.Model):
    id = models.AutoField(primary_key=True)
    charge_id=models.IntegerField(default=0)
    kind_name = models.CharField(max_length=50)
    title = models.CharField(max_length=255,null=True,blank=True)
    file = models.FileField(upload_to='media/files',null=True)
    create_time = models.DateTimeField(auto_now_add=True)


class TrafficArticle(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    article_title = models.CharField(max_length=255)
    publish_time = models.CharField(max_length=255)
    issuing_agency = models.CharField(max_length=255)
    article_content = models.TextField()
    soucrce_url = models.CharField(max_length=255)


class ArticleStatics(models.Model):
    id = models.AutoField(primary_key=True)
    static_file_name = models.CharField(max_length=255)
    static_file_path = models.CharField(max_length=255)
    article_id = models.CharField(max_length=255)


class Annotation(models.Model):
    id = models.CharField(max_length=255,primary_key=True)
    annotation = models.TextField()
    keywords = models.CharField(max_length=255)
    is_enable = models.CharField(max_length=1, default="1")
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-create_time',)

class Daojiao_lawsearch_code(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.TextField(verbose_name="名称")
    name_md5_id = models.CharField(max_length=32, unique=True, verbose_name="名称md5")
    release_date = models.CharField(max_length=255, verbose_name="发布日期", null=True, blank=True)
    implement_date = models.CharField(max_length=255, verbose_name="实施日期", null=True, blank=True)
    issuing_agency = models.CharField(max_length=255, verbose_name="发文机关", null=True, blank=True)
    location = models.CharField(max_length=255, verbose_name="行政区划", null=True, blank=True)
    issuing_number = models.CharField(max_length=255, null=True, blank=True, verbose_name="发布文号")
    timeliness = models.CharField( max_length=255,verbose_name="时效性", null=True, blank=True)
    law_type = models.CharField( max_length=255, null=True,blank=True, verbose_name="效力等级")
    subject_category = models.CharField(max_length=255, null=True, blank=True, verbose_name="主题分类")
    user_id = models.IntegerField(null=True, blank=True, verbose_name="最后修改人")
    is_enable = models.BooleanField(default=True, null=False, verbose_name="是否可用")
    priority = models.IntegerField(default=0, verbose_name="优先级")
    type_choices = (
        (0, "公开文件"),
        (1, "内部文件")
    )
    type = models.IntegerField(choices=type_choices, default=0, null=True, blank=True, verbose_name="文件类型")

    class Meta:
        db_table = "daojiao_lawsearch_code"
        app_label = 'lawsearch'
        verbose_name = "交警助手 法律法规"
        verbose_name_plural = "交警助手 法律法规"