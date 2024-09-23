# from model.chat import azure_openai
from backend.utils import azure_openai
from utilize.const import *
from utilize.const import *
from datetime import datetime, timedelta

# from langchain.chat_models import ChatOpenAI
import json
from chains.VerifyTagging import *
from langchain.output_parsers import PydanticOutputParser
from chains.SQLAgent import *
import streamlit as st
from chains.BusSchedule import *

from chains.Mentioned import *
# from connect_db import *
# from SQLAgent import *

from utilize.utils import get_the_latest_sheet, get_the_starting_time

import pandas as pd
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv("../application/.env"))
# bus_schedule_file = os.getenv("BUS_SCHEDULE_FILE")

BUS_SCHEDULE_FILE = os.getenv("BUS_SCHEDULE_FILE")
df, latest_sheet = get_the_latest_sheet(BUS_SCHEDULE_FILE)


if "context" not in st.session_state:
    st.session_state.context = ""

# filepath = os.getenv("STARTING_TIME_FILE")
# df_bus = pd.read_csv(filepath)

STARTING_TIME_FILE = os.getenv("STARTING_TIME_FILE")
df_bus = get_the_starting_time(STARTING_TIME_FILE)


df_calendar = df.iloc[8:, :]

def get_busschedule_ans(prompt):
    print('--------------------------------------------')
    # print("tables:", tables)
    # tagging prompt
    print("session state:", st.session_state.state)
    # initialize
    print("prompt:", prompt)
    print("latest bot answer:", st.session_state.latest_bot_answer)
    print('-------------------')
    st.session_state.context = st.session_state.latest_bot_answer + " " + prompt
    # if all session state value is empty, means the new question is coming in, then context is new question
    # if all(not value for value in st.session_state.state.values())==True:
    #     st.session_state.context = prompt.replace(st.session_state.latest_bot_answer, "")
    # else:
    #     st.session_state.context = prompt + st.session_state.latest_bot_answer

    print("st.session_state.context:", st.session_state.context)
    # print("latest bot answer:", st.session_state.latest_bot_answer)
    # print("prompt:", prompt)
    print('-------------------')
    # answer = ""

    # suggested_questions = []
    # tagged_prompt = tagging(question=st.session_state.context, chain_busschedule=chain_busschedule)
    # print("tagged_prompt 1----------:", tagged_prompt)

    try:
        tagged_prompt = tagging(question=st.session_state.context, chain_busschedule=chain_busschedule)
        print("tagged_prompt:", tagged_prompt)

        # check tagged_prompt: if there is wrong tag then remove
        tagged_prompt = checking_tag(tagged_prompt=tagged_prompt)
        print("-----------------------------------", tagged_prompt)

        # update state
        st.session_state.state, tagged_prompt = update_state(state=st.session_state.state,
                                                             tagged_prompt=tagged_prompt,
                                                             context=st.session_state.context)
        print("after update:", tagged_prompt)
        # for key,val in st.session_state.state.items():
        #     # if tagged_prompt is not empty - means new value is here, then update session
        #     if (is_empty_or_none(tagged_prompt[reversed_mapping_state[key]])==False):
        #
        #         st.session_state.state.update({
        #             key: tagged_prompt[reversed_mapping_state[key]]
        #         })


        print("after updated:", st.session_state.state)

        # generate answer based on state
        try:
            topic, answer = bot_answer(st.session_state.state)
        except Exception as e:
            print("topic bug:", e)
            answer = "Please input your request again?"
            topic = ""

        # generate suggestion for user based on topic
        try:
            suggested_questions = generate_user_suggestion(topic=topic)
        except Exception as e:
            print("suggested questions bug:", e)
            suggested_questions = []


    except Exception as e:
        print("general bug:", e)
        answer = "Sorry, can you please provide more information again?"
        suggested_questions = []

    if all(not value for value in st.session_state.state.values()) == True:
        st.session_state.latest_bot_answer = ""
    else:
        st.session_state.latest_bot_answer = answer
    # print("session state:", st.session_state.state)
    print("answer:", answer)
    # print("session state:", st.session_state.state)
    return answer, suggested_questions



#========= suggestion for user - in general ==========
def generate_user_suggestion(topic):
    print("topic:", topic)
    if topic=="route name":
        suggested_questions = generate_route_name(state=st.session_state.state)

    elif topic=="pick-up point":
        suggested_questions = generate_pickup_point(state=st.session_state.state)
    elif topic=="drop-off point":
        suggested_questions = generate_dropoff_point(state=st.session_state.state)

    elif topic=="specific date":
        suggested_questions = generate_specific_date(state=st.session_state.state)
    elif topic=="specific time":
        suggested_questions = generate_specific_time(state=st.session_state.state)

    else: # topic=="":
        suggested_questions = []
    # print("suggested_questions", suggested_questions)
    return suggested_questions

