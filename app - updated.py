from flask import Flask, render_template, request
from chatbot import chatbot
import pyodbc
import re

# Create a connection to your SQL Server database
conn = pyodbc.connect('Driver={SQL Server};Server=ARVIND\MSSQLSERVER01;Database=master;Trusted_Connection=yes;')

app = Flask(__name__)
app.static_folder = 'static'

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')

    # Check if the user query is for AHT
    if "AHT" in userText:
        # Extract the agent name and number of days from the user query
        agent_name, num_days = extract_agent_info(userText)

        if agent_name is None or num_days is None:
            response = "Please provide the agent name and number of days for calculating AHT."
        else:
            # Construct the SQL query
            query = f"SELECT Date, AVG(TalkTime) FROM AHT_data WHERE Agent_Name = '{agent_name}' AND Date >= DATEADD(day, -{num_days}, CAST(GETDATE() AS DATE)) GROUP BY Date"
            # Print the SQL query being used
            print("SQL Query:", query)

            # Execute the SQL query
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()

            # Process the result and generate a response
            if result:
                response = "The average handling time (AHT) for {} over the past {} days:<br>".format(agent_name, num_days)
                response += "<table style='border-collapse: collapse;'>"
                response += "<tr><th style='border: 1px solid black; padding: 5px;'>Date</th><th style='border: 1px solid black; padding: 5px;'>AHT (seconds)</th></tr>"
                for row in result:
                    date = row[0]
                    aht = row[1]
                    response += "<tr><td style='border: 1px solid black; padding: 5px;'>{}</td><td style='border: 1px solid black; padding: 5px;'>{}</td></tr>".format(date, aht)
                response += "</table>"
            else:
                response = "No data available for the specified agent and time period."
    else:
        # Pass the user query to the chatbot for other non-SQL related responses
        response = str(chatbot.get_response(userText))

    return response

def extract_agent_info(query):
    # Extract the agent name and number of days from the user query
    agent_name = None
    num_days = None

    # Use regular expressions to find the agent name and number of days
    agent_match = re.search(r'for\s+(\w+)\s+', query, re.IGNORECASE)
    days_match = re.search(r'(\d+)\s+days', query, re.IGNORECASE)

    # Extract the agent name and number of days if found
    if agent_match:
        agent_name = agent_match.group(1)
    if days_match:
        num_days = int(days_match.group(1))

    return agent_name, num_days


if __name__ == "__main__":
    app.run()
