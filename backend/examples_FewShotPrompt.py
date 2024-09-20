from langchain_core.prompts import PromptTemplate

# define example for FewShotPromptTemplate
examples = [

    {
        "input": "what is the bus schedules of Monday from Tay Ho?",
        "sql_query": "select departure_time, arrival_time "
                 "from bus_trips a join bus_timetable b "
                 "on a.trip_id = b.trip_id "
                 "where b.day_of_week = 'Monday' and a.departure_district = 'Tay Ho';"
    },
    {
        # test - wrong SQL query
        # "input": "is there any bus from hai ba trung to buv campus?",
        "input": "is there any bus from hai ba trung to buv campus?",
        "sql_query": "select departure_time, arrival_time "
                 "from bus_trips a join bus_timetable b "
                 "on a.trip_id = b.trip_id "
                 "and a.arrival = 'BUV Campus' "
                 "where b.day_of_week = 'Monday' and a.departure_district = 'Hai Ba Trung';"
    },

]

# define template
example_prompt = PromptTemplate(
    input_variables=["input", "sql_query"],
    template="Q: {input}\n"
             "SQL Query (A): {sql_query}\n"
)
# print(example_prompt.format(**examples[0]))