#========= verify tagged stops ==========
def update_state(state, tagged_prompt, context):
    # verify tagging
    def verify_tag(tag, tagged_name, context):
        verification = chain_verify_tagging.invoke({
            "tagged_name": tagged_name,
            "tag": tag,  # dropoff_point, pickup_point
            "context": context
        })
        result = {
            "tagging": True
        }

        try:
            result["tagging"] = json.loads(verification.dict()["content"])["tagging"]
        except Exception as e:
            print("verify bug:", e)

        return result

    print("========== verify ============")
    print(tagged_prompt)
    # print(context)

    # update state
    print("state:", state)
    # print("another state:". st.session_state.state)
    # for key,val in tagged_prompt.items():
    #     if is_empty_or_none(val)==False:
    #         print(key, val)
    #         for tagged_name in val:
    #             print(verify_tag(tag=key, tagged_name=tagged_name, context=context))
    #     # tag = key # dropoff_point etc.
    #     # for each tagged value in val, verify it was appear in context or not
    #     for tagged_name in val:
    #         vrf = verify_tag(tag=key, tagged_name=tagged_name, context=context)
    #         if vrf["tagging"]==True: # if this location is really appear in context
    #             st.session_state.state[key].append(tagged_name)



    # update state
    for key, val in state.items():
        # if tagged_prompt is not empty - means new value is here, then update session
        if (is_empty_or_none(tagged_prompt[reversed_mapping_state[key]]) == False):
            st.session_state.state.update({
                key: tagged_prompt[reversed_mapping_state[key]]
            })

    return state, tagged_prompt


def checking_tag(tagged_prompt):
    # simple check if the tagged values are in the bus schedule or not
    for key,val in tagged_prompt.items():
        # if the bot recognized something:
        if is_empty_or_none(val)==False:
            # "something" = route name, check if route name not in bus schedule
            if (key=="route_name") and (val[0] not in bus_route_name):
                # then remove tagged value
                val = []
            # "something" is pickup or dropoff point
            if (key in ["pickup_point", "dropoff_point"]) and (val[0] not in point_name):
                tagged_prompt[key] = []
    return tagged_prompt


#========= suggestion of each params for user ==========
def generate_route_name(state):
    return ["Hai Ba Trung", "Cau Giay", "Tay Ho", "Ha Dong", "Ecopark"]

def generate_pickup_point(state):
    if is_empty_or_none(state["route name"])==False:
        # if no drop-off point
        if is_empty_or_none(state["drop-off point"]) == True:
            # then suggest all stops of the route - mapping with route name
            return [i for i in dct_routename_station[state["route name"][0]] if i!="Hong Ha"]
        # if has drop-off point
        if is_empty_or_none(state["drop-off point"]) == False:
            result = [i for i in dct_routename_station[state["route name"][0]] if i not in state["drop-off point"]]

            # for route Tay Ho, if it already has drop-off point in [Hong Ha, Tran Khanh Du]
            if state["drop-off point"][0] in ["Tran Khanh Du", "Hong Ha"]:
                result = [i for i in result if i not in ["Tran Khanh Du", "Hong Ha"]]

            return result
        # return dct_routename_station[state["route name"][0]]

    # if no route name
    if is_empty_or_none(state["route name"])==True:
        # if no drop-off point
        if is_empty_or_none(state["drop-off point"]) == True:
            # then suggest all stops of the route
            return point_name
        # if has drop-off point
        if is_empty_or_none(state["drop-off point"]) == False:
            # then need to suggest mapping with  drop-off point
            # check route of drop-off point
            for route,stops in dct_routename_station.items():
                if state["drop-off point"] in stops:
                    result = stops
                    break
            # list all stops in this route, except drop-off point
            result = [i for i in result if i!=state["drop-off point"]]

            # for route Tay Ho, if it already has drop-off point in [Hong Ha, Tran Khanh Du]
            if state["drop-off point"][0] in ["Tran Khanh Du", "Hong Ha"]:
                result = [i for i in result if i not in ["Tran Khanh Du", "Hong Ha"]]

            return result
    #
    # else:
    #     return []

