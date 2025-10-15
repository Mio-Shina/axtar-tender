import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import datetime

TEXT_LIMIT = 65000

def safe_append(data_dict, key, value):
    """Добавляем обрезанное значение в словарь"""
    if value is None:
        value = 'Yoxdur'
    elif isinstance(value, str):
        value = value[:TEXT_LIMIT]
    else:
        value = str(value)[:TEXT_LIMIT]
    data_dict[key].append(value)

main_data = {
    'event_id': [], 'event_number': [], 'organization_name': [], 'organization_voen': [], 'organization_address': [],
    'event_name': [], 'classification_code': [], 'suggested_price': [], 'event_start_date': [], 'submission_deadline': [],
    'envelope_opening_date': [], 'participation_fee': [], 'participation_description': [], 'usage_fee': [], 
    'usage_description': [], 'full_name': [], 'contact': [], 'position': [], 'phone_number': [],
    'detail_name': [], 'detail_description': [], 'detail_cat_code': [], 'detailed': []
}

API_REQUEST_DELAY = 2

def try_request(url):
    """Простая обертка requests.get без прокси"""
    try:
        resp = requests.get(url, timeout=25)
        if resp.status_code == 200:
            return resp
    except Exception:
        pass
    return None

def get_total_items_from_link(api_link=None):
    if not api_link:
        api_link = ('https://etender.gov.az/api/events?EventType=2&PageSize=1&PageNumber=1&'
                    'EventStatus=1&Keyword=&buyerOrganizationName=&PrivateRfxId=&publishDateFrom=&'
                    'publishDateTo=&AwardedparticipantName=&AwardedparticipantVoen=&DocumentViewType=')
    resp = try_request(api_link)
    if resp:
        return resp.json().get('totalItems', -1)
    return -1

def get_total_items_from_id(id):
    template = f'https://etender.gov.az/api/events/{id}/bomLines?PageSize=1&PageNumber=1'
    resp = try_request(template)
    if resp:
        return resp.json().get('totalItems', -1)
    return -1

def get_all_events_ids(page_size):
    template = f'https://etender.gov.az/api/events?EventType=2&PageSize={page_size}&PageNumber=1&EventStatus=1'
    resp = try_request(template)
    if resp:
        return sorted([item.get('eventId') for item in resp.json().get('items', [])], reverse=True)
    return []

def get_main_data_from_link_requests(ids):
    for id in ids:
        api_link = f'https://etender.gov.az/api/events/{id}'
        resp = try_request(api_link)
        time.sleep(API_REQUEST_DELAY)
        if resp:
            resp_json = resp.json()
            safe_append(main_data, 'event_id', resp_json.get('id'))
            safe_append(main_data, 'event_number', resp_json.get('rfxId'))
            safe_append(main_data, 'organization_name', resp_json.get('organizationName'))
            safe_append(main_data, 'organization_voen', resp_json.get('organizationVoen'))
            safe_append(main_data, 'organization_address', resp_json.get('address'))
            safe_append(main_data, 'event_name', resp_json.get('tenderName'))
            safe_append(main_data, 'suggested_price', str(resp_json.get('estimatedAmount')) if resp_json.get('estimatedAmount') else 'Yoxdur')
            category_codes = resp_json.get('categoryCodes', [])
            classification_code = category_codes[0] if category_codes else (str(resp_json.get('cpvCode')) if resp_json.get('cpvCode') else 'Yoxdur')
            safe_append(main_data, 'classification_code', classification_code)
            safe_append(main_data, 'event_start_date',
                        (datetime.datetime.fromtimestamp(resp_json['publishDate']) - datetime.timedelta(hours=4)).strftime('%Y-%m-%d %H:%M') 
                        if resp_json.get('publishDate') else 'Yoxdur')
            safe_append(main_data, 'submission_deadline',
                        (datetime.datetime.fromtimestamp(resp_json['endDate']) - datetime.timedelta(hours=4)).strftime('%Y-%m-%d %H:%M') 
                        if resp_json.get('endDate') else 'Yoxdur')
            safe_append(main_data, 'envelope_opening_date',
                        (datetime.datetime.fromtimestamp(resp_json['envelopeDate']) - datetime.timedelta(hours=4)).strftime('%Y-%m-%d %H:%M') 
                        if resp_json.get('envelopeDate') else 'Yoxdur')
        else:
            for key in main_data.keys():
                safe_append(main_data, key, 'Yoxdur')

