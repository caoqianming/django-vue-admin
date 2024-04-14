from django.db import models
from django.contrib.auth.models import AbstractUser

from utils.model import SoftModel, BaseModel
from simple_history.models import HistoricalRecords


class Tag(SoftModel):
    """
    标签表
    """
    name = models.CharField('名称', max_length=128, blank=False)


# class Group(SoftModel):
#     """
#     分组
#     """
#     name = models.CharField('名称', max_length=128, blank=False)
#     description = models.CharField('描述', max_length=512, blank=True)


class Course(SoftModel):
    """
    课程表
    """
    course_type_choices = (
        ('公开课', '公开课'),
        ('入门课', '入门课'),
        ('进阶课', '进阶课'),
    )
    title = models.CharField('课程标题', max_length=128, unique=True, blank=False)
    description = models.TextField('描述', blank=True)
    type = models.CharField('课程类型', max_length=128, choices=course_type_choices, default='公开课')
    lesson_count = models.IntegerField('课程数量', default=0)


# class Word(SoftModel):
#     """
#     单词表
#     """
#     pass
#
#
# class Grammar(SoftModel):
#     """
#     语法表
#     """
#     pass


class StudyMaterial(SoftModel):
    """
    学习素材表
    """
    material_type_choices = (
        ('QNA', '问卷页'),
        ('Article', '图文内容页'),
        ('TrueFalse', '判断题页'),
    )
    title = models.CharField('标题', max_length=128, blank=False)
    sub_title = models.CharField('副标题', max_length=512, blank=True)
    description = models.TextField('描述', blank=True)
    type = models.CharField('课程类型', max_length=128, choices=material_type_choices)
    context = models.TextField('素材内容')
    # words = models.ManyToManyField(Word, blank=True, verbose_name='单词', related_name='words')
    # grammars = models.ManyToManyField(Grammar, blank=True, verbose_name='语法', related_name='grammars')
    tags = models.ManyToManyField(Tag, blank=True, verbose_name='标签', related_name='tags')


class Card(SoftModel):
    """
    卡片表
    """
    card_type_choices = (
        ('编程课', '编程课'),
        ('编程卡', '编程卡'),
    )
    card_status_choices = (
        (0, '下线'),
        (1, '上线')
    )

    card_difficulty_choices = (
        ('easy', '简单'),
        ('medium', '中等'),
        ('difficult', '困难'),
    )
    title = models.CharField('课时标题', max_length=128, blank=False)
    description = models.TextField('描述', blank=True)
    type = models.CharField('课程类型', max_length=128, choices=card_type_choices, default='编程课')
    status = models.IntegerField('状态', choices=card_status_choices, default=0)
    card_core_image = models.CharField('核心图', max_length=128, blank=True)
    group_name = models.CharField('卡片分组名称', max_length=512, blank=True)
    topic = models.CharField('话题', max_length=128, blank=True)
    difficulty = models.CharField('难度', max_length=32, choices=card_difficulty_choices, blank=False, default='easy')
    study_materials = models.ManyToManyField(StudyMaterial, blank=True, verbose_name='素材', related_name='study_materials')


class Lesson(SoftModel):
    """
    课时表
    """
    lesson_type_choices = (
        ('编程课', '编程课'),
        ('编程卡', '编程卡'),
    )
    title = models.CharField('课时标题', max_length=128, blank=False)
    description = models.TextField('描述', blank=True)
    type = models.CharField('课程类型', max_length=128, choices=lesson_type_choices, default='编程课')
    lesson_number = models.IntegerField('顺序', blank=False)
    group_name = models.CharField('课时分组', default='默认分组', max_length=512)
    version = models.CharField('版本号')

    cards = models.ManyToManyField(Card, blank=True, verbose_name='卡片', related_name='cards')
    course_id = models.ForeignKey(Course, on_delete=models.SET_NULL, verbose_name='课程', blank=True, null=True)