def generate_dropoff_point(state):
    if is_empty_or_none(state["route name"])==False:
        # if no pick-up point
        if is_empty_or_none(state["pick-up point"]) == True:
            # then suggest all stops of the route - mapping with route name
            return dct_routename_station[state["route name"][0]]
        # if has pick-up point
        if is_empty_or_none(state["pick-up point"]) == False:
            result = [i for i in dct_routename_station[state["route name"][0]] if i not in state["pick-up point"]]

            # for route Tay Ho, if it already has pick-up point in [Hong Ha, Tran Khanh Du]
            if state["pick-up point"][0] in ["Tran Khanh Du", "Hong Ha"]:
                result = [i for i in result if i not in ["Tran Khanh Du", "Hong Ha"]]

            # if pick-up point is BUV Campus then drop-off cannot be Tran Khanh Du
            if state["pick-up point"][0] in ["BUV Campus"]:
                result = [i for i in result if i not in ["Tran Khanh Du"]]
            return result
        # return dct_routename_station[state["route name"][0]]

    # if no route name
    if is_empty_or_none(state["route name"])==True:
        # if no pick-up point
        if is_empty_or_none(state["pick-up point"]) == True:
            # then suggest all stops of the route
            return point_name
        # if has pick-up point
        if is_empty_or_none(state["pick-up point"]) == False:
            # then need to suggest mapping with pick-up point
            # check route of pick-up point
            for route,stops in dct_routename_station.items():
                if state["pick-up point"] in stops:
                    result = stops
                    break
            # list all stops in this route, except pick-up point
            result = [i for i in result if i!=state["pick-up point"]]
            return result

    # old code:
    # # print("here", state["route name"], is_empty_or_none(state["route name"]))
    # if is_empty_or_none(state["route name"])==False:
    #     # print("here2")
    #     # print(dct_routename_station[state["route name"][0]])
    #     return dct_routename_station[state["route name"][0]]
    # else:
    #     return []


def generate_specific_date(state) -> List:    
    # # Get the list of sheet names
    # sheet_names = pd.ExcelFile(bus_schedule_file).sheet_names

    # # Pick the latest sheet
    # latest_sheet = sheet_names[-1]

    # # Load the data from the latest sheet
    # df = pd.read_excel(bus_schedule_file, sheet_name=latest_sheet)

    # Get a list of datetime elements in the first column, skipping nan values and str type
    datetimes = df.iloc[:, 0].dropna().loc[lambda x: x.apply(lambda y: not isinstance(y, str))].reset_index(drop=True)

    # Get unique values
    unique_datetimes = datetimes.unique()

    # Convert to a pandas Series to use sort_values
    unique_datetimes_series = pd.Series(unique_datetimes)

    # Sort the unique datetimes in ascending order
    sorted_unique_datetimes = unique_datetimes_series.sort_values().reset_index(drop=True)
    sorted_unique_datetimes = pd.to_datetime(sorted_unique_datetimes)
    
    # Get today's date
    today = datetime.today()
    today = today.strftime('%Y-%m-%d')
    today = pd.to_datetime(today)

    # Filter dates starting from today
    filtered_datetimes = sorted_unique_datetimes[sorted_unique_datetimes >= today]

    # Format the filtered dates
    result = [day.strftime("%a %d %b") for day in filtered_datetimes]
    
    return result


def generate_specific_time(state):
    route_name = state["route name"][0]
    pickup_point = state["pick-up point"][0]
    dropoff_point = state["drop-off point"][0]
    specific_date = state["specific date"][0]

    print(f"{route_name=}, {pickup_point=}, {dropoff_point=}, {specific_date=}")
    # if there is a route name
    if is_empty_or_none(state["route name"])==False:

        # if no pick-up point:
        if is_empty_or_none(state["pick-up point"])==True:
            # then return all starting time available of this route
            return dct_pickup_time[state["route name"]]

        # if there is a pick-up point
        if is_empty_or_none(state["pick-up point"])==False:
            # then return starting time of this pickup point only
            print("---------get suggest time here--------------")
            weekday = specific_date.split()[0]
            print(f"{weekday=}")
            result_calendar = df_calendar[(df_calendar["Unnamed: 1"]==weekday)
                            & (df_calendar["Unnamed: 2"]==dct_excel_mapping[route_name])]
            print(f"{result_calendar=}")
            result_calendar.columns = [str(i) for i in range(0, 14)]
            print(f"{df_bus=}")
            result = df_bus[(df_bus["route_name"]==route_name) \
                & (df_bus["pickup_point"] == pickup_point)
                & (df_bus["dropoff_point"] == dropoff_point)]

            print(f"{result=}")
            suggestion = gen_available_timeslot(pickup_point, result_calendar, result)
            print("suggestion:", suggestion)
            return suggestion

    # if no route name
    if is_empty_or_none(state["route name"])==True:

        # if no pick-up point:
        if is_empty_or_none(state["pick-up point"]) == True:
            return pickup_time

        # if there is a pick-up point
        if is_empty_or_none(state["pick-up point"]) == False:
            suggestion = gen_available_timeslot()
            
            return suggestion

#=======================================================



