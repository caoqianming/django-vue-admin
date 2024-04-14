from rest_framework import serializers

from .models import Course, StudyMaterial, Lesson, Card, Tag


class CourseSerializer(serializers.ModelSerializer):
    """
    课程序列化
    """

    class Meta:
        model = Course
        fields = '__all__'


class LessonListSerializer(serializers.ModelSerializer):
    """
    课时序列化
    """

    class Meta:
        model = Lesson
        fields = '__all__'


class CardListSerializer(serializers.ModelSerializer):
    """
    卡片序列号
    """

    class Meta:
        model = Card
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    """
    标签序列号
    """

    class Meta:
        model = Tag
        fields = '__all__'


class TagDetailSerializer(serializers.ModelSerializer):
    """
    标签序列号
    """

    class Meta:
        model = Tag
        fields = ['id', 'name', 'create_time']


class StudyMaterialListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyMaterial
        fields = ['id', 'title', 'sub_title', 'description', 'type', 'context', 'tags']


class StudyMaterialDetailSerializer(serializers.ModelSerializer):
    tags = TagDetailSerializer(many=True, read_only=True)

    class Meta:
        model = StudyMaterial
        fields = ['id', 'title', 'sub_title', 'description', 'type', 'context', 'tags']


class CardDetailSerializer(serializers.ModelSerializer):
    """
    卡片序列号
    """
    study_materials = StudyMaterialDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Card
        fields = '__all__'


class LessonDetailSerializer(serializers.ModelSerializer):
    """
    课时序列化
    """
    cards = CardDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = '__all__'
