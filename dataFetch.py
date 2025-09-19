import sqlite3
import pandas as pd
from taipy.gui import Gui
import json
import os
port = int(os.environ.get("PORT", 5000))

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
            route TEXT,
            form_selected TEXT,
            unit_selected TEXT,
            frequency_selected TEXT,
            route_selected TEXT
        )
    """)
    cur.execute("SELECT COUNT(*) FROM data")
    forms = ["solution", "tablet", "syrup"]
    units = ["mL", "mG", "L"]
    frequencies = ["1r/day", "2r/day", "3r/day"]
    routes = ["intraven", "oral"]

    if cur.fetchone()[0] == 0:
        sample_data = [
            {
                "name": "Euphylini",
                "form": json.dumps(forms),
                "dosage": "10",
                "unit": json.dumps(units),
                "concentration": "2.4%",
                "frequency": json.dumps(frequencies),
                "duration": "NA",
                "route": json.dumps(routes),
                "form_selected": forms[0],
                "unit_selected": units[0],
                "frequency_selected": frequencies[0],
                "route_selected": routes[0]
            },
            {
                "name": "Morphin",
                "form": json.dumps(forms),
                "dosage": "5",
                "unit": json.dumps(units),
                "concentration": "5%",
                "frequency": json.dumps(frequencies),
                "duration": "3d",
                "route": json.dumps(routes),
                "form_selected": forms[0],
                "unit_selected": units[0],
                "frequency_selected": frequencies[0],
                "route_selected": routes[0]
            },
            {
                "name": "Paracetamol",
                "form": json.dumps(forms),
                "dosage": "20",
                "unit": json.dumps(units),
                "concentration": "1%",
                "frequency": json.dumps(frequencies),
                "duration": "5d",
                "route": json.dumps(routes),
                "form_selected": forms[0],
                "unit_selected": units[0],
                "frequency_selected": frequencies[0],
                "route_selected": routes[0]
            }
        ]
        for item in sample_data:
            cur.execute("""
                INSERT INTO data (name, form, dosage, unit, concentration, frequency, duration, route, form_selected, unit_selected, frequency_selected, route_selected)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item["name"], item["form"], item["dosage"], item["unit"],
                item["concentration"], item["frequency"], item["duration"], item["route"], item["form_selected"], 
                item["unit_selected"], item["frequency_selected"], item["route_selected"]
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
        "form": json.loads(row[2]),
        "dosage": row[3],
        "unit": json.loads(row[4]),
        "concentration": row[5],
        "frequency": json.loads(row[6]),
        "duration": row[7],
        "route": json.loads(row[8]),
        "form_selected": row[9],
        "unit_selected": row[10],
        "frequency_selected": row[11],
        "route_selected": row[12]
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
        "ID": row["id"],
        "Name": row["name"],
        "Form": row["form_selected"],
        "Dosage": row["dosage"],
        "Unit": row["unit_selected"],
        "Concentration": row["concentration"],
        "Frequency": row["frequency_selected"],
        "Duration": row["duration"],
        "Route": row["route_selected"]
    }])

df = load_row(curr_row_id)

row = get_row(curr_row_id)

forms_lov = row["form"]
units_lov = row["unit"]
freq_lov = row["frequency"]
routes_lov = row["route"]

def on_edit(state, var_name, payload):
    global curr_row_id
    idx, col, val = payload["index"], payload["col"], payload["value"]
    df_copy = getattr(state, var_name).copy()
    df_copy.loc[idx, col] = val
    state.assign(var_name, df_copy)

    col_map = {
    "Form": "form_selected",
    "Unit": "unit_selected",
    "Frequency": "frequency_selected",
    "Route": "route_selected",
    "Name": "name",
    "Dosage": "dosage",
    "Concentration": "concentration",
    "Duration": "duration"
    }
    db_col = col_map[col]

    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute(f"UPDATE data SET {db_col} = ? WHERE id = ?", (val, curr_row_id))
    con.commit()
    con.close()
item_count = f"{curr_row_id}/{total_rows}"
def update_id(state):
    global curr_row_id, total_rows
    state.item_count = f"{curr_row_id}/{total_rows}"


def prev_row(state):
    global curr_row_id, item_count, total_rows
    if curr_row_id > 1:
        curr_row_id -= 1
        state.df = load_row(curr_row_id)
        update_id(state)

def next_row(state):
    global curr_row_id, item_count, total_rows
    if curr_row_id < total_rows:
        curr_row_id += 1
        state.df = load_row(curr_row_id)
        update_id(state)

def add_row(state, var_name, payload):
    global curr_row_id, total_rows

    forms = ["solution", "tablet", "syrup"]
    units = ["mL", "mG", "L"]
    frequencies = ["1r/day", "2r/day", "3r/day"]
    routes = ["intraven", "oral"]

    new_row_data = {
        "name": "New Drug",
        "form": json.dumps(forms),
        "dosage": "",
        "unit": json.dumps(units),
        "concentration": "",
        "frequency": json.dumps(frequencies),
        "duration": "",
        "route": json.dumps(routes),
        "form_selected": forms[0],
        "unit_selected": units[0],
        "frequency_selected": frequencies[0],
        "route_selected": routes[0],
    }

    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("""
        INSERT INTO data 
        (name, form, dosage, unit, concentration, frequency, duration, route, 
        form_selected, unit_selected, frequency_selected, route_selected)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        new_row_data["name"], new_row_data["form"], new_row_data["dosage"], new_row_data["unit"],
        new_row_data["concentration"], new_row_data["frequency"], new_row_data["duration"], new_row_data["route"],
        new_row_data["form_selected"], new_row_data["unit_selected"], new_row_data["frequency_selected"], new_row_data["route_selected"]
    ))
    con.commit()

    new_id = cur.lastrowid
    con.close()
    total_rows += 1
    curr_row_id = new_id
    state.df = load_row(curr_row_id)
    update_id(state)

def del_row(state, var_name, payload):
    global curr_row_id, total_rows

    row_idx = payload["index"]
    row_id = int(state.df.loc[row_idx, "ID"])
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    cur.execute("DELETE FROM data WHERE id=?", (row_id,))
    con.commit()
    con.close()
    total_rows-=1

    if(curr_row_id>1): curr_row_id-=1
    else: curr_row_id=1

    if (total_rows>0):
        state.df = load_row(curr_row_id)
    else:
        state.df = pd.DataFrame()
    update_id(state)


user_text = "Sentiments two occasional affronting solicitude travelling and one contrasted. Fortune day out married parties. Happiness remainder joy but earnestly for off. Took sold add play may none him few. If as increasing contrasted entreaties be. Now summer who day looked our behind moment coming. Pain son rose more park way that. An stairs as be lovers uneasy."


def setClassCol(state, value, index, row, column_name):
    return "colWidth"

page ="""

<style>
    .colWidth{
        width:max-content;
    }
</style>

## Drugs Table — Plain Text Fields Only
<|{user_text}|input|multiline|rows=6|label=Raw drugs text|width=100%|>

<|{df}|table|lov[Form]={forms_lov}|lov[Unit]={units_lov}|lov[Frequency]={freq_lov}|lov[Route]={routes_lov}|editable|on_edit=on_edit|on_add=add_row|on_delete=del_row|show_all|width=100%|columns=Name;Form;Dosage;Unit;Concentration;Frequency;Duration;Route;|class_name=table|cell_class_name[Form]=setClassCol|size=medium|>

<|Previous|button|on_action=prev_row|> <|{item_count}|text|> <|Next|button|on_action=next_row|>
"""

Gui(page=page).run(run_browser=False, port=port, host="0.0.0.0", use_reloader=True)
