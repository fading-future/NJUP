# users/forms.py

"""
本文件主要用于前端界面展示，继承models.py中的模型类，定义表单类。
表单类主要用于数据验证和数据清洗，确保用户输入的数据符合预期格式。
表单类通常用于处理用户输入的数据，并将其转换为模型实例。
"""
from django import forms
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
from django.forms import ModelForm
from django.contrib.auth.hashers import make_password

# 定义一个 AddTeacherForm 表单类，继承自 ModelForm
class AddTeacherForm(ModelForm):
    # 手动定义一个密码字段，使用 PasswordInput 小部件，输入内容会被隐藏
    password = forms.CharField(widget=forms.PasswordInput, label="密码")

    # Meta 是 ModelForm 的内部类，用于配置表单与模型之间的关系
    class Meta:
        # 指定这个表单对应的数据库模型是 Teacher
        model = Teacher
        
        # 指定要在表单中包含的字段（注意字段名要和模型中的字段一致）
        fields = ["Name", "Email", "Password"]
        
        # 为每个字段指定使用的 HTML 小部件（widget）及其属性
        widgets = {
            # Name 字段使用文本输入框，并添加 Bootstrap 样式类 form-control
            "Name": forms.TextInput(attrs={"class": "form-control"}),
            
            # Email 字段使用邮箱输入框，同样添加 form-control 样式
            "Email": forms.EmailInput(attrs={"class": "form-control"}),
            
            # Password 字段使用密码输入框，添加样式
            "Password": forms.PasswordInput(attrs={"class": "form-control"}),
        }

    # 重写 save 方法，以便在保存前对密码进行加密处理
    def save(self, commit=True):
        # 调用父类的 save 方法，并不立即提交到数据库（commit=False）
        teacher = super().save(commit=False)
        
        # 使用 make_password 对用户输入的密码进行哈希加密
        teacher.Password = make_password(self.cleaned_data["password"])
        
        # 如果 commit 为 True，则将对象保存到数据库
        if commit:
            teacher.save()
        
        # 返回保存后的 teacher 实例（无论是否已提交）
        return teacher

# 定义一个 AddStudentForm 表单类，继承自 ModelForm，类似上面的 AddTeacherForm
class AddStudentForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="密码")

    class Meta:
        model = Student
        fields = ["Name", "Email", "Password"]
        widgets = {
            "Name": forms.TextInput(attrs={"class": "form-control"}),
            "Email": forms.EmailInput(attrs={"class": "form-control"}),
            "Password": forms.PasswordInput(attrs={"class": "form-control"}),
        }

    def save(self, commit=True):
        student = super().save(commit=False)
        student.Password = make_password(self.cleaned_data["password"])
        if commit:
            student.save()
        return student


# 定义一个名为 EditTeacherForm 的表单类，用于编辑教师信息，继承自 ModelForm
class EditTeacherForm(ModelForm):

    # 被注释掉的密码字段定义：
    # 可以让用户在编辑页面选择是否输入新密码（设置 required=False 表示非必填）
    # 使用 PasswordInput 小部件隐藏输入内容，标签为“密码”
    # password = forms.CharField(
    #     widget=forms.PasswordInput, label="密码", required=False
    # )

    # Meta 是 ModelForm 的内部类，用于配置该表单与模型之间的关系
    class Meta:
        # 指定该表单对应的模型是 Teacher
        model = Teacher

        # 指定要在表单中包含的字段：Name、Email、Password
        fields = ["Name", "Email", "Password"]

        # 定义每个字段在前端渲染时使用的 HTML 小部件和属性
        widgets = {
            # Name 字段使用文本输入框，并添加 Bootstrap 样式类 form-control
            "Name": forms.TextInput(attrs={"class": "form-control"}),

            # Email 字段使用邮箱输入框，并添加样式类
            "Email": forms.EmailInput(attrs={"class": "form-control"}),

            # Password 字段使用密码输入框，输入内容会隐藏，同样添加样式类
            "Password": forms.PasswordInput(attrs={"class": "form-control"}),
        }

    # 重写 save 方法，实现对密码字段的条件性加密处理
    def save(self, commit=True):
        # 先调用父类的 save 方法，但不立即提交到数据库（commit=False）
        teacher = super().save(commit=False)

        # 从 cleaned_data 中获取用户输入的密码，如果未填写则返回 None
        password = self.cleaned_data.get("Password")

        # 如果用户输入了新密码，则进行哈希加密并赋值给 teacher.Password
        if password:
            teacher.Password = make_password(password)

        # 如果 commit 参数为 True，将修改保存到数据库
        if commit:
            teacher.save()

        # 返回 teacher 实例（无论是否已提交到数据库）
        return teacher


class EditStudentForm(ModelForm):
    # password = forms.CharField(widget=forms.PasswordInput, label="密码", required=False)

    class Meta:
        model = Student
        fields = ["Name", "Email", "Password"]
        widgets = {
            "Name": forms.TextInput(attrs={"class": "form-control"}),
            "Email": forms.EmailInput(attrs={"class": "form-control"}),
            "Password": forms.PasswordInput(attrs={"class": "form-control"}),
        }

    def save(self, commit=True):
        student = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            student.Password = make_password(password)
        if commit:
            student.save()
        return student



# 定义一个名为 AddAPIKeyForm 的表单类，继承自 ModelForm
class AddAPIKeyForm(ModelForm):

    # Meta 是 ModelForm 的内部类，用于配置该表单与模型之间的关系
    class Meta:
        # 指定这个表单对应的模型是 APIKey
        model = APIKey

        # 指定要在表单中包含的字段（这些字段必须存在于 APIKey 模型中）
        fields = ["TeacherID", "Model", "Version", "KeyValue", "Status"]

        # 为每个字段指定前端渲染时使用的 HTML 小部件（widget）和属性
        widgets = {

            # TeacherID 字段使用 Select 下拉选择框（适用于外键字段），并添加 Bootstrap 样式类
            "TeacherID": forms.Select(attrs={"class": "form-control"}),

            # Model 字段使用文本输入框，添加 form-control 类以便样式统一
            "Model": forms.TextInput(attrs={"class": "form-control"}),

            # Version 字段也使用文本输入框，同样应用 Bootstrap 样式
            "Version": forms.TextInput(attrs={"class": "form-control"}),

            # KeyValue 字段表示 API Key 的值，使用普通文本输入框，带相同样式
            "KeyValue": forms.TextInput(attrs={"class": "form-control"}),

            # Status 字段是一个布尔类型（True/False），使用复选框控件，并使用 form-check-input 类适配 Bootstrap 的表单组样式
            "Status": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class EditAPIKeyForm(ModelForm):
    class Meta:
        model = APIKey
        fields = ["TeacherID", "Model", "Version", "KeyValue"]
        widgets = {
            "TeacherID": forms.Select(attrs={"class": "form-control"}),
            "Model": forms.TextInput(attrs={"class": "form-control"}),
            "Version": forms.TextInput(attrs={"class": "form-control"}),
            "KeyValue": forms.TextInput(attrs={"class": "form-control"}),
        }


class AddQuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["CourseID", "Title", "Content", "ScoringCriteria", "Prompt", "IsOpen"]
        widgets = {
            "CourseID": forms.Select(attrs={"class": "form-control"}),
            "Title": forms.TextInput(attrs={"class": "form-control"}),
            "Content": forms.Textarea(attrs={"class": "form-control", "rows": 5}    ),
            "ScoringCriteria": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "Prompt": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "IsOpen": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_Title(self):
        title = self.cleaned_data.get("Title")
        if not title:
            raise forms.ValidationError("标题不可为空。")
        return title


class EditPromptForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["Prompt"]
        widgets = {
            "Prompt": forms.Textarea(attrs={"class": "form-control", "rows": 20}),
        }

    def clean_Prompt(self):
        prompt = self.cleaned_data.get("Prompt")
        # if not prompt:
        #     raise forms.ValidationError("Prompt 不可为空。")
        return prompt


class CourseForm(ModelForm):
    class Meta:
        model = Course
        fields = ["Name", "Description"]
        widgets = {
            "Name": forms.TextInput(attrs={"class": "form-control"}),
            "Description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class QuestionForm(ModelForm):
    class Meta:
        model = Question
        fields = [
            "Title",
            "Content",
            "ScoringCriteria",
            "Prompt",
            "IsOpen",
        ]
        #    "OpenAt"]
        widgets = {
            "Title": forms.TextInput(attrs={"class": "form-control"}),
            "Content": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "ScoringCriteria": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "Prompt": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "IsOpen": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            # "OpenAt": forms.DateTimeInput(
            #     attrs={"class": "form-control", "type": "datetime-local"}
            # ),
        }


# 提交答案表单
class SubmitAnswerForm(forms.ModelForm):
    File = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "form-control-file"}),
    )  # File得到的是一个文件对象
    # 没有文件路径，文件路径是在服务器上的，不会传到客户端

    Content = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 10}),
    )  # Content得到的是一个字符串。rows表示文本框的行数，显示10行，如果内容超过10行，会自动滚动显示

    class Meta:  # 通过Meta类指定表单的元数据
        model = StudentAnswer  # 表单对应的模型：StudentAnswer
        fields = ["Content"]  # 表单包含的字段：Content

    def clean(self):
        cleaned_data = super().clean()  # 调用父类的clean方法，获取验证后的数据
        content = cleaned_data.get("Content")
        file = cleaned_data.get("File")

        # 验证逻辑：Content 和 File 至少提供一个，且不能同时提供
        if not content and not file:
            raise forms.ValidationError("请提交答案内容或上传文件。")
        if content and file:
            raise forms.ValidationError("请提交答案内容或上传文件，不能同时提交。")

        if file:  # 如果上传了文件，检查文件格式
            import os

            ext = os.path.splitext(file.name)[1].lower()
            if ext not in [".txt", ".md"]:
                raise forms.ValidationError("仅支持txt、markdown文档格式。")

        return cleaned_data

