from bike_data.database_config import PostgreDjangoDB
from bike_data.items import BikeDataItem
import json

class DBHelper():


    def __init__(self):
        pass

    def get_last_offer_time(self):
        db = PostgreDjangoDB()
        cursor = db.connect()
        statement = ("SELECT add_time FROM bike_offers_olx ORDER BY add_time DESC LIMIT 1")
        cursor.execute(statement)
        respo = cursor.fetchall()
        db.save_and_close()
        return respo[0][0]

    def get_some_records(self):
        db = PostgreDjangoDB()
        cursor = db.connect()
        statement = ("SELECT * FROM bike_offers_olx WHERE description IS NOT NULL LIMIT 10;")
        cursor.execute(statement)
        respo = cursor.fetchall()
        db.save_and_close()
        bike_list = []
        for x in range(10):
            bike = self.convert_to_bike_obj(respo[x])
            bike_list.append(bike)

        return bike_list

    def convert_to_bike_obj(self, bike_data):
        a = BikeDataItem(
            id=bike_data[0],
            title=bike_data[1],
            price=bike_data[2],
            url_addres=bike_data[3],
            add_time=bike_data[4],
            place=bike_data[5],
            paid_offer=bike_data[6],
            description=bike_data[7],
            added_via_phone=bike_data[8]
        )
        return a


if __name__=="__main__":
    a = DBHelper().get_some_records()
