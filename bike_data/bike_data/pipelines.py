# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from bike_data.database_utils import PostgreDjangoDB
from scrapy.exceptions import DropItem

class BikeDataPipeline(object):
    def process_item(self, item, spider):
        rollback = []
        db_con = PostgreDjangoDB()
        cur = db_con.connect()

        try:
            columns = [x for x in item.keys()]
            data = [x for x in item.values()]

            columns_str = str(columns)
            columns_str = columns_str.replace("'", "").replace("[","").replace("]", "")
            data_str = str(data).replace("[","").replace("]", "")

            statement = 'INSERT INTO bike_offers_olx (' + columns_str + ') VALUES (' + data_str + ')' 
            cur.execute(statement)
            db_con.save_and_close()

        except:
            rollback = rollback.append(db_con.save_and_close)
            raise DropItem 
        finally:
            if rollback:
                for rollback_func in rollback:
                    rollback_func()
                return "rollbacked."

            return item # "Object added to database"
