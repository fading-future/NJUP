# users/admin.py

# 导入 Django 提供的 admin 模块，用于注册模型并启用管理界面功能
from django.contrib import admin

# 从当前应用（users）的 models.py 中导入需要注册到后台管理的所有模型
from .models import (
    User,
    Administrator,
    OperationLog,
    Teacher,
    APIKey,
    Course,
    Student,
    StudentCourse,
    Question,
    StudentAnswer,
    ScoringFeedback,
    # KnowledgeWeaknessAnalysis,
)

# 将 User 模型注册到 Admin 后台，使用默认的展示方式，后面同理
admin.site.register(User)
admin.site.register(Administrator)
admin.site.register(OperationLog)
admin.site.register(Teacher)
admin.site.register(APIKey)
admin.site.register(Course)
admin.site.register(Student)
admin.site.register(StudentCourse)
admin.site.register(Question)
admin.site.register(StudentAnswer)
admin.site.register(ScoringFeedback)
# admin.site.register(KnowledgeWeaknessAnalysis)
