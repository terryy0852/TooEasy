-- 简单SQL修复脚本：手动为Schumacherm2013分配作业
-- 执行此SQL语句即可解决问题

-- 1. 首先确认学生ID
SELECT id, username FROM users WHERE username = 'Schumacherm2013';

-- 2. 确认作业ID和状态  
SELECT id, title, status FROM assignments;

-- 3. 手动分配Math Homework (ID 1) 给 Schumacherm2013 (ID 3)
INSERT INTO student_assignments (student_id, assignment_id, status)
VALUES (3, 1, 'assigned');

-- 4. 验证分配结果
SELECT 
    u.username,
    a.title,
    a.status as assignment_status,
    sa.status as student_status
FROM student_assignments sa
JOIN users u ON sa.student_id = u.id
JOIN assignments a ON sa.assignment_id = a.id
WHERE u.username = 'Schumacherm2013';