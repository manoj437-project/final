import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))
from app.database import engine  # type: ignore[import]
from sqlalchemy import text

with engine.connect() as conn:
    # Show current subjects in weekly_timetables
    result = conn.execute(text('SELECT DISTINCT subject FROM weekly_timetables'))
    subjects = [row[0] for row in result.fetchall()]
    print('Current subjects in weekly_timetables:', subjects)

    result2 = conn.execute(text('SELECT DISTINCT subject FROM daily_topics'))
    subjects2 = [row[0] for row in result2.fetchall()]
    print('Current subjects in daily_topics:', subjects2)

    # Mapping: pattern (lowercased start) -> correct name
    fixes = [
        ('software eng', 'Software Engineering'),
        ('advance comp', 'Computer Networks'),
        ('advance computer', 'Computer Networks'),
        ('linear alg', 'Engineering Mathematics II'),
    ]

    for prefix, correct in fixes:
        r1 = conn.execute(text(
            "UPDATE weekly_timetables SET subject=:correct WHERE LOWER(subject) LIKE :pattern"
        ), {'correct': correct, 'pattern': prefix + '%'})
        if r1.rowcount:
            print(f'weekly_timetables: fixed "{prefix}*" -> "{correct}" ({r1.rowcount} rows)')

        r2 = conn.execute(text(
            "UPDATE daily_topics SET subject=:correct WHERE LOWER(subject) LIKE :pattern"
        ), {'correct': correct, 'pattern': prefix + '%'})
        if r2.rowcount:
            print(f'daily_topics: fixed "{prefix}*" -> "{correct}" ({r2.rowcount} rows)')

    conn.commit()

print('\nDone!')
