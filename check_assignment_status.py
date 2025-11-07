import os
import psycopg2

def check_assignment_status():
    """检查Schumacherm2013的作业分配状态"""
    try:
        # 使用生产数据库URL
        database_url = "postgresql://postgres:n5jTtilYoz2S1LwO@db.xqjscxsvcespsrkyoekf.supabase.co:5432/postgres"
            
        print(f"🔗 连接到数据库: {database_url}")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("🔍 检查Schumacherm2013的作业分配状态...")
        
        # 1. 检查学生是否存在
        cursor.execute("SELECT id, username FROM users WHERE username = %s", ('Schumacherm2013',))
        student = cursor.fetchone()
        if not student:
            print("❌ 学生Schumacherm2013不存在于数据库中")
            return
        
        student_id = student[0]
        print(f"✅ 找到学生: ID={student_id}, 用户名={student[1]}")
        
        # 2. 检查作业分配情况
        cursor.execute("""
            SELECT 
                a.id, 
                a.title, 
                a.status as assignment_status,
                sa.status as student_status,
                sa.created_at as assigned_date
            FROM student_assignments sa
            RIGHT JOIN assignments a ON sa.assignment_id = a.id AND sa.student_id = %s
            ORDER BY a.id
        """, (student_id,))
        
        assignments = cursor.fetchall()
        
        print(f"\n📊 Schumacherm2013的作业分配状态:")
        print("=" * 60)
        
        if assignments:
            for assignment in assignments:
                assignment_id, title, assignment_status, student_status, assigned_date = assignment
                if student_status:
                    print(f"✅ 已分配: {title} (ID: {assignment_id})")
                    print(f"   作业状态: {assignment_status}, 学生状态: {student_status}")
                    if assigned_date:
                        print(f"   分配时间: {assigned_date}")
                else:
                    print(f"❌ 未分配: {title} (ID: {assignment_id})")
                    print(f"   作业状态: {assignment_status}")
                print("-" * 40)
        else:
            print("❌ 数据库中没有找到任何作业记录")
        
        # 3. 统计分配数量
        cursor.execute("SELECT COUNT(*) FROM student_assignments WHERE student_id = %s", (student_id,))
        assigned_count = cursor.fetchone()[0]
        print(f"📈 总共分配给该学生的作业数量: {assigned_count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 检查过程中出现错误: {e}")

if __name__ == "__main__":
    check_assignment_status()