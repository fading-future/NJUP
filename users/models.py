# users/models.py

"""
用户模型和相关模型定义。
该模块定义了用户、管理员、教师、学生、课程、问题、答案等模型类，并实现了相应的索引和字符串表示方法。
这些模型类用于 Django ORM 数据库操作。
主要功能：
- 定义用户模型（User）及其管理器（UserManager）
- 定义管理员（Administrator）、教师（Teacher）、学生（Student）模型
- 定义课程（Course）、问题（Question）、答案（StudentAnswer）模型   
- 定义评分反馈（ScoringFeedback）模型
- 定义 APIKey 模型，用于存储 API 密钥
- 定义学生选课（StudentCourse）模型
- 定义操作日志（OperationLog）模型
- 定义索引以优化查询性能
- 定义字符串表示方法以便于调试和管理
作者：DKW
日期：2025年10月
版本：1.0
注意：在使用这些模型之前，请确保已正确配置 Django 项目和数据库连接。
"""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from django.conf import settings  # 用于引用自定义的 User 模型


# 自定义用户管理器
class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, role="student"):
        if not email:
            raise ValueError("Users must have an email address")
        if not name:
            raise ValueError("Users must have a name")

        email = self.normalize_email(email)
        user = self.model(email=email, name=name, role=role)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        user = self.create_user(email, name, password, role="admin")
        user.is_admin = True
        user.save(using=self._db)
        return user


# 用户模型
class User(AbstractBaseUser):
    ROLE_CHOICES = (
        ("admin", "管理员"),
        ("teacher", "教师"),
        ("student", "学生"),
        # ("parent", "家长"),
    )

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100, unique=True, null=True)  # , blank=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="student")

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return self.email if self.email else self.name

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

# 定义管理员模型
class Administrator(models.Model):
    # user = models.OneToOneField(
    #     settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True
    # )
    AdminID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=50, default="admin")
    Email = models.EmailField(max_length=100, null=True, unique=True)  # , blank=True)
    Password = models.CharField(max_length=255, default="123456")  # 加密存储

    class Meta:
        db_table = "Administrator"
        indexes = [
            models.Index(fields=["Email"], name="idx_admin_email"),
        ]

    def __str__(self):
        return self.Name


class OperationLog(models.Model):
    LogID = models.AutoField(primary_key=True)
    AdminID = models.ForeignKey(
        Administrator, on_delete=models.CASCADE, related_name="operation_logs"
    )
    Operation = models.CharField(max_length=200)
    Details = models.TextField()
    Timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "OperationLog"
        indexes = [
            models.Index(fields=["Timestamp"], name="idx_log_timestamp"),
        ]

    def __str__(self):
        return f"{self.Operation} by {self.AdminID.Name} at {self.Timestamp}"


class Teacher(models.Model):
    # user = models.OneToOneField(
    #     settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True
    # )
    TeacherID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=50)
    Email = models.EmailField(max_length=100, null=True, unique=True)  # , blank=True)
    Password = models.CharField(max_length=255, default="123456")

    class Meta:
        db_table = "Teacher"
        indexes = [
            models.Index(fields=["Email"], name="idx_teacher_email"),
        ]

    def __str__(self):
        return self.Name

# 定义一个名为 APIKey 的模型类，继承自 Django 的 models.Model 类
class APIKey(models.Model):
    # KeyID 字段：自动递增的整数，作为主键
    KeyID = models.AutoField(primary_key=True)

    # TeacherID 字段：外键，关联到 Teacher 模型。当对应的 Teacher 记录被删除时，级联删除此 APIKey 记录
    # related_name="api_keys" 允许通过 teacher.api_keys 访问所有与该教师相关的 APIKey 对象
    TeacherID = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name="api_keys"
    )

    # Model 字段：最大长度为50的字符串字段，用于存储与该 APIKey 相关的模型名称
    Model = models.CharField(max_length=50)

    # Version 字段：最大长度为20的字符串字段，用于存储与该 APIKey 相关的模型版本号
    Version = models.CharField(max_length=20)

    # KeyValue 字段：最大长度为255的字符串字段，用于存储实际的 API 密钥值
    KeyValue = models.CharField(max_length=255)

    # Status 字段：布尔类型，默认值为 True。表示该 APIKey 是否处于启用状态
    Status = models.BooleanField(default=True)

    # Meta 是内部类，用于定义模型的元数据（如数据库表名、索引等）
    class Meta:
        # 指定该模型对应的真实数据库表名为 "APIKey"
        db_table = "APIKey"

        # 定义索引以优化查询性能
        indexes = [
            # 创建一个联合索引，基于 TeacherID 和 Status 字段，命名为 idx_apikey_teacher_status
            models.Index(fields=["TeacherID", "Status"], name="idx_apikey_teacher_status"),
            
            # 创建另一个联合索引，基于 Model 和 Version 字段，命名为 idx_apikey_model_version
            models.Index(fields=["Model", "Version"], name="idx_apikey_model_version"),
        ]

    # __str__ 方法：定义对象的字符串表示形式，方便在管理后台或调试时查看
    def __str__(self):
        # 返回格式化的字符串，包含 APIKey 的 ID 及其所属教师的名字
        return f"APIKey {self.KeyID} for {self.TeacherID.Name}"


