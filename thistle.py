import re
import mysql.connector
from datetime import datetime

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'thistle',
    'password': 'thistle',
    'database': 'thistle'
}

# Apache log regex pattern
log_pattern = re.compile(
    r'(?P<ip>\S+) \S+ \S+ \[(?P<datetime>.*?)\] "(?P<method>\S+) (?P<endpoint>.*?) (?P<protocol>.*?)" (?P<status>\d{3}) (?P<bytes>\S+) "(?P<referrer>.*?)" "(?P<user_agent>.*?)"'
)

def parse_log_line(line):
    match = log_pattern.match(line)
    if match:
        data = match.groupdict()
        # Parse datetime to standard format
        data['datetime'] = datetime.strptime(data['datetime'], "%d/%b/%Y:%H:%M:%S %z").strftime("%Y-%m-%d %H:%M:%S")
        # Convert bytes_sent to integer, handle '-' as 0
        data['bytes'] = int(data['bytes']) if data['bytes'] != '-' else 0
        return data
    return None

def insert_log_to_db(cursor, log_data):
    sql = (
        "INSERT INTO apache_logs (virtualhost,ip_address, identity, user, timestamp, method, endpoint, protocol, status_code, bytes_sent, referrer, user_agent) "
        "VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    )
    values = (
        'jocarsa-oldlace',
        log_data['ip'],
        '-',  # Identity (not provided in this log example)
        '-',  # User (not provided in this log example)
        log_data['datetime'],
        log_data['method'],
        log_data['endpoint'],
        log_data['protocol'],
        int(log_data['status']),
        log_data['bytes'],
        log_data['referrer'],
        log_data['user_agent']
    )
    cursor.execute(sql, values)

def main():
    log_file_path = '/var/log/apache2/jocarsa-oldlace-access.log'  # Update with your log file path

    # Connect to the database
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    try:
        with open(log_file_path, 'r') as file:
            for line in file:
                log_data = parse_log_line(line)
                if log_data:
                    insert_log_to_db(cursor, log_data)

        # Commit all inserts
        connection.commit()
        print("Log data inserted successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")
        connection.rollback()

    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    main()
