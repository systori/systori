import json, psycopg2
from decimal import Decimal

con = psycopg2.connect("dbname=systori_backup")
c = con.cursor()
c.execute('set search_path to "mehr-handwerk", public;')


def append_all():
    items = []
    for row in c.fetchall():
        if not row[1]:
            continue
        if len(str(row[1]).split(".")[1].rstrip("0")) > 2:
            items.append((row[0], str(row[1].quantize(Decimal("0.001")))))
    return items


c.execute("select id, qty from task_lineitem;")
lineitems = append_all()
c.execute("select id, qty from task_task;")
tasks = append_all()
c.execute("select id, complete from task_progressreport;")
progress = append_all()

with open("qty.json", "w") as f:
    f.write(json.dumps({"lineitems": lineitems, "tasks": tasks, "progress": progress}))
