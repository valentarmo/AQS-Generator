import boto3
import argparse
import datetime
import pycountry
import time
import json
import random

def generate_data(country_codes):
    return {
        'location': 'somewhere',
        'value': random.uniform(0, 100),
        'unit': 'µg/m³',
        'particle': random.choice(['pm10', 'pm25', 'so2', 'so3', 'co', 'no2']),
        'country_code': random.choice(country_codes),
        'entity_name1': 'foss',
        'entity_name2': 'foo',
        'date_utc': datetime.datetime.utcnow().isoformat() + 'Z',
        'date_local': datetime.datetime.now().isoformat(),
        'entity': random.choice(['government', 'community']),
        'some_boolean': random.choice([True, False]),
        'latitude': random.uniform(-90, 90),
        'longitude': random.uniform(-180, 180),
        'interval': 1,
        'time_unit': 'hours'
    }


def send_to_firehose(data, stream_name, kinesis_client):
    kinesis_client.put_record(
        DeliveryStreamName=stream_name,
        Record={
            'Data': json.dumps(data)
        }
    )
    print('Sending record: ', data)


def get_stream_name():
    ssm = boto3.client('ssm')
    return ssm.get_parameter(Name='AQSDeliveryStreamName')['Parameter']['Value']


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--Interval', default=1, help='Time to wait in seconds')
    args = parser.parse_args()

    interval = args.Interval
    stream_name = get_stream_name()

    kinesis = boto3.client('firehose')

    countries = list(pycountry.countries)

    while True:
        data = generate_data(list(map(lambda country: country.alpha_2, countries)))
        try: 
            send_to_firehose(data, stream_name, kinesis)
            time.sleep(interval)
        except Exception as e:
            print(e)
            time.sleep(interval)
            continue