class Course(models.Model):
    CourseID = models.AutoField(primary_key=True)
    TeacherID = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name="courses"
    )
    Name = models.CharField(max_length=100)
    Description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "Course"
        indexes = [
            models.Index(fields=["TeacherID"], name="idx_course_teacher"),
        ]

    def __str__(self):
        # return self.Name
        return f"{self.CourseID} - {self.Name}"


class Student(models.Model):
    # user = models.OneToOneField(
    #     settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True
    # )
    StudentID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=50)
    Email = models.EmailField(max_length=100, null=True, unique=True)  # , blank=True)
    Password = models.CharField(max_length=255, default="123456")

    class Meta:
        db_table = "Student"
        indexes = [
            models.Index(fields=["Email"], name="idx_student_email"),
        ]

    def __str__(self):
        return self.Name


class StudentCourse(models.Model):
    StudentID = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="student_courses"
    )  # 外键关联学生表
    CourseID = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="student_courses"
    )  # 外键关联课程表

    class Meta:
        db_table = "StudentCourse"  # 表名
        unique_together = ("StudentID", "CourseID")  # 联合唯一索引
        indexes = [
            models.Index(
                fields=["StudentID", "CourseID"], name="idx_student_course"
            ),  # 经常需要根据StudentID和CourseID两个字段一起查询数据，故建立复合索引
        ]

    def __str__(self):
        return f"{self.StudentID.Name} enrolled in {self.CourseID.Name}"


class Question(models.Model):
    QuestionID = models.AutoField(primary_key=True)
    CourseID = models.ForeignKey(
        "Course", on_delete=models.CASCADE, related_name="questions"
    )
    Title = models.CharField(max_length=100)
    Content = models.TextField()
    ScoringCriteria = models.TextField(null=True, blank=True)
    Prompt = models.TextField(null=True, blank=True)
    CreatedAt = models.DateTimeField(
        default=timezone.now
    )  # timezone.now返回当前时间（带时区，默认为UTC，可通过settings.py修改）
    IsOpen = models.BooleanField(default=False)
    OpenAt = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "Question"
        indexes = [
            models.Index(
                fields=["CourseID", "IsOpen"], name="idx_question_course_open"
            ),  # 经常需要根据CourseID和IsOpen两个字段一起查询数据
            models.Index(fields=["CreatedAt"], name="idx_question_created_at"),
            # 经常需要根据CreatedAt字段排序
        ]

    def __str__(self):
        return self.Title


class StudentAnswer(models.Model):
    AnswerID = models.AutoField(
        primary_key=True
    )  # 主键，聚簇索引，按主键字段排序数据，用于快速定位行
    QuestionID = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="answers"
    )  # 非聚簇索引，加速按外键字段过滤或关联查询，避免全表扫描
    StudentID = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="answers"
    )  # 非聚簇索引，加速按外键字段过滤或关联查询，避免全表扫描
    Content = models.TextField(blank=True, null=True)
    SubmittedAt = models.DateTimeField(default=timezone.now)
    ConfirmedAt = models.DateTimeField(
        null=True, blank=True
    )  # 该答案的评分与反馈确认时间

    class Meta:
        db_table = "StudentAnswer"
        indexes = [
            models.Index(
                fields=["QuestionID", "StudentID"], name="idx_answer_question_student"
            ),  # 经常需要根据QuestionID和StudentID两个字段一起查询数据
            models.Index(fields=["SubmittedAt"], name="idx_answer_submitted_at"),
            # 经常需要根据SubmittedAt字段排序
        ]

    def __str__(self):
        return f"Answer {self.AnswerID} by {self.StudentID.Name}"


class ScoringFeedback(models.Model):
    FeedbackID = models.AutoField(primary_key=True)
    AnswerID = models.ForeignKey(
        StudentAnswer, on_delete=models.CASCADE, related_name="feedbacks"
    )
    Score = models.FloatField()
    Feedback = models.TextField(null=True, blank=True)
    CreatedAt = models.DateTimeField(default=timezone.now)
    IsFinal = models.BooleanField(default=False)

    class Meta:
        db_table = "ScoringFeedback"
        indexes = [
            models.Index(
                fields=["AnswerID", "IsFinal"], name="idx_feedback_answer_final"
            ),
            models.Index(fields=["CreatedAt"], name="idx_feedback_created_at"),
        ]

    def __str__(self):
        return f"Feedback {self.FeedbackID} for Answer {self.AnswerID.AnswerID}"
    
    

# class KnowledgeWeaknessAnalysis(models.Model):
#     """
#     知识点薄弱分析模型，用于记录学生在某次答题中表现出的薄弱知识点。
#     与 ScoringFeedback 关联，可支持自动或人工分析结果。
#     """
#     WeaknessID = models.AutoField(primary_key=True)  # 主键，自动递增
#     # 与 ScoringFeedback 建立外键关系
#     feedback = models.ForeignKey(
#         ScoringFeedback,
#         on_delete=models.CASCADE,  # 当 feedback 被删除时，该分析也一并删除
#         related_name='weakness_analysis'  # 反向访问字段名
#     )

#     # 表示识别出的薄弱知识点名称（例如“函数”、“牛顿定律”等）
#     knowledge_point = models.CharField(
#         max_length=255,
#         verbose_name="薄弱知识点"
#     )

#     # 分析来源，说明是系统自动识别还是教师手动添加
#     analysis_source = models.CharField(
#         max_length=50,
#         choices=[
#             ('system', '系统分析'),
#             ('teacher', '教师标记')
#         ],
#         default='system',
#         verbose_name="分析来源"
#     )

#     # 可选字段，用于推荐学习资料、视频链接或练习题目
#     suggested_resource = models.TextField(
#         blank=True,
#         null=True,
#         verbose_name="建议学习资源"
#     )

#     # 记录创建时间，默认为当前时间
#     created_at = models.DateTimeField(
#         auto_now_add=True,
#         verbose_name="创建时间"
#     )

#     class Meta:
#         db_table = "KnowledgeWeaknessAnalysis"  # 自定义数据库表名
#         verbose_name = "知识点薄弱分析"
#         verbose_name_plural = "知识点薄弱分析列表"

#         # 保证同一个 feedback 不会重复分析同一个知识点
#         unique_together = [
#             ['feedback', 'knowledge_point']
#         ]

#         # 添加索引提升查询效率
#         indexes = [
#             models.Index(fields=['feedback'], name='idx_weakness_feedback'),
#             models.Index(fields=['knowledge_point'], name='idx_weakness_kp'),
#             models.Index(fields=['created_at'], name='idx_weakness_created_at'),
#         ]

#     def __str__(self):
#         return f"WeaknessFeedback {self.WeaknessID} for Weakness {self.feedback}"

# 定义家长模型
# class Parent(models.Model):
#     ParentID = models.AutoField(primary_key=True)
#     Name = models.CharField(max_length=50)
#     Email = models.EmailField(max_length=100, null=True, unique=True)  # , blank=True)
#     Password = models.CharField(max_length=255, default="123456")

#     class Meta:
#         db_table = "Parent"
#         indexes = [
#             models.Index(fields=["Email"], name="idx_parent_email"),
#         ]

#     def __str__(self):
#         return self.Name


# 和老师进行私信的模型
# class ParentMessage(models.Model):
#     MessageID = models.AutoField(primary_key=True)
#     ParentID = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name="messages")
#     TeacherID = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="messages")
#     Content = models.TextField()
#     CreatedAt = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         db_table = "ParentMessage"
#         indexes = [
#             models.Index(fields=["ParentID", "TeacherID"], name="idx_parent_teacher"),
#             models.Index(fields=["CreatedAt"], name="idx_message_created_at"),
#         ]

#     def __str__(self):
#         return f"Message {self.MessageID} from {self.ParentID.Name} to {self.TeacherID.Name}"

# 查看关联学生的成绩和评价
# class ParentStudentPerformance(models.Model):
#     ParentID = models.ForeignKey(
#         "Parent", on_delete=models.CASCADE, related_name="student_performances"
#     )
#     StudentID = models.ForeignKey(
#         "Student", on_delete=models.CASCADE, related_name="parent_performances"
#     )
#     CourseID = models.ForeignKey(
#         "Course", on_delete=models.CASCADE, related_name="parent_performances"
#     )
#     AverageScore = models.FloatField(null=True, blank=True)
#     LastFeedback = models.TextField(null=True, blank=True)

#     class Meta:
#         db_table = "ParentStudentPerformance"
#         indexes = [
#             models.Index(fields=["ParentID", "StudentID"], name="idx_parent_student"),
#             models.Index(fields=["CourseID"], name="idx_performance_course"),
#         ]

#     def __str__(self):
#         return f"{self.ParentID.Name} - {self.StudentID.Name} - {self.CourseID.Name}"