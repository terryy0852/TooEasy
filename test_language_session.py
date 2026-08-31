from flask import Flask, session, redirect, url_for, request
from app import app

# 配置测试客户端
app.config['TESTING'] = True
test_client = app.test_client()

# 创建一个简单的测试路由来检查当前语言
def setup_test_route():
    @app.route('/test_language')
    def test_language():
        # 这个函数会返回当前语言设置
        lang = request.args.get('lang')
        if lang:
            return f"URL参数语言: {lang}\n"
        if 'lang' in session:
            return f"会话语言: {session['lang']}\n"
        return f"默认语言: {app.config['BABEL_DEFAULT_LOCALE']}\n"

    return test_language


def test_language_session_persistence():
    # 设置测试路由
    setup_test_route()
    
    print("===== 测试语言会话持久性 =====")
    
    # 测试1: 初始访问 - 应该使用默认语言
    print("\n测试1: 初始访问")
    response = test_client.get('/test_language')
    print(f"响应: {response.data.decode('utf-8').strip()}")
    
    # 测试2: 切换到英文
    print("\n测试2: 切换到英文")
    with test_client as c:
        # 模拟访问语言切换路由
        response = c.get('/switch_language/en', follow_redirects=True)
        
        # 检查会话中的语言值
        with c.session_transaction() as sess:
            session_lang = sess.get('lang', '未设置')
            print(f"会话中的语言: {session_lang}")
        
        # 通过测试路由检查语言
        response = c.get('/test_language')
        print(f"测试路由响应: {response.data.decode('utf-8').strip()}")
    
    # 测试3: 切换到繁体中文
    print("\n测试3: 切换到繁体中文")
    with test_client as c:
        response = c.get('/switch_language/zh_TW', follow_redirects=True)
        
        with c.session_transaction() as sess:
            session_lang = sess.get('lang', '未设置')
            print(f"会话中的语言: {session_lang}")
        
        response = c.get('/test_language')
        print(f"测试路由响应: {response.data.decode('utf-8').strip()}")
    
    # 测试4: 验证跨请求的持久性
    print("\n测试4: 跨请求的语言持久性")
    with test_client as c:
        # 先设置语言
        c.get('/switch_language/en', follow_redirects=True)
        
        # 访问其他页面
        c.get('/login')
        
        # 检查语言是否保持
        with c.session_transaction() as sess:
            session_lang = sess.get('lang', '未设置')
            print(f"访问其他页面后会话中的语言: {session_lang}")
        
        response = c.get('/test_language')
        print(f"测试路由响应: {response.data.decode('utf-8').strip()}")
    
    # 测试5: 带URL参数的语言切换
    print("\n测试5: 带URL参数的语言切换")
    response = test_client.get('/test_language?lang=zh_CN')
    print(f"带URL参数的响应: {response.data.decode('utf-8').strip()}")
    
    print("\n===== 测试完成 =====")
    print("如果所有测试中的语言值都正确设置，则语言切换功能已修复。")
    print("在实际浏览器中，您应该能够通过点击语言按钮切换界面语言。")

if __name__ == "__main__":
    test_language_session_persistence()