
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from chains.DateTimeAgent import *
from utilize.const import *
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv("../application/.env"))
from datetime import datetime
# from model.chat import azure_openai
from backend.utils import azure_openai
# from model.embeddings import text_embedding_3large
from backend.utils import text_embedding_3large
from utilize.connect_db import *
# from utilize.queries import *
import sqlite3


def query_full_info(state):
    pickup_point = state["pick-up point"][0]
    dropoff_point = state["drop-off point"][0]
    specific_date = state["specific date"][0]
    specific_time = state["specific time"][0]
    print(pickup_point, dropoff_point, specific_date, specific_time)

    specific_datetime = convert_datetime(state_date=specific_date, state_time=specific_time) + ":00"
    # print(specific_datetime)

    datetime_obj = datetime.strptime(specific_datetime, "%Y-%m-%d %H:%M:%S")
    specific_time = datetime_obj.strftime("%H:%M:%S")
    specific_date = datetime_obj.strftime("%Y-%m-%d") + " 00:00:00"

    # # Trích xuất phần thời gian
    # time_str = datetime_obj.strftime("%H:%M:%S")
    # # Đặt thời gian thành 00:00:00
    # date_str = datetime_obj.strftime("%Y-%m-%d") + " 00:00:00"
    # print(time_str)
    # print(date_str)

    # if cannot detect exactly the specific time, get time slots of the whole day


    query = f"""
    select date(tmp3.date), src.trip_id,src.stop_name,  time(src.stop_time)  from bus_schedule src
    join
    (
    select a.trip_id, a.stop_sequence from bus_schedule a 
    join bus_timetable b on a.trip_id = b.trip_id 
    where b.date = '{specific_date}'
    and a.stop_name = '{pickup_point}'
    and time(a.stop_time) = '{specific_time}'
    ) tmp1 on src.trip_id = tmp1.trip_id
    join
    (
    select a.trip_id, a.stop_sequence from bus_schedule a 
    join bus_timetable b on a.trip_id = b.trip_id 
    where b.date = '{specific_date}'
    and a.stop_name = '{dropoff_point}'
    ) tmp2 on src.trip_id = tmp2.trip_id
    join bus_timetable tmp3 on src.trip_id = tmp3.trip_id
    where src.stop_sequence >= tmp1.stop_sequence and src.stop_sequence <= tmp2.stop_sequence
    and tmp3.date = '{specific_date}';
    """ #.format(specific_datetime, pickup_point, dropoff_point)

    # query_posgres = f"""
    # SELECT DATE(tmp3.date) AS date, src.trip_id, src.stop_name, src.stop_time::time AS stop_time
    # FROM bus_schedule AS src
    # JOIN (
    #     SELECT a.trip_id, a.stop_sequence
    #     FROM bus_schedule AS a
    #     JOIN bus_timetable AS b ON a.trip_id = b.trip_id
    #     WHERE b.date = '2024-05-29 00:00:00'
    #       AND a.stop_name = 'Nguyen Quoc Tri'
    #       AND a.stop_time::time <= '08:00:00'
    # ) AS tmp1 ON src.trip_id = tmp1.trip_id
    # JOIN (
    #     SELECT a.trip_id, a.stop_sequence
    #     FROM bus_schedule AS a
    #     JOIN bus_timetable AS b ON a.trip_id = b.trip_id
    #     WHERE b.date = '2024-05-29 00:00:00'
    #       AND a.stop_name = 'BUV Campus'
    # ) AS tmp2 ON src.trip_id = tmp2.trip_id
    # JOIN bus_timetable AS tmp3 ON src.trip_id = tmp3.trip_id
    # WHERE src.stop_sequence >= tmp1.stop_sequence
    #   AND src.stop_sequence <= tmp2.stop_sequence
    #   AND tmp3.date = '2024-05-29 00:00:00';
    #
    # """

    print("------------------")
    print(query)
    print("------------------")

    return query

def query_full_info_postgres(state):
    pickup_point = state["pick-up point"][0]
    dropoff_point = state["drop-off point"][0]
    specific_date = state["specific date"][0]
    specific_time = state["specific time"][0]
    print(pickup_point, dropoff_point, specific_date, specific_time)

    specific_datetime = convert_datetime(state_date=specific_date, state_time=specific_time) + ":00"
    # print(specific_datetime)

    datetime_obj = datetime.strptime(specific_datetime, "%Y-%m-%d %H:%M:%S")
    specific_time = datetime_obj.strftime("%H:%M:%S")
    specific_date = datetime_obj.strftime("%Y-%m-%d") + " 00:00:00"


    query = f"""
    SELECT DATE(tmp3.date) AS date, src.trip_id, src.stop_name, src.stop_time::time AS stop_time
    FROM bus_schedule AS src
    JOIN
    (
    select a.trip_id, a.stop_sequence from bus_schedule a 
    join bus_timetable b on a.trip_id = b.trip_id 
    where b.date = '{specific_date}'
    and a.stop_name = '{pickup_point}'
    AND a.stop_time::time = '{specific_time}'
    ) tmp1 on src.trip_id = tmp1.trip_id
    join
    (
    select a.trip_id, a.stop_sequence from bus_schedule a 
    join bus_timetable b on a.trip_id = b.trip_id 
    where b.date = '{specific_date}'
    and a.stop_name = '{dropoff_point}'
    ) tmp2 on src.trip_id = tmp2.trip_id
    join bus_timetable tmp3 on src.trip_id = tmp3.trip_id
    where src.stop_sequence >= tmp1.stop_sequence and src.stop_sequence <= tmp2.stop_sequence
    and tmp3.date = '{specific_date}';
    """ #.format(specific_datetime, pickup_point, dropoff_point)

    # query_posgres = f"""
    # SELECT DATE(tmp3.date) AS date, src.trip_id, src.stop_name, src.stop_time::time AS stop_time
    # FROM bus_schedule AS src
    # JOIN (
    #     SELECT a.trip_id, a.stop_sequence
    #     FROM bus_schedule AS a
    #     JOIN bus_timetable AS b ON a.trip_id = b.trip_id
    #     WHERE b.date = '2024-05-29 00:00:00'
    #       AND a.stop_name = 'Nguyen Quoc Tri'
    #       AND a.stop_time::time <= '08:00:00'
    # ) AS tmp1 ON src.trip_id = tmp1.trip_id
    # JOIN (
    #     SELECT a.trip_id, a.stop_sequence
    #     FROM bus_schedule AS a
    #     JOIN bus_timetable AS b ON a.trip_id = b.trip_id
    #     WHERE b.date = '2024-05-29 00:00:00'
    #       AND a.stop_name = 'BUV Campus'
    # ) AS tmp2 ON src.trip_id = tmp2.trip_id
    # JOIN bus_timetable AS tmp3 ON src.trip_id = tmp3.trip_id
    # WHERE src.stop_sequence >= tmp1.stop_sequence
    #   AND src.stop_sequence <= tmp2.stop_sequence
    #   AND tmp3.date = '2024-05-29 00:00:00';
    #
    # """
    print("------------------")
    print(query)

    return query
