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

## 部署到 Render（包含修改密码功能）

本项目已包含用于 Render 部署的文件：
- `Procfile`：`web: gunicorn app:app --bind 0.0.0.0:$PORT`
- `requirements.txt`：包含 Flask、Flask-Login、Flask-Babel、Flask-SQLAlchemy、gunicorn 等依赖

### 1) 推送代码到 GitHub
在本机终端（PowerShell、Git Bash 或 IDE 终端）进入项目目录，并执行：

```bash
cd "d:\OD\OneDrive\BaiduSyncdisk\Learn\Project Easy\Python Programs\Too Easy"
# 如已是 Git 仓库，直接提交并推送
git add .
git commit -m "Change password feature + secure login"
git push origin <branch>

# 如果是第一次初始化（未配置仓库）
git init
git remote add origin https://github.com/<your-username>/<your-repo>.git
git branch -M main
git add .
git commit -m "Initial commit"
git push -u origin main
```

### 2) 在 Render 创建 Web Service
- 在 Render 仪表盘选择“New” → “Web Service”，连接你的 GitHub 仓库和分支。
- Build 命令：`pip install -r requirements.txt`
- Start 命令：使用 `Procfile`（Render 会自动识别），或显式设置 `gunicorn app:app --bind 0.0.0.0:$PORT`
- 环境变量：
  - `SECRET_KEY`：设置为强随机值（保持一致，避免会话失效）
  - 可选：`FLASK_ENV=production`

### 3) 部署后自测
- 访问 `/login`：
  - 老用户能登录，若旧密码为明文，将自动升级为安全哈希并保持登录。
  - 新用户正常注册与登录。
- 登录后访问 `/change_password`：
  - 输入当前密码、新密码、确认新密码。
  - 新密码需满足强度策略：至少 8 位，包含大小写、数字、特殊字符。
- 教师/学生仪表盘导航正常工作。

### 4) 常见问题
- 登录失败：
  - 检查 `SECRET_KEY` 是否已在 Render 环境中设置且不变更。
  - 查看 Render 日志定位错误。
- 页面缺失：
  - 登录后导航栏应显示“Change Password”链接。
- 数据在重新部署后清空：
  - 使用 SQLite 会出现这种情况；如需持久化数据，可以之后再迁移到 PostgreSQL。