from flask import Flask, render_template, jsonify, request
import pandas as pd
import numpy as np
import pickle
import os
import mysql.connector

conn= mysql.connector.connect(host = 'localhost' , 
                               user = 'root' , 
                               password = '' , 
                               database = 'insurancedata')


app = Flask(__name__)

# Trained model load karein
with open('model/insurance_model.pkl', 'rb') as model_file:
    model = pickle.load(model_file)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/forms')
def forms():
    return render_template('forms.html') # Updated form

@app.route('/submit_data', methods=['GET','POST'])
def submit_data():
    
    try:
        if request.method == 'GET':
            age = request.args.get('age', type=float)
            sex = request.args.get('sex')
            bmi = request.args.get('bmi', type=float)
            children = request.args.get('children', type=int)
            smoker = request.args.get('smoker')
            region = request.args.get('region')

        # Handling POST request (form-data or JSON)
        elif request.method == 'POST':
            if request.content_type == 'application/json':
                data = request.get_json()
            else:  # Handling x-www-form-urlencoded
                data = request.form.to_dict()
        # Form se data lena
        age = float(request.form['age'])
        sex = request.form['sex']
        bmi = float(request.form['bmi'])
        children = int(request.form['children'])
        smoker = request.form['smoker']
        region = request.form['region']

        # Encoding for categorical variables
        sex = 1 if sex == 'female' else 0
        smoker = 1 if smoker == 'yes' else 0
        region_map = {'southwest': 0, 'southeast': 1, 'northwest': 2, 'northeast': 3}
        region = region_map[region]

        # Prediction ke liye input prepare karein
        input_data = np.array([[age, sex, bmi, children, smoker, region]])
        prediction = model.predict(input_data)[0]
        cursor=conn.cursor()
        query = """
            INSERT INTO insurance (age,sex,bmi,children,smoker,region,charges) 
            VALUES (%s, %s, %s, %s, %s, %s,%s)
        """
        values = (age, sex, bmi, children, smoker, region,float(prediction))

        try:
            cursor.execute(query, values)
            conn.commit()  
            print("Data stored successfully in MySQL")
        except mysql.connector.Error as err:
            print("Error:", err)
        finally:
            cursor.close()
    

        return jsonify({'prediction': f"${prediction:,.2f}"})

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=1000)
