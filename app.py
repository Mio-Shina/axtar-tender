from flask import Flask, request, render_template, jsonify
import mysql.connector
from config import *
from scrapper import *
import threading
import time
import os

TEXT_LIMIT = 65000

def safe_value(val):
    if val is None:
        return 'Yoxdur'
    val_bytes = str(val).encode("utf-8")
    return val_bytes[:TEXT_LIMIT].decode("utf-8", errors="ignore")

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )

def get_current_tenders_ids():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT event_id FROM events")
    current_ids = [id_[0] for id_ in cursor.fetchall()]
    cursor.close()
    conn.close()
    return current_ids

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search_results', methods=['GET'])
def search_some_columns():
    search_query = request.args.get('query', '').lower()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SHOW COLUMNS FROM events")
    columns = [col[0] for col in cursor.fetchall()]

    search_conditions = " OR ".join([f"LOWER({col}) LIKE %s" for col in columns])
    params = ['%' + search_query + '%'] * len(columns)
    cursor.execute(f"SELECT * FROM events WHERE {search_conditions}", params)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('search_results.html', results=results, column_names=columns)

@app.route('/update_data', methods=['GET'])
def update_data():
    try:
        all_ids = sorted(get_all_events_ids(get_total_items_from_link()), reverse=True)
        current_ids = set(get_current_tenders_ids())
        to_delete = current_ids - set(all_ids)
        if to_delete:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.executemany("DELETE FROM events WHERE event_id = %s", [(id_,) for id_ in to_delete])
            conn.commit()
            cursor.close()
            conn.close()

        new_ids = [id_ for id_ in all_ids if id_ not in current_ids]
        if new_ids:
            fetch_data(new_ids)
            conn = get_db_connection()
            cursor = conn.cursor()
            insert_query = '''
                INSERT INTO events (event_id, event_number, organization_name, organization_voen, organization_address, event_name,
                classification_code, suggested_price, event_start_date, submission_deadline, envelope_opening_date, participation_fee,
                participation_description, usage_fee, usage_description, full_name, contact, position, phone_number,
                detail_name, detail_description, detail_cat_code, detailed)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            for data in zip(
                main_data['event_id'][-len(new_ids):],
                main_data['event_number'][-len(new_ids):],
                main_data['organization_name'][-len(new_ids):],
                main_data['organization_voen'][-len(new_ids):],
                main_data['organization_address'][-len(new_ids):],
                main_data['event_name'][-len(new_ids):],
                main_data['classification_code'][-len(new_ids):],
                main_data['suggested_price'][-len(new_ids):],
                main_data['event_start_date'][-len(new_ids):],
                main_data['submission_deadline'][-len(new_ids):],
                main_data['envelope_opening_date'][-len(new_ids):],
                main_data['participation_fee'][-len(new_ids):],
                main_data['participation_description'][-len(new_ids):],
                main_data['usage_fee'][-len(new_ids):],
                main_data['usage_description'][-len(new_ids):],
                main_data['full_name'][-len(new_ids):],
                main_data['contact'][-len(new_ids):],
                main_data['position'][-len(new_ids):],
                main_data['phone_number'][-len(new_ids):],
                main_data['detail_name'][-len(new_ids):],
                main_data['detail_description'][-len(new_ids):],
                main_data['detail_cat_code'][-len(new_ids):],
                main_data['detailed'][-len(new_ids):]
            ):
                cursor.execute(insert_query, tuple(safe_value(d) for d in data))
            conn.commit()
            cursor.close()
            conn.close()
        return jsonify(success=True, message="Məlumat uğurla əlavə edildi!")
    except Exception as e:
        return jsonify(success=False, message=f"Xəta baş verdi: {e}")

def auto_update():
    UPDATE_INTERVAL = 10 * 60
    while True:
        try:
            all_ids = sorted(get_all_events_ids(get_total_items_from_link()), reverse=True)
            current_ids = set(get_current_tenders_ids())
            new_ids = [id_ for id_ in all_ids if id_ not in current_ids]
            if new_ids:
                fetch_data(new_ids)
                conn = get_db_connection()
                cursor = conn.cursor()
                insert_query = '''
                    INSERT INTO events (event_id, event_number, organization_name, organization_voen, organization_address, event_name,
                    classification_code, suggested_price, event_start_date, submission_deadline, envelope_opening_date, participation_fee,
                    participation_description, usage_fee, usage_description, full_name, contact, position, phone_number,
                    detail_name, detail_description, detail_cat_code, detailed)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                '''
                for data in zip(
                    main_data['event_id'][-len(new_ids):],
                    main_data['event_number'][-len(new_ids):],
                    main_data['organization_name'][-len(new_ids):],
                    main_data['organization_voen'][-len(new_ids):],
                    main_data['organization_address'][-len(new_ids):],
                    main_data['event_name'][-len(new_ids):],
                    main_data['classification_code'][-len(new_ids):],
                    main_data['suggested_price'][-len(new_ids):],
                    main_data['event_start_date'][-len(new_ids):],
                    main_data['submission_deadline'][-len(new_ids):],
                    main_data['envelope_opening_date'][-len(new_ids):],
                    main_data['participation_fee'][-len(new_ids):],
                    main_data['participation_description'][-len(new_ids):],
                    main_data['usage_fee'][-len(new_ids):],
                    main_data['usage_description'][-len(new_ids):],
                    main_data['full_name'][-len(new_ids):],
                    main_data['contact'][-len(new_ids):],
                    main_data['position'][-len(new_ids):],
                    main_data['phone_number'][-len(new_ids):],
                    main_data['detail_name'][-len(new_ids):],
                    main_data['detail_description'][-len(new_ids):],
                    main_data['detail_cat_code'][-len(new_ids):],
                    main_data['detailed'][-len(new_ids):]
                ):
                    cursor.execute(insert_query, tuple(safe_value(d) for d in data))
                conn.commit()
                cursor.close()
                conn.close()
        except Exception as e:
            print(f"[BG ERROR] {e}")
        time.sleep(UPDATE_INTERVAL)

threading.Thread(target=auto_update, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