def get_fees(ids):
    for id in ids:
        template = f'https://etender.gov.az/api/events/{id}/info'
        resp = try_request(template)
        time.sleep(API_REQUEST_DELAY)
        if resp:
            resp_json = resp.json()
            safe_append(main_data, 'participation_fee', resp_json.get('participationFee'))
            safe_append(main_data, 'usage_fee', resp_json.get('viewFee'))
        else:
            safe_append(main_data, 'participation_fee', 'Yoxdur')
            safe_append(main_data, 'usage_fee', 'Yoxdur')

def get_contact(ids):
    for id in ids:
        api_link = f'https://etender.gov.az/api/events/{id}/contact-persons'
        resp = try_request(api_link)
        time.sleep(API_REQUEST_DELAY)
        if resp and resp.json():
            resp_json = resp.json()[0]
            safe_append(main_data, 'full_name', resp_json.get('fullName'))
            safe_append(main_data, 'contact', resp_json.get('contact'))
            safe_append(main_data, 'position', resp_json.get('position'))
            safe_append(main_data, 'phone_number', resp_json.get('phoneNumber'))
        else:
            safe_append(main_data, 'full_name', 'Yoxdur')
            safe_append(main_data, 'contact', 'Yoxdur')
            safe_append(main_data, 'position', 'Yoxdur')
            safe_append(main_data, 'phone_number', 'Yoxdur')

def get_fees_descriptions(ids):
    link = 'https://etender.gov.az/assets/i18n/az.json'
    for _ in range(len(ids)):
        resp = try_request(link)
        time.sleep(API_REQUEST_DELAY)
        if resp:
            resp_json = resp.json()
            safe_append(main_data, 'participation_description', resp_json.get('Participation fee description new'))
            safe_append(main_data, 'usage_description', resp_json.get('View fee description'))
        else:
            safe_append(main_data, 'participation_description', 'Yoxdur')
            safe_append(main_data, 'usage_description', 'Yoxdur')

def get_links_detailed(ids):
    for id in ids:
        safe_append(main_data, 'detailed', f'https://etender.gov.az/main/competition/detail/{id}')

def get_tables_info(ids):
    for id in ids:
        items_amount = get_total_items_from_id(id=id)
        link = f'https://etender.gov.az/api/events/{id}/bomLines?PageSize={items_amount}&PageNumber=1'
        resp = try_request(link)
        time.sleep(API_REQUEST_DELAY)
        if resp:
            resp_json = resp.json()
            items = resp_json.get('items', [])
            if items:
                safe_append(main_data, 'detail_name', items[0].get('name'))
                stringline = ' '.join(item.get('description', '') for item in items).strip()
                safe_append(main_data, 'detail_description', stringline)
                safe_append(main_data, 'detail_cat_code', items[0].get('categoryCode'))
            else:
                safe_append(main_data, 'detail_name', 'Yoxdur')
                safe_append(main_data, 'detail_description', 'Yoxdur')
                safe_append(main_data, 'detail_cat_code', 'Yoxdur')
        else:
            safe_append(main_data, 'detail_name', 'Yoxdur')
            safe_append(main_data, 'detail_description', 'Yoxdur')
            safe_append(main_data, 'detail_cat_code', 'Yoxdur')
        print(f"[LOG] Tender {id} processed")

def fetch_data(ids):
    chunk_size = 50
    id_chunks = [ids[i:i + chunk_size] for i in range(0, len(ids), chunk_size)]
    for chunk in id_chunks:
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(get_main_data_from_link_requests, chunk),
                executor.submit(get_fees, chunk),
                executor.submit(get_contact, chunk),
                executor.submit(get_links_detailed, chunk),
                executor.submit(get_fees_descriptions, chunk),
                executor.submit(get_tables_info, chunk)
            ]
            for future in as_completed(futures):
                future.result()
                time.sleep(1)
    print('Done')
