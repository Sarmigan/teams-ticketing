from flask import Flask, request, Response
from dotenv import load_dotenv
import json
import boto3
import os

load_dotenv()
app = Flask(__name__)

client = boto3.client(
    'sqs',
    aws_access_key_id=os.environ["ACCESS_KEY"],
    aws_secret_access_key=os.environ["SECRET_KEY"]
)

def send_to_queue(message, priority):
    message = json.dumps(message)

    try:
        url = client.get_queue_by_name(QueueName=priority)["QueueUrl"]
    except:
        url = client.create_queue(QueueName=priority)["QueueUrl"]
        client.send_message(
            QueueUrl=url,
            MessageBody=(message)
        )

@app.route("/", methods=["POST"])
def hook():
    data = json.loads(request.data)

    priority = data["priority"]
    description = data["description"]

    try:
        match priority:
            case "High":
                send_to_queue({"priority": priority, "description": description}, "High")
            case "Medium":
                send_to_queue({"priority": priority, "description": description}, "Medium")
            case "Low":
                send_to_queue({"priority": priority, "description": description}, "Low")

        return Response(status=200, response="Successfully submitted ticket!")
    
    except Exception as e:
        return Response(status=205, response=f"Could not process ticket!: {e}")

if __name__ == "__main__":
    app.run()