# 多语言翻译系统说明

这个目录包含了作业管理系统的国际化翻译文件。

## 支持的语言
- 中文简体 (zh_CN) - 默认语言
- 英语 (en)
- 中文繁体 (zh_TW)

## 翻译文件结构
```
translations/
├── messages.pot       # 翻译模板文件
├── en/                # 英语翻译
│   └── LC_MESSAGES/
│       ├── messages.po  # 可编辑的翻译源文件
│       └── messages.mo  # 编译后的二进制文件（Flask-Babel使用）
└── zh_TW/             # 繁体中文翻译
    └── LC_MESSAGES/
        ├── messages.po  # 可编辑的翻译源文件
        └── messages.mo  # 编译后的二进制文件（Flask-Babel使用）
```

## 翻译流程

### 1. 提取翻译字符串
当添加新的需要翻译的文本时，需要从代码和模板中提取这些字符串：

```bash
# 注意：由于环境限制，我们使用了手动创建的模板文件
# 正常情况下应使用以下命令：
# pybabel extract -F .babelrc -k _ -o translations/messages.pot .
```

### 2. 更新或创建翻译文件
```bash
# 英语
# pybabel update -i translations/messages.pot -d translations -l en

# 繁体中文
# pybabel update -i translations/messages.pot -d translations -l zh_TW
```

### 3. 编辑翻译文件
手动编辑 `.po` 文件，添加或更新翻译内容。

### 4. 编译翻译文件
```bash
python compile_translations.py
```

## 修改现有翻译
如需修改现有翻译：
1. 编辑相应语言的 `.po` 文件
2. 运行编译脚本更新 `.mo` 文件

## 添加新语言
如需添加新语言支持：
1. 创建语言目录结构：`translations/[语言代码]/LC_MESSAGES/`
2. 复制 `.po` 文件并翻译内容
3. 编译成 `.mo` 文件
4. 在 `app.py` 中的 `BABEL_SUPPORTED_LOCALES` 配置中添加新语言代码

## 注意事项
- 所有在模板中显示的文本都应该使用 `{{ _('文本内容') }}` 包裹
- 所有在 Python 代码中显示的文本（如 flash 消息）都应该使用 `_('文本内容')` 包裹
- 翻译文件使用 UTF-8 编码