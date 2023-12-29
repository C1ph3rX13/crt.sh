# -*- coding: utf-8 -*-
import argparse
import json
import re
from datetime import datetime

import httpx
import pandas as pd

PROXIES = {}


def banner():
    print('''
     ▄▄· ▄▄▄  ▄▄▄▄▄   .▄▄ ·  ▄ .▄
    ▐█ ▌▪▀▄ █·•██     ▐█ ▀. ██▪▐█
    ██ ▄▄▐▀▀▄  ▐█.▪   ▄▀▀▀█▄██▀▐█
    ▐███▌▐█•█▌ ▐█▌·   ▐█▄▪▐███▌▐▀
    ·▀▀▀ .▀  ▀ ▀▀▀  ▀  ▀▀▀▀ ▀▀▀ ·

     @Auth: C1ph3rX13
     @Blog: https://c1ph3rx13.github.io
     @Note: crt.sh Data Retrieval By C1ph3rX13
     @Warn: 代码仅供学习使用，请勿用于其他用途  
    ''')


def format_date_string(date_string: str) -> str:
    date_string = re.sub(r'\.\d+', '', date_string)
    dt = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S')
    formatted_date = dt.strftime('%Y-%m-%d')
    return formatted_date


def get_certificate_data(domain: str) -> list:
    headers = {
        'authority': 'crt.sh',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }

    params = {
        'q': domain,
        'output': 'json',
    }

    with httpx.Client(headers=headers, timeout=10, proxies=PROXIES, verify=False) as client:
        response = client.get('https://crt.sh/', params=params)
        data = json.loads(response.text)

        formatted_data = []
        for paragraph in data:
            formatted_paragraph = {
                'crt.sh ID': paragraph['id'],
                'Logged At': format_date_string(paragraph['entry_timestamp']),
                'Not Before': format_date_string(paragraph['not_before']),
                'Not After': format_date_string(paragraph['not_after']),
                'Common Name': paragraph['common_name'],
                'Matching Identities': paragraph['name_value'],
                'Issuer Name': paragraph['issuer_name'],
                'Result Count': paragraph['result_count']
            }
            formatted_data.append(formatted_paragraph)

    return formatted_data


def save_to_excel(data: list, domain: str):
    df = pd.DataFrame(data)

    df = df[['crt.sh ID', 'Logged At', 'Not Before', 'Not After', 'Common Name',
             'Matching Identities', 'Issuer Name', 'Result Count']]

    filename = generate_filename(domain)
    writer = pd.ExcelWriter(filename)
    df.to_excel(writer, index=False)
    writer.close()


def generate_filename(domain: str) -> str:
    current_time = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    return f'{current_time} - {domain}.xlsx'


if __name__ == '__main__':
    banner()
    parser = argparse.ArgumentParser(description='crt.sh Data Retrieval By C1ph3rX13')
    parser.add_argument('-t', '--target', required=True, help='Target domain')
    parser.add_argument('-p', '--proxy', required=False, help='Proxy Url')
    args = parser.parse_args()

    if args.proxy:
        PROXIES = args.proxy
        print(f'[*] Proxy Set: {args.proxy}')

    if args.target:
        certificate_data = get_certificate_data(args.target)
        save_to_excel(certificate_data, args.target)
        print(f'[*] Done: {args.target}')