def tagging(question, chain_busschedule):

    def check_mentioned():
        chain_mention.invoke({

        })
        return

    # def check_route(route_list):
    #     if not route_list:
    #         route_list = []
    #     return [name for name in route_list if name in bus_route_name]

    # set up output format
    formatted_msg = {
        'route_name': None,
        'pickup_point': None,
        'dropoff_point': None,
        'date_': None,
        'time_': None,
    }
    try:
        msg = chain_busschedule.invoke({"query": question})
        msg_json = convert_to_json(msg.dict())
        # msg_json = msg.dict()["content"]
        # msg_json = json.loads(msg.dict()["content"])

        # print("key route:", msg_json["route_name"])
        print("json result:", msg_json) # json result: {'json': {'route_name': None, 'pickup_point': None, 'dropoff_point': ['BUV Campus'], 'date_': None, 'time_': None}}

        # print("type:", type(msg_json))
        keys_in_both = [key for key in formatted_msg if key in msg_json]
        # print(keys_in_both)
        # print("msg json:", msg_json)

        for key in keys_in_both:
            # print(key)
            # print(formatted_msg[key])
            formatted_msg[key] = msg_json[key]

        # print("formatted msg:", formatted_msg)
        return formatted_msg
    except Exception as e:
        print("json bug:", e)

    return formatted_msg



def convert_to_json(input_str):
    # init str
    str_data = input_str["content"]
    try:
        return json.loads(str_data)
    except json.decoder.JSONDecodeError:
        # Loại bỏ dấu phẩy thừa
        corrected_json_string = str_data.rstrip(",\n ") + '\n'
        corrected_json_string = corrected_json_string.replace(",\n}", "\n}").replace(",\n]", "\n]")
        return json.loads(corrected_json_string)


def is_empty_or_none(lst):
    # print("type:", type(lst))
    if (type(lst)==list) and (None in lst):
        lst = [item for item in lst if item is not None]
    return lst is None or len(lst) == 0

def gen_available_timeslot(pickup_point, result_calendar, result):
    suggestion = []
    for col in result_calendar.columns:
        if (result_calendar[col].values[0]==1) and (int(col)<=7) and (pickup_point!="BUV Campus"):
            # print(col, result_calendar[col].values[0])
            timeslot = result["slot"+str(int(col)-2)].values[0]
            suggestion.append(str(timeslot))
        if (result_calendar[col].values[0]==1) and (int(col)>=8) and (pickup_point=="BUV Campus"):
            timeslot = result["slot"+str(int(col)-7)].values[0]
            suggestion.append(str(timeslot))
    suggestion = [x for x in suggestion if x!="nan"]     
    return suggestion

#======================== QUERY DATA FROM DB =====================
def answer_from_query(state):
    answer = convert_sql(state)

    # reset memories
    st.session_state.context = ""
    st.session_state.state = {
        "route name": [],
        "pick-up point": [],
        "drop-off point": [],
        "specific date": [],
        "specific time": []
    }
    st.session_state.latest_bot_answer = ""

    return answer
#======================== GET DATA FROM DATAFRAME =====================
def answer_from_dataframe(state):

    return
#================================================================




# suggest bot questions
def bot_answer(state):

    def generate_question_of(topic):
        prompt_template = PromptTemplate(
            input_variables=[],
            template="""You're bot assistant to provide information about bus schedule.\n
            Customers need to provide information about their bus route they want to catch. Can you suggest a question about: {topic}\n
            Don't greet the user! Don't say Hi. Explain you need to get some info. \n
            Avoid greetings such as 'Hi' or 'Hello'."""
        )
        # create chain
        chain = prompt_template | azure_openai | StrOutputParser()
        # get answer from chain
        answer = chain.invoke({
            "topic": topic,
        })
        return answer

    print("hereeee -----------------")
    # print(state)
    # if all infor are provided
    # if (is_empty_or_none(state["route name"])==False) \
    #         and (is_empty_or_none(state["pick-up point"])==False) \
    if (is_empty_or_none(state["pick-up point"]) == False) \
            and (is_empty_or_none(state["drop-off point"]) == False) \
            and (is_empty_or_none(state["specific date"])==False) \
            and (is_empty_or_none(state["specific time"])==False):

        # CALL SQL
        answer_result = answer_from_query(state=state)

        # CALL DATAFRAME
        answer_res = answer_from_dataframe(state=state)

        return ("topic empty bot answer", answer_result)

    # if there is still a topic need to be filled infor
    for key, val in state.items():
        if (key=="route name") \
            and (is_empty_or_none(state["route name"]) == True) \
            and (is_empty_or_none(state["pick-up point"]) == True) \
            and (is_empty_or_none(state["drop-off point"]) == True) \
            and (is_empty_or_none(state["specific date"]) == True) \
            and (is_empty_or_none(state["specific time"]) == True):
            return (key, generate_question_of(key))


        if (is_empty_or_none(val)==True) and key != "route name":
            topic = key
            # print(topic)
            return (topic, generate_question_of(topic))
        # else:
        #     print("no empty topic")
        #     topic = key
        #     return (topic, generate_question_of(topic))


