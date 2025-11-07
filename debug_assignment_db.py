import os
import psycopg2
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def check_assignment_allocation():
    """检查学生作业分配情况"""
    try:
        # 连接到生产数据库
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = conn.cursor()
        
        print("🔍 检查学生 Schumacherm2013 的作业分配情况...")
        
        # 1. 检查学生是否存在
        cursor.execute("SELECT id, username FROM users WHERE username = %s", ('Schumacherm2013',))
        student = cursor.fetchone()
        if not student:
            print("❌ 学生 Schumacherm2013 不存在于数据库中")
            return
        
        student_id = student[0]
        print(f"✅ 找到学生: ID={student_id}, 用户名={student[1]}")
        
        # 2. 检查所有作业
        cursor.execute("SELECT id, title, status, deadline FROM assignments")
        assignments = cursor.fetchall()
        print(f"📋 数据库中的作业总数: {len(assignments)}")
        
        if assignments:
            print("\n📝 所有作业列表:")
            for assignment in assignments:
                print(f"  - ID: {assignment[0]}, 标题: {assignment[1]}, 状态: {assignment[2]}, 截止日期: {assignment[3]}")
        
        # 3. 检查作业分配
        cursor.execute("""
            SELECT a.id, a.title, a.status, a.deadline, sa.status as student_status
            FROM assignments a
            LEFT JOIN student_assignments sa ON a.id = sa.assignment_id AND sa.student_id = %s
            ORDER BY a.deadline
        """, (student_id,))
        
        allocated_assignments = cursor.fetchall()
        print(f"\n🎯 学生 Schumacherm2013 的作业分配情况:")
        
        if allocated_assignments:
            for assignment in allocated_assignments:
                assignment_id, title, status, deadline, student_status = assignment
                allocation_status = "已分配" if student_status else "未分配"
                print(f"  - {title} (ID: {assignment_id}): {allocation_status}, 作业状态: {status}, 学生状态: {student_status}")
        else:
            print("  ❌ 没有找到任何作业分配记录")
        
        # 4. 检查是否有已发布但未分配的作业
        cursor.execute("""
            SELECT a.id, a.title, a.deadline
            FROM assignments a
            WHERE a.status = 'published'
            AND a.id NOT IN (
                SELECT assignment_id 
                FROM student_assignments 
                WHERE student_id = %s
            )
        """, (student_id,))
        
        unallocated_published = cursor.fetchall()
        print(f"\n📊 已发布但未分配给该学生的作业: {len(unallocated_published)}")
        
        if unallocated_published:
            for assignment in unallocated_published:
                print(f"  - {assignment[1]} (ID: {assignment[0]}), 截止日期: {assignment[2]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 数据库连接错误: {e}")

if __name__ == "__main__":
    check_assignment_allocation()