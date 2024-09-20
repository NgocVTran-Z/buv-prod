from datetime import datetime
import pandas as pd

bus_route_name = ["Hai Ba Trung", "Cau Giay", "Ha Dong", "Tay Ho", "Ecopark"]

route_HaiBaTrung = ["51 Le Dai Hanh", "Times City", "AEON Mall Long Bien",
                    "Rung Co - E2 Building", "BUV Campus"]
route_BUV_HaiBaTrung = ["BUV Campus", "AEON Mall Long Bien", "Times City", "51 Le Dai Hanh"]
    # ["Sky Oasis", "Sol Forest", "Landmark", "Swanlake",
    #              "Westbay – B Building", "Westbay – C Building",
    #              "Aquabay - Sky 2 Building", "Aquabay – Park 1 - Building", "BUV Campus"]
# route_HaiBaTrung = ["Le Dai Hanh", "Times City", "AEON Mall Long Bien", "Ecopark", "BUV Campus"]

route_CauGiay = ["Nguyen Quoc Tri", "National Cinema Centre", "BUV Campus"]
# route_BUV_CauGiay = []

route_HaDong = ["Ho Guom Plaza", "473 Nguyen Trai", "Muong Thanh Grand Hotel", "Linh Nam", "BUV Campus"]

route_TayHo = ["Ho Tay Water Park", "Au Co", "Tran Khanh Du", "Hong Ha", "Vinhomes Ocean Park", "BUV Campus"]

route_Ecopark = ["Sky Oasis", "Sol Forest", "Landmark", "Swanlake",
                 "Westbay – B Building", "Westbay – C Building",
                 "Aquabay - Sky 2 Building", "Aquabay – Park 1 - Building",
                 "Rung Co - E2 Building", "BUV Campus"]

topics = ("pickup_point", "dropoff_point", "date_", "time_")

point_name = route_CauGiay + route_HaDong + route_HaiBaTrung + route_TayHo + route_Ecopark
point_name = list(set(point_name))

dct_routename_station = {
    "Hai Ba Trung": route_HaiBaTrung,
    "Cau Giay": route_CauGiay,
    "Ha Dong": route_HaDong,
    "Tay Ho": route_TayHo,
    "Ecopark": route_Ecopark
}

dct_excel_mapping = {
    "Hai Ba Trung": "HBT",
    "Tay Ho": "TH",
    "Cau Giay": "CG",
    "Ha Dong": "HD"
}

current_datetime = datetime.now()
formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
day_of_week_str = current_datetime.strftime("%A")
datetime_full = day_of_week_str + " " + formatted_datetime

mapping_state = {
    "route_name": "route name",
    "pickup_point": "pick-up point",
    "dropoff_point": "drop-off point",
    "date_": "specific date",
    "time_": "specific time"
}
# Tạo dictionary mới bằng cách hoán đổi key và value
reversed_mapping_state = {value: key for key, value in mapping_state.items()}

#=================================================
pickup_CauGiay = ["07:00:00", "09:30:00", "10:25:00", "11:40:00", "13:30:00"]
pickup_HaDong = ["07:30:00", "09:30:00", "10:30:00", "11:30:00", "13:30:00"]
pickup_HaiBaTrung = ["07:40:00", "09:40:00", "10:40:00", "12:00:00", "13:30:00"]
pickup_TayHo = ["07:40:00", "09:40:00", "10:40:00", "11:40:00", "13:30:00"]

pickup_time = pickup_CauGiay + pickup_HaDong + pickup_HaiBaTrung + pickup_TayHo
pickup_time = list(set(pickup_time))

dct_pickup_time = {
    "Cau Giay": pickup_CauGiay,
    "Hai Ba Trung": pickup_HaiBaTrung,
    "Ha Dong": pickup_HaDong,
    "Tay Ho": pickup_TayHo
}


route_gps = {
    "route 1": {
        "51 Le Dai Hanh": "https://maps.app.goo.gl/5Z33GKjzCQ4HXm827",
        "Times City": "https://maps.app.goo.gl/TXhQPCe52VVa8Bn99",
        "AEON Mall": "https://maps.app.goo.gl/1cHZ7NSBEd8G9q6v9"
    },
    "route 2": {
        "Ho Guom Plaza": "https://maps.app.goo.gl/QShde2kSyFzbDhnb6",
    },

}



#--------------------------- read dataframe --------------------------
filepath = "data/StartingTime.csv"
df_bus = pd.read_csv(filepath)



#--------------------------- streamlit UI --------------------------


introduction = """
Hi, I’m StarLeo, 

Before you begin using our chat services, please note that the information provided by this chatbot is intended for reference purposes only. For more information visit Chatbot Disclaimer and Guidelines.

If you are required an immediate assistance, please call our hotline at **0704 068 386**

If you have any feedback or special request, feel free to contact the Transportation Team via transportation@buv.edu.vn.
        
"""



