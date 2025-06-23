WITH recap AS (
    SELECT
        v.user_id,
        co.course_title,
        co.course_id,
        t.teacher_id,
        t.first_name,
        t.last_name,
        SUM(v.watched_seconds) AS watched_seconds_total
    FROM view v
    INNER JOIN schedule sc ON v.schedule_id = sc.schedule_id
    INNER JOIN course co ON sc.course_id = co.course_id
    INNER JOIN teacher t ON sc.teacher_id = t.teacher_id
    GROUP BY
        v.user_id,
        co.course_title,
        co.course_id,
        t.teacher_id,
        t.first_name,
        t.last_name
),
ranked_courses AS (
    SELECT 
        user_id,
        watched_seconds_total,
        course_id,
        course_title,
        teacher_id,
        last_name,
        first_name,
        ROW_NUMBER() OVER (
            PARTITION BY user_id 
            ORDER BY watched_seconds_total DESC
        ) AS row_num
    FROM recap
),
top_course_per_user AS (
    SELECT * FROM ranked_courses WHERE row_num = 1
),
subscription_summary AS (
    SELECT 
        user_id,
        SUM(price) AS total_paid
    FROM sub
    GROUP BY user_id
),
watch_summary AS (
    SELECT 
        user_id,
        SUM(watched_seconds) AS total_watched_seconds
    FROM view
    GROUP BY user_id
)
SELECT
    r.user_id,
    u.gender AS genre,
    u.department_code,
    u.birthdate,
    t.course_id AS top_course_id,
    t.course_title AS top_course_title,
    t.teacher_id AS top_teacher_id,
    t.first_name AS top_teacher_first_name,
    t.last_name AS top_teacher_last_name,
    TIMESTAMPDIFF(YEAR, u.birthdate, CURDATE()) AS age,
    COALESCE(v.total_watched_seconds, 0) AS total_watched_seconds,
    CASE 
        WHEN r.total_paid = 0 THEN 0
        ELSE 1
    END AS has_paid_subscription
FROM subscription_summary r
INNER JOIN user u ON r.user_id = u.user_id
INNER JOIN watch_summary v ON r.user_id = v.user_id
INNER JOIN top_course_per_user t ON r.user_id = t.user_id;