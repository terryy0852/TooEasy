# 作业管理系统

这是一个基于 Flask 的作业管理系统，允许教师上传作业，学生查看并提交作业，教师评分并提供反馈。

## 功能特性

### 教师功能：
1. 创建和管理作业
2. 上传作业材料
3. 查看学生提交的作业
4. 为作业评分并提供反馈

### 学生功能：
1. 查看可用作业
2. 下载作业材料
3. 提交完成的作业
4. 查看教师评分和反馈

## 技术栈
- Python 3
- Flask
- Flask-SQLAlchemy（数据库）
- Flask-Login（用户认证）
- SQLite（数据库）

## 安装和运行

### 1. 安装依赖

首先，确保您已经安装了 Python 3。然后，运行以下命令安装所需的依赖：

```bash
pip install -r requirements.txt
```

### 2. 运行应用

使用以下命令启动应用：

```bash
python app.py
```

应用将在 http://localhost:5000/ 启动。

### 3. 使用说明

1. 打开浏览器，访问 http://localhost:5000/
2. 注册一个账号（可以选择教师或学生身份）
3. 登录系统
4. 根据您的身份使用相应的功能：
   - 教师：创建作业、查看学生提交、评分
   - 学生：查看作业、提交作业、查看评分

## 注意事项

- 这是一个简易的示例应用，在实际生产环境中，应添加更多的安全措施，如密码加密存储、更强的文件类型验证等
- 文件将保存在 `uploads` 目录中
- 数据存储在 SQLite 数据库 `assignments.db` 中

## 项目结构
```
app.py                 # 主应用文件
requirements.txt       # 依赖列表
README.md              # 项目说明
uploads/               # 上传文件存储目录
templates/             # HTML 模板
  base.html            # 基础模板
  login.html           # 登录页面
  register.html        # 注册页面
  tutor_dashboard.html # 教师仪表盘
  create_assignment.html # 创建作业页面
  view_submissions.html # 查看提交页面
  grade_submission.html # 评分页面
  student_dashboard.html # 学生仪表盘
  view_assignment.html # 作业详情页面
```