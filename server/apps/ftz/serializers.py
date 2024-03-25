from rest_framework import serializers

from .models import Course, StudyMaterial, Lesson, Card


class CourseSerializer(serializers.ModelSerializer):
    """
    课程序列化
    """

    class Meta:
        model = Course
        fields = '__all__'


class StudyMaterialSerializer(serializers.ModelSerializer):
    """
    学习素材序列号
    """

    class Meta:
        model = StudyMaterial
        fields = '__all__'


class LessonSerializer(serializers.ModelSerializer):
    """
    课时序列化
    """

    class Meta:
        model = Lesson
        fields = '__all__'


class CardSerializer(serializers.ModelSerializer):
    """
    卡片序列号
    """

    class Meta:
        model = Card
        fields = '__all__'
