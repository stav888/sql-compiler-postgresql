-- Window functions example
SELECT 
    department,
    employee_name,
    salary,
    AVG(salary) OVER (PARTITION BY department) as dept_avg_salary,
    RANK() OVER (
        PARTITION BY department 
        ORDER BY salary DESC
    ) as salary_rank,
    LAG(salary, 1) OVER (
        PARTITION BY department 
        ORDER BY hire_date
    ) as prev_hire_salary,
    SUM(salary) OVER (
        ORDER BY hire_date 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) as running_total
FROM employees
WHERE active = TRUE
ORDER BY department, salary_rank;