# 定义一个基于模型的表单：GradeAnswerForm
class GradeAnswerForm(forms.ModelForm):
    """
    这个表单用于评分和反馈的提交。
    它基于 ScoringFeedback 模型创建，并限制只操作 Score 和 Feedback 两个字段。
    """

    class Meta:
        """
        Meta 类用于配置 ModelForm 的基本属性：
        - model: 告诉这个表单是基于哪个模型生成的
        - fields: 指定需要包含在表单中的字段列表
        - widgets: 自定义每个字段对应的 HTML 小部件（如输入框、文本域等）
        """
        model = ScoringFeedback  # 使用自定义模型 ScoringFeedback
        fields = ["Score", "Feedback"]  # 只展示这两个字段

        # 自定义每个字段的前端显示方式（HTML 渲染效果）
        widgets = {
            # Score 字段使用 NumberInput 输入框
            "Score": forms.NumberInput(
                attrs={
                    "class": "form-control",  # Bootstrap 样式类名
                    "min": "0",               # 最小值为 0
                    "max": "200",             # 最大值为 200
                    "step": "0.1",            # 支持一位小数
                    "id": "id_Score",         # 显式设置 HTML ID
                }
            ),
            # Feedback 字段使用多行文本框 Textarea
            "Feedback": forms.Textarea(
                attrs={
                    "class": "form-control",   # Bootstrap 样式类
                    "rows": 5,                 # 默认显示五行
                    "id": "id_Feedback",       # 显式设置 HTML ID
                }
            ),
        }

    # 自定义字段验证方法：clean_Score()
    def clean_Score(self):
        """
        对 Score 字段进行额外的验证。
        虽然前端已经设置了 min 和 max，但后端仍需验证防止非法请求。

        如果分数不在 0~200 范围内，抛出 ValidationError 异常；
        否则返回清理后的数据。
        """
        score = self.cleaned_data.get("Score")  # 获取用户输入的分数

        # 判断是否为空或超出范围
        if score is not None and (score < 0 or score > 200):
            raise forms.ValidationError("分数必须在0到200之间。")

        return score  # 返回合法的分数值


