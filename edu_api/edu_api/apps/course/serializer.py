from rest_framework.serializers import ModelSerializer, SerializerMethodField

from course.models import CourseCategory, Course, Teacher


class CourseCategorySerializer(ModelSerializer):
    """课程分类"""

    class Meta:
        model = CourseCategory
        fields = ["id", "name"]


class CourseTeacherSerializer(ModelSerializer):
    """课程所属老师的序列化器"""

    class Meta:
        model = Teacher
        fields = ("id", "name", "title", "signature", 'image')


class CourseModelSerializer(ModelSerializer):
    """课程列表"""

    # 序列化器嵌套查询老师信息
    teacher = CourseTeacherSerializer()

    class Meta:
        model = Course
        fields = ["id", "name", "course_img", "students", "lessons", "pub_lessons", "price", "teacher", "lesson_list",
                  'discount_name', 'real_price']


class CourseDetailModelSerializer(ModelSerializer):
    teacher = CourseTeacherSerializer()
    level_name = SerializerMethodField()

    def get_level_name(self, obj):
        return obj.get_level_display()

    class Meta:
        model = Course
        fields = ["id", "name", "students", "lessons", 'pub_lessons', 'file_path', 'course_img',
                  "price", "teacher", 'chapter_list', 'brief_', 'level_name', 'comment', 'problems_',
                  'real_price', 'discount_name', 'active_time']
