# _*_ coding:utf-8 _*_
#@Author = zhoupengfei
#@Time = 2018/12/6 14:57
from rest_framework import serializers
from .models import Question,Annotation

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = "__all__"


class AnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Annotation
        fields = "__all__"