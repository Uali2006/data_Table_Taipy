import sqlite3
import pandas as pd
from taipy.gui import Gui

DB_NAME = "data.db"

def init_db():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            form TEXT,
            dosage TEXT,
            unit TEXT,
            concentration TEXT,
            frequency TEXT,
            duration TEXT,
            route TEXT
        )
    """)
    cur.execute("SELECT COUNT(*) FROM data")
    if cur.fetchone()[0] == 0:
        sample_data = [
            {
                "name": "Euphylini",
                "form": "solution",
                "dosage": "10",
                "unit": "mL",
                "concentration": "2.4%",
                "frequency": "1r/day",
                "duration": "NA",
                "route": "intraven"
            },
            {
                "name": "Morphin",
                "form": "tablet",
                "dosage": "5",
                "unit": "mg",
                "concentration": "5%",
                "frequency": "2r/day",
                "duration": "3d",
                "route": "oral"
            },
            {
                "name": "Paracetamol",
                "form": "syrup",
                "dosage": "20",
                "unit": "mg",
                "concentration": "1%",
                "frequency": "3r/day",
                "duration": "5d",
                "route": "oral"
            }
        ]
        for item in sample_data:
            cur.execute("""
                INSERT INTO data (name, form, dosage, unit, concentration, frequency, duration, route)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item["name"], item["form"], item["dosage"], item["unit"],
                item["concentration"], item["frequency"], item["duration"], item["route"]
            ))
        con.commit()
    con.close()

init_db()

def get_row(row_id):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("SELECT * FROM data WHERE id=?", (row_id,))
    row = cur.fetchone()
    con.close()
    if not row:
        return None
    return {
        "id": row[0],
        "name": row[1],
        "form": row[2],
        "dosage": row[3],
        "unit": row[4],
        "concentration": row[5],
        "frequency": row[6],
        "duration": row[7],
        "route": row[8]
    }

curr_row_id = 1
con = sqlite3.connect(DB_NAME)
total_rows = con.cursor().execute("SELECT COUNT(*) FROM data").fetchone()[0]
con.close()

def load_row(row_id):
    row = get_row(row_id)
    if not row:
        return pd.DataFrame()
    return pd.DataFrame([{
        "Name": row["name"],
        "Form": row["form"],
        "Dosage": row["dosage"],
        "Unit": row["unit"],
        "Concentration": row["concentration"],
        "Frequency": row["frequency"],
        "Duration": row["duration"],
        "Route": row["route"]
    }])

df = load_row(curr_row_id)

def on_edit(state, var_name, payload):
    global curr_row_id
    idx, col, val = payload["index"], payload["col"], payload["value"]
    df_copy = getattr(state, var_name).copy()
    df_copy.loc[idx, col] = val
    state.assign(var_name, df_copy)

    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute(f"UPDATE data SET {col.lower()} = ? WHERE id = ?", (val, curr_row_id))
    con.commit()
    con.close()

def prev_row(state):
    global curr_row_id
    if curr_row_id > 1:
        curr_row_id -= 1
        state.df = load_row(curr_row_id)

def next_row(state):
    global curr_row_id
    if curr_row_id < total_rows:
        curr_row_id += 1
        state.df = load_row(curr_row_id)


page = """
## Drugs Table — Plain Text Fields Only

<|{df}|table|editable|on_edit=on_edit|width=100%|>

<|Previous|button|on_action=prev_row|>  
<|Next|button|on_action=next_row|>
"""

Gui(page=page).run()
