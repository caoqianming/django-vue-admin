from django.test import TestCase

# Create your tests here.
from .models import StudyMaterial, Tag


class TestStudyMaterial(TestCase):

    def test_create_study_material(self):
        material = StudyMaterial.objects.create(
            title='新的学习素材标题',
            sub_title='副标题',
            description='描述',
            type='Article',
            context='素材内容'
        )

        # 获取要关联的标签和卡片实例（假设已经存在）
        tag1 = Tag.objects.get(pk=1)
        tag2 = Tag.objects.get(pk=2)
        # 将标签和卡片关联到新的 StudyMaterial 实例
        material.tags.add(tag1, tag2)


