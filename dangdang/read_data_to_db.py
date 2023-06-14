import pymysql
import csv


def extract_data_from_csv_file(csv_file):
    with open(csv_file, 'r', encoding='U8') as f:
        csv_reader = csv.reader(f)
        next(csv_reader)
        yield from csv_reader


def handle(data):
    with pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='271xufei.',
        database='jyge'
    ) as connection:
        cursor = connection.cursor()
        sql_insert_statement = 'insert into books values (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
        for single_data in data:
            [book_type, book_name, pb_date, publisher, now_price, pre_price, discount, detail, _] = single_data
            if pb_date == "":
                pb_date = None
            book_type = book_type.strip()
            book_name = book_name.strip()
            publisher = publisher.strip()
            detail = detail.strip()
            now_price = float(now_price.strip('¥'))
            pre_price = float(pre_price.strip('¥'))
            discount = int(float(discount.replace('折', '')) * 10)
            try:
                cursor.execute(sql_insert_statement, (
                    None, book_type, book_name, now_price, pre_price, pb_date, publisher, discount, detail
                ))
                connection.commit()
            except Exception as e:
                print(e)
                connection.rollback()
        cursor.close()


if __name__ == '__main__':
    iter_data = extract_data_from_csv_file('Python-result.csv')
    handle(data=iter_data)
