from django.db import models
from django.contrib.auth.models import AbstractUser

from utils.model import SoftModel, BaseModel
from simple_history.models import HistoricalRecords


class Tag(SoftModel):
    """
    标签表
    """
    name = models.CharField('名称', max_length=128, blank=False)


class EnumConfig(SoftModel):
    """
    枚举配置表
    """
    module = models.CharField('模块', max_length=128, blank=False)
    service = models.CharField('业务', max_length=128, blank=False)
    name = models.CharField('名称', max_length=128, blank=False)
    value = models.CharField('值', max_length=128, blank=False)
    description = models.TextField('描述', blank=True)


# class Group(SoftModel):
#     """
#     分组
#     """
#     name = models.CharField('名称', max_length=128, blank=False)
#     description = models.CharField('描述', max_length=512, blank=True)


def get_enum_choices(module: str, service: str):
    enum_choices = EnumConfig.objects.filter(module=module, service=service).values_list('value', 'name')
    return enum_choices


class Course(SoftModel):
    """
    课程表
    """
    # course_type_choices = (
    #     ('公开课', '公开课'),
    #     ('入门课', '入门课'),
    #     ('进阶课', '进阶课'),
    # )
    title = models.CharField('课程标题', max_length=128, unique=True, blank=False)
    description = models.TextField('描述', blank=True)
    type = models.CharField('课程类型', max_length=128, choices=[])
    lesson_count = models.IntegerField('课程数量', default=0)

    def __init__(self, *args, **kwargs):
        super(Course, self).__init__(*args, **kwargs)
        self._meta.get_field('type').choices = get_enum_choices(module='course', service='type')


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
    title = models.CharField('标题', max_length=128, blank=False)
    sub_title = models.CharField('副标题', max_length=512, blank=True)
    description = models.TextField('描述', blank=True)
    type = models.CharField('课程类型', max_length=128, choices=[])
    context = models.TextField('素材内容', blank=True)
    # words = models.ManyToManyField(Word, blank=True, verbose_name='单词', related_name='words')
    # grammars = models.ManyToManyField(Grammar, blank=True, verbose_name='语法', related_name='grammars')
    tags = models.ManyToManyField(Tag, blank=True, verbose_name='标签', related_name='tags')

    def __init__(self, *args, **kwargs):
        super(StudyMaterial, self).__init__(*args, **kwargs)
        self._meta.get_field('type').choices = get_enum_choices(module='material', service='type')


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
    type = models.CharField('课程类型', max_length=128, choices=[])
    status = models.IntegerField('状态', choices=[], default=0)
    card_core_image = models.CharField('核心图', max_length=128, blank=True)
    group_name = models.CharField('卡片分组名称', max_length=512, blank=True)
    topic = models.CharField('话题', max_length=128, blank=True)
    difficulty = models.CharField('难度', max_length=32, choices=[], blank=False, default='easy')
    study_materials = models.ManyToManyField(StudyMaterial, blank=True, verbose_name='素材',
                                             related_name='study_materials')

    def __init__(self, *args, **kwargs):
        super(Card, self).__init__(*args, **kwargs)
        self._meta.get_field('type').choices = get_enum_choices(module='card', service='type')
        self._meta.get_field('difficulty').choices = get_enum_choices(module='card', service='difficulty')
        self._meta.get_field('status').choices = get_enum_choices(module='card', service='status')


class Lesson(SoftModel):
    """
    课时表
    """
    # lesson_type_choices = (
    #     ('编程课', '编程课'),
    #     ('编程卡', '编程卡'),
    # )
    title = models.CharField('课时标题', max_length=128, blank=False)
    description = models.TextField('描述', blank=True)
    type = models.CharField('课程类型', max_length=128, choices=[])
    lesson_number = models.IntegerField('顺序', blank=False)
    group_name = models.CharField('课时分组', default='默认分组', max_length=512)
    version = models.CharField('版本号')

    cards = models.ManyToManyField(Card, blank=True, verbose_name='卡片', related_name='cards')
    course_id = models.ForeignKey(Course, on_delete=models.SET_NULL, verbose_name='课程', blank=True, null=True)

    def __init__(self, *args, **kwargs):
        super(Lesson, self).__init__(*args, **kwargs)
        self._meta.get_field('type').choices = get_enum_choices(module='lesson', service='type')