# # 定义一个基于模型的表单：KnowledgeWeaknessAnalysisForm
# class KnowledgeWeaknessAnalysisForm(forms.ModelForm):
#     """
#     这个表单用于记录学生的薄弱知识点分析。
#     它基于 KnowledgeWeaknessAnalysis 模型创建，并允许选择或手动输入薄弱知识点。
#     """

#     class Meta:
#         """
#         Meta 类用于配置 ModelForm 的基本属性：
#         - model: 告诉这个表单是基于哪个模型生成的
#         - fields: 指定需要包含在表单中的字段列表
#         - widgets: 自定义每个字段对应的 HTML 小部件（如输入框、文本域等）
#         """
#         model = KnowledgeWeaknessAnalysis  # 使用自定义模型 KnowledgeWeaknessAnalysis
#         fields = ["feedback", "knowledge_point", "analysis_source", "suggested_resource"]  # 包含这些字段

#         # 自定义每个字段的前端显示方式（HTML 渲染效果）
#         widgets = {
#             # feedback 字段使用隐藏输入框，通常由视图逻辑设置
#             "feedback": forms.HiddenInput(),
#             # knowledge_point 字段使用 TextInput 输入框
#             "knowledge_point": forms.TextInput(
#                 attrs={
#                     "class": "form-control",  # Bootstrap 样式类名
#                     "placeholder": "请输入薄弱知识点名称",  # 占位符提示
#                     "id": "id_knowledge_point",  # 显式设置 HTML ID
#                 }
#             ),
#             # analysis_source 字段使用 Select 下拉菜单
#             "analysis_source": forms.Select(
#                 attrs={
#                     "class": "form-control",  # Bootstrap 样式类名
#                     "id": "id_analysis_source",  # 显式设置 HTML ID
#                 }
#             ),
#             # suggested_resource 字段使用 Textarea 多行文本框
#             "suggested_resource": forms.Textarea(
#                 attrs={
#                     "class": "form-control",  # Bootstrap 样式类名
#                     "rows": 3,  # 默认显示三行
#                     "placeholder": "请输入推荐的学习资源或练习题链接",  # 占位符提示
#                     "id": "id_suggested_resource",  # 显式设置 HTML ID
#                 }
#             ),
#         }

#         labels = {
#             'knowledge_point': '薄弱知识点',
#             'analysis_source': '分析来源',
#             'suggested_resource': '建议学习资源',
#         }

#         help_texts = {
#             'knowledge_point': '例如“函数定义域”、“牛顿第三定律”等。',
#             'suggested_resource': '可以是视频链接、文章链接或练习题目。',
#         }

#     def __init__(self, *args, **kwargs):
#         """
#         初始化方法，可以在这里预设一些值或动态调整字段选项。
#         """
#         super(KnowledgeWeaknessAnalysisForm, self).__init__(*args, **kwargs)
#         # 如果需要动态加载 feedback 选项，可以在此处处理
#         pass

#     # 可选：自定义验证逻辑
#     def clean_knowledge_point(self):
#         """
#         对 knowledge_point 字段进行额外的验证。
#         确保输入的内容不为空且符合预期格式。
#         """
#         knowledge_point = self.cleaned_data.get("knowledge_point")

#         if not knowledge_point.strip():
#             raise forms.ValidationError("薄弱知识点不能为空。")

#         return knowledge_point