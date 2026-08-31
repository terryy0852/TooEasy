import os
from flask_babel import gettext

# This script is used to extract all translatable strings
# Run it before using pybabel to extract messages

# List of all translatable strings in the application
translations = [
    # Common terms
    _('作业管理系统'),
    _('登录'),
    _('注册'),
    _('退出登录'),
    _('仪表盘'),
    
    # Login page
    _('用户登录'),
    _('用户名'),
    _('密码'),
    _('还没有账号？'),
    _('立即注册'),
    _('忘记密码？'),
    _('重置密码'),
    
    # Register page
    _('用户注册'),
    _('邮箱'),
    _('我是教师'),
    _('已有账号？'),
    _('立即登录'),
    
    # Tutor dashboard
    _('教师仪表盘'),
    _('创建新作业'),
    _('我的作业'),
    _('下载文件'),
    _('查看提交'),
    _('您还没有创建任何作业'),
    _('创建第一个作业'),
    
    # Create assignment
    _('创建作业'),
    _('作业标题'),
    _('作业描述'),
    _('上传文件（可选）'),
    _('支持的格式：txt, pdf, doc, docx, xls, xlsx, ppt, pptx, zip'),
    _('截止日期（可选）'),
    _('创建作业'),
    _('取消'),
    
    # View submissions
    _('查看提交'),
    _('返回仪表盘'),
    _('学生'),
    _('提交时间'),
    _('文件'),
    _('评分状态'),
    _('操作'),
    _('下载'),
    _('已评分'),
    _('未评分'),
    _('修改评分'),
    _('评分'),
    _('还没有学生提交此作业'),
    
    # Grade submission
    _('评分'),
    _('返回提交列表'),
    _('学生信息'),
    _('学生姓名'),
    _('提交文件'),
    _('分数'),
    _('反馈'),
    _('保存评分'),
    
    # Student dashboard
    _('学生仪表盘'),
    _('可用作业'),
    _('已提交'),
    _('发布者'),
    _('截止日期'),
    _('发布时间'),
    _('查看详情'),
    _('开始作业'),
    _('当前没有可用的作业'),
    
    # View assignment
    _('返回仪表盘'),
    _('提交状态'),
    _('教师尚未评分'),
    _('提交作业'),
    _('上传作业文件'),
    _('提交作业'),
    
    # Flash messages
    _('Invalid username or password'),
    _('Username already exists'),
    _('Email already exists'),
    _('Registration successful! Please login.'),
    _('You are not authorized to access this page'),
    _('Assignment created successfully!'),
    _('You are not authorized to view these submissions'),
    _('You are not authorized to grade this submission'),
    _('Submission graded successfully!'),
    _('You have already submitted this assignment'),
    _('No file part'),
    _('No selected file'),
    _('Assignment submitted successfully!'),
    _('Invalid file type')
]

if __name__ == '__main__':
    print("Translation strings have been defined.")
    print("Run the following commands to extract and compile translations:")
    print("pybabel extract -F .babelrc -k _l -o translations/messages.pot .")
    print("pybabel init -i translations/messages.pot -d translations -l en")
    print("pybabel init -i translations/messages.pot -d translations -l zh_TW")
    print("pybabel compile -d translations")