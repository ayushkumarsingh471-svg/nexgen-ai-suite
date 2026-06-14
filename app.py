import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import joblib
import pandas as pd
import numpy as np
import random

app = Flask(__name__)
app.secret_key = "nexgen_super_secret_key_2026"

# Root Directory Setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load Models
def load_model(filename):
    return joblib.load(os.path.join(BASE_DIR, 'models', filename))

try:
    review_vectorizer = load_model('tfidf_vectorizer.pkl')
    review_model = load_model('fake_review_model.pkl')
    order_model = load_model('order_model.pkl')
    sup_vectorizer = load_model('support_vectorizer.pkl')
    sup_model = load_model('support_model.pkl')
    aqi_model = load_model('aqi_model.pkl')
except Exception as e:
    print(f"Error loading models: {e}")
    review_vectorizer, review_model, order_model, sup_vectorizer, sup_model, aqi_model = [None]*6

@app.route('/', methods=['GET', 'POST'])
def order_forecaster():
    if 'logged_in' not in session: return redirect('/login')
    global inventory_db
    forecast_results = None
    if request.method == 'POST':
        if 'add_product' in request.form:
            inventory_db.append({"id": f"PRD-{random.randint(100, 999)}", "name": request.form.get('new_product_name'), "price": int(request.form.get('new_price', 0)), "current_stock": int(request.form.get('new_stock', 0))})
        elif 'remove_product' in request.form:
            inventory_db = [item for item in inventory_db if item['id'] != request.form.get('remove_id')]
        elif 'predict_product' in request.form and order_model:
            demand = int(order_model.predict(pd.DataFrame({'Visits': [float(request.form['visits'])], 'Ad_Spend': [float(request.form['ad_spend'])], 'Discount': [10.0]}))[0])
            for item in inventory_db:
                if item['name'] == request.form.get('product_name'):
                    forecast_results = {"product": item['name'], "demand": demand, "current": item['current_stock'], "to_order": max(0, demand - item['current_stock'])}
    return render_template('index.html', active_tab='orders', inventory=inventory_db, forecast=forecast_results)

# Routes for Logistics, Support, Login (Keep these as they were)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['logged_in'] = True
        return redirect('/')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
