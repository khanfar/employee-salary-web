import csv
from datetime import datetime
import re
import gradio as gr
import requests

# URL of the CSV file
CSV_URL = "https://huggingface.co/spaces/mhammad/Khanfar/raw/main/docs/your_data.csv"

def read_csv_from_url(url, start_date, end_date):
    mechanics_work = {}
    cash_amount = 0
    response = requests.get(url)
    lines = response.text.split("\n")
    reader = csv.DictReader(lines)
    for row in reader:
        if row['تقرير نهائي'] and 'شيكل' in row['تقرير نهائي']:
            try:
                entry_date = datetime.strptime(row['تاريخ الدخول'], '%d.%m.%Y')
            except ValueError:
                print(f"Error parsing date for row: {row}")
                continue

            if start_date <= entry_date <= end_date:
                mechanic = row['اسم الميكانيكي'].strip()  # Remove trailing spaces
                if mechanic in mechanics_work:
                    mechanics_work[mechanic]['job_count'] += 1
                    amount_str = row['تقرير نهائي']
                    amount = re.findall(r'(\d+(\.\d+)?) شيكل', amount_str)
                    if amount:
                        mechanics_work[mechanic]['total_money'] += float(amount[0][0])
                else:
                    mechanics_work[mechanic] = {'job_count': 1, 'total_money': 0}
                    amount_str = row['تقرير نهائي']
                    amount = re.findall(r'(\d+(\.\d+)?) شيكل', amount_str)
                    if amount:
                        mechanics_work[mechanic]['total_money'] = float(amount[0][0])

                # Check if رقم المركبة and نوع المركبه are both "كاش"
                if row['رقم المركبة'].strip() == 'كاش' and row['نوع المركبه'].strip() == 'كاش':
                    cash_amount += float(re.findall(r'(\d+(\.\d+)?) شيكل', row['تقرير نهائي'])[0][0])
    total_amount = sum(info['total_money'] for info in mechanics_work.values())
    return mechanics_work, total_amount

def start_processing(start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, '%d.%m.%Y')
    end_date = datetime.strptime(end_date_str, '%d.%m.%Y')

    work_by_date_range, total_amount = read_csv_from_url(CSV_URL, start_date, end_date)
    output_text = create_output_text(work_by_date_range, total_amount, start_date, end_date)
    
    return output_text

def create_output_text(data, total_amount, start_date, end_date):
    output = f'    ARAFAR JOB Calc. from date ({start_date.strftime("%d.%m.%Y")}) to date ({end_date.strftime("%d.%m.%Y")})\n'
    output += '#' * 70 + '\n'
    output += '-' * 50 + '\n'
    output += f'Total Amount: {total_amount} شيكل (Total Jobs: {sum(info["job_count"] for info in data.values())})\n'
    output += '-' * 50 + '\n'
    for mechanic, info in data.items():
        output += f'{mechanic}: {info["total_money"]} شيكل (Total Jobs: {info["job_count"]})\n'
        output += '-' * 50 + '\n'
    return output

output_text = gr.Textbox(label="Output")

iface = gr.Interface(
    fn=start_processing,
    inputs=[
        gr.Textbox(label="من تاريخ (dd.mm.yyyy)"),
        gr.Textbox(label="الى تاريخ (dd.mm.yyyy)")
    ],
    outputs=output_text,
    title="حاسبة العمل والموظفين",
    description="احسب العمل والموظفين في فترة معينة"
)

iface.launch()
