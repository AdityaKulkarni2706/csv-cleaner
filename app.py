from flask import Flask, request, render_template, jsonify, redirect, url_for, send_file
from werkzeug.utils import secure_filename
import os
import AgentLibrary
import csv

app = Flask(__name__)

@app.route("/")

def render():
    return render_template("cleaner.html")

@app.route("/accept_file", methods = ["POST"])

def get_file():

    
    uploaded_file = request.files.get('file')
    user_rule = request.form.get('rule')
    print(f"This is the user rule : {user_rule}")

    if uploaded_file and uploaded_file.filename.endswith('.csv'):
        filename = f"uploads/{secure_filename(uploaded_file.filename)}"
        uploaded_file.save(filename)

        return process_file(filename, user_rule)
    
    return jsonify({"status" : "failure"})




def process_file(csv_file_path, user_rule):

    orch_object = AgentLibrary.Orchestrator(csv_file_path, user_rule)
    final_csv_path = orch_object.callAgents()
    if final_csv_path:

        print("final file made")
        return send_file(final_csv_path, as_attachment=True)
    
    print("failure")
    return jsonify({"status": "failure", "filename": "NA"})


if __name__ == "__main__":
    app.run(debug=True)