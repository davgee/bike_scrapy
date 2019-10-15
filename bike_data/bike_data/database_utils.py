from bike_data.database_config import PostgreDjangoDB

class DBHelper():


    def __init__(self):
        pass

    def get_last_offer_time(self):
        db = PostgreDjangoDB()
        cursor = db.connect()
        statement = ("SELECT last_auction_add_time FROM data_gatherer_olx_scrapping_info WHERE id=1")
        cursor.execute(statement)
        respo = cursor.fetchall()
        db.save_and_close()
        return respo[0][0]

if __name__=="__main__":
    print(DBHelper().get_last_offer_time())