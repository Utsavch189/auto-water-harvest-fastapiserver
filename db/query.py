from db.connection import client,conn
from utils import get_datetime

class Query:

    @staticmethod
    def login(username:str,password:str):
        try:
            exists_q="""
                    SELECT password,id FROM Raspberry WHERE username='%s'
            """%(username,)
            res=client.exec_query(exists_q,conn)
            for i in res:
                data=i
            if not res:
                return {"message":"username is incorrect!"},False
            id=data['id']
            pswd=data['password']

            if not password==pswd:
                return {"message":"password is incorrect!"},False
            
            return {"message":"logged in!","id":id},True

        except Exception as e:
            print(e)
    
    @staticmethod
    def update_raspberry_task(raspberry_id:str,auto_harvest:bool,pump_schedule_start_time:str,pump_schedule_end_time:str,system_cooling:bool,pump_start_now:bool):
        try:
            insert_q="""
            INSERT INTO RaspberryTaskControl(raspberry_id,auto_harvest,pump_schedule_start_time,pump_schedule_end_time,system_cooling,pump_start_now,uploaded_at)
            VALUES('%s',%d,'%s','%s',%d,%d,'%s')
        """%(raspberry_id,auto_harvest,pump_schedule_start_time,pump_schedule_end_time,system_cooling,pump_start_now,get_datetime())
   
            update_q="""
                UPDATE RaspberryTaskControl SET auto_harvest=%d,pump_schedule_start_time='%s',pump_schedule_end_time='%s',system_cooling=%d,pump_start_now=%d,uploaded_at='%s'
                WHERE raspberry_id="%s"
            """%(auto_harvest,pump_schedule_start_time,pump_schedule_end_time,system_cooling,pump_start_now,get_datetime(),raspberry_id)

            if Query.get_updated_task(raspberry_id):
                client.exec_query(update_q,conn)
            else:
                client.exec_query(insert_q,conn)
        except Exception as e:
            print(e)

    
    @staticmethod
    def get_updated_task(raspberry_id:str):
        q="""
            SELECT * FROM RaspberryTaskControl WHERE raspberry_id='%s'
        """%(raspberry_id,)
        try:
            res=client.exec_query(q,conn)
            data=[]
            for i in res:
                data.append(i)
            return data
        except Exception as e:
            print(e)
    
    @staticmethod
    def get_raspall_data(raspberry_id:str):
        system_q="""
            SELECT id,cpu_temperature,cpu_usage,memory_usage,disk_usage,network_stats,system_uptime,core_info,uploaded_at
            FROM RaspberrySystem
            WHERE raspberry_id='%s'
            ORDER BY uploaded_at DESC
            LIMIT 10
        """%(raspberry_id,)

        sensor_q="""
            SELECT id,temp_data,humidity_data,soil_moist_data,uploaded_at
            FROM RaspSensorData
            WHERE raspberry_id='%s'
            ORDER BY uploaded_at DESC
            LIMIT 10
        """%(raspberry_id,)
        # print(q)
        try:
            res1=client.exec_query(system_q,conn)
            res2=client.exec_query(sensor_q,conn)
            system=[]
            sensor=[]
            for i in res1:
                system.append(i)
            for i in res2:
                sensor.append(i)
            data={
                "system_data":system,
                "sensor_data":sensor
            }
            return data
        except Exception as e:
            print(e)

