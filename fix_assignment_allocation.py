import os
import psycopg2
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def fix_assignment_allocation():
    """手动为 Schumacherm2013 分配作业"""
    try:
        # 连接到生产数据库 - 使用正确的环境变量
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL 环境变量未设置")
            return
            
        print(f"🔗 连接到数据库: {database_url}")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("🔧 开始修复作业分配问题...")
        
        # 1. 检查学生是否存在
        cursor.execute("SELECT id, username FROM users WHERE username = %s", ('Schumacherm2013',))
        student = cursor.fetchone()
        if not student:
            print("❌ 学生 Schumacherm2013 不存在于数据库中")
            return
        
        student_id = student[0]
        print(f"✅ 找到学生: ID={student_id}, 用户名={student[1]}")
        
        # 2. 检查所有已发布的作业
        cursor.execute("SELECT id, title FROM assignments WHERE status = 'published'")
        published_assignments = cursor.fetchall()
        print(f"📋 已发布的作业总数: {len(published_assignments)}")
        
        if not published_assignments:
            print("❌ 没有已发布的作业可供分配")
            return
        
        # 3. 检查哪些作业已经分配
        cursor.execute("""
            SELECT a.id, a.title
            FROM assignments a
            LEFT JOIN student_assignments sa ON a.id = sa.assignment_id AND sa.student_id = %s
            WHERE a.status = 'published' AND sa.assignment_id IS NULL
        """, (student_id,))
        
        unallocated_assignments = cursor.fetchall()
        print(f"📊 需要分配的作业数量: {len(unallocated_assignments)}")
        
        if not unallocated_assignments:
            print("✅ 所有已发布的作业都已分配给该学生")
            return
        
        # 4. 分配作业
        assigned_count = 0
        for assignment in unallocated_assignments:
            assignment_id, title = assignment
            
            # 插入分配记录
            cursor.execute("""
                INSERT INTO student_assignments (student_id, assignment_id, status)
                VALUES (%s, %s, 'assigned')
            """, (student_id, assignment_id))
            
            assigned_count += 1
            print(f"✅ 已分配作业: {title} (ID: {assignment_id})")
        
        # 提交事务
        conn.commit()
        print(f"🎉 成功为 Schumacherm2013 分配了 {assigned_count} 个作业")
        
        # 5. 验证分配结果
        cursor.execute("""
            SELECT COUNT(*) 
            FROM student_assignments 
            WHERE student_id = %s
        """, (student_id,))
        
        total_assignments = cursor.fetchone()[0]
        print(f"📈 学生现在总共有 {total_assignments} 个分配的作业")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 修复过程中出现错误: {e}")
        if 'conn' in locals():
            conn.rollback()

if __name__ == "__main__":
    fix_assignment_allocation()