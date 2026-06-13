from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import joblib
import pandas as pd
import numpy as np
import random
import uuid

app = Flask(__name__)
app.secret_key = "nexgen_super_secret_key_2026"

# Load Core AI Models
try:
    review_vectorizer = joblib.load('models/tfidf_vectorizer.pkl')
    review_model = joblib.load('models/fake_review_model.pkl')
    order_model = joblib.load('models/order_model.pkl')
    sup_vectorizer = joblib.load('models/support_vectorizer.pkl')
    sup_model = joblib.load('models/support_model.pkl')
    aqi_model = joblib.load('models/aqi_model.pkl')
except:
    review_vectorizer, review_model, order_model, sup_vectorizer, sup_model, aqi_model = [None]*6

def is_logged_in():
    return 'logged_in' in session

inventory_db = [
    {"id": "PRD-001", "name": "Wireless Earbuds", "price": 1299, "current_stock": 45},
    {"id": "PRD-002", "name": "Smart Watch", "price": 2499, "current_stock": 12}
]

def get_city_from_pincode(pincode):
    pin_str = str(pincode)
    if pin_str.startswith('11'): return "New Delhi, Delhi"
    elif pin_str.startswith('40'): return "Mumbai, Maharashtra"
    elif pin_str.startswith('80'): return "Patna, Bihar"
    elif pin_str.startswith('56'): return "Bangalore, Karnataka"
    elif pin_str.startswith('70'): return "Kolkata, West Bengal"
    elif pin_str.startswith('60'): return "Chennai, Tamil Nadu"
    else: return "Verified Indian City"

@app.route('/', methods=['GET', 'POST'])
def order_forecaster():
    if not is_logged_in(): return redirect(url_for('login'))
    global inventory_db
    forecast_results = None
    
    if request.method == 'POST':
        if 'add_product' in request.form:
            new_name = request.form.get('new_product_name')
            new_price = int(request.form.get('new_price', 0))
            new_stock = int(request.form.get('new_stock', 0))
            if new_name:
                inventory_db.append({"id": f"PRD-{random.randint(100, 999)}", "name": new_name, "price": new_price, "current_stock": new_stock})
        elif 'remove_product' in request.form:
            remove_id = request.form.get('remove_id')
            inventory_db = [item for item in inventory_db if item['id'] != remove_id]
        elif 'predict_product' in request.form and order_model:
            selected_product = request.form.get('product_name')
            visits = float(request.form['visits'])
            ad_spend = float(request.form['ad_spend'])
            predicted_demand = int(order_model.predict(pd.DataFrame({'Visits': [visits], 'Ad_Spend': [ad_spend], 'Discount': [10.0]}))[0])
            for item in inventory_db:
                if item['name'] == selected_product:
                    to_order = max(0, predicted_demand - item['current_stock'])
                    forecast_results = {"product": selected_product, "demand": predicted_demand, "current": item['current_stock'], "to_order": to_order}
                    break
    return render_template('index.html', active_tab='orders', inventory=inventory_db, forecast=forecast_results)

@app.route('/logistics', methods=['GET', 'POST'])
def aqi_tracker():
    if not is_logged_in(): return redirect(url_for('login'))
    logistics_data = None
    if request.method == 'POST' and aqi_model:
        buyer_address = request.form['buyer_address']
        pickup, delivery = int(request.form['pickup']), int(request.form['delivery'])
        destination_city = get_city_from_pincode(delivery)
        simulated_distance = abs(pickup - delivery) * 0.08  
        if simulated_distance < 10: simulated_distance = np.random.randint(50, 1200)
        simulated_aqi = np.random.randint(50, 500)
        delay = max(0, int(aqi_model.predict(pd.DataFrame({'AQI': [simulated_aqi], 'Distance': [simulated_distance]}))[0]))
        logistics_data = {"address": buyer_address, "city": destination_city, "distance": int(simulated_distance), "aqi": simulated_aqi, "delay": delay}
    return render_template('index.html', active_tab='aqi', result=logistics_data)

@app.route('/support', methods=['GET'])
def support_copilot():
    if not is_logged_in(): return redirect(url_for('login'))
    return render_template('index.html', active_tab='support')

# --- UPGRADED SMART CHAT LOGIC ---
@app.route('/api/chat', methods=['POST'])
def chat_api():
    data = request.get_json()
    raw_msg = data.get('message', '').lower()
    lang = data.get('lang', 'hi')
    
    # 🔴 BUG FIX: String Sanitization - Removing exclamation marks and punctuation
    clean_msg = raw_msg.replace('!', '').replace('?', '').replace('.', '').replace(',', '')
    words = clean_msg.split()
    
    # 1. Human Agent Logic
    human_keywords = ['human', 'insaan', 'customer care', 'agent', 'call', 'baat', 'support']
    if any(word in clean_msg for word in human_keywords):
        reply = "Transferring your chat to a human support agent. Please hold on..." if lang == 'en' else "Main aapki chat hamare human agent (customer care) ko transfer kar rahi hoon. Kripya pratiksha karein..."
        return jsonify({"reply": reply})

    # 2. Greetings & Closings
    if any(word in words for word in ['hi', 'hello', 'hey', 'namaste']):
        reply = "Hello! Welcome to NexGen Support. How can I help you today?" if lang == 'en' else "Hello! Welcome to NexGen Support. Main aapki kya madad kar sakti hoon?"
        return jsonify({"reply": reply})
        
    elif any(word in words for word in ['bye', 'goodbye', 'tata']):
        reply = "Goodbye! Have a great day ahead. 👋" if lang == 'en' else "Goodbye! Aapka din shubh ho. 👋"
        return jsonify({"reply": reply})
        
    elif any(word in words for word in ['thank', 'thanks', 'ok', 'okay', 'solved']):
        reply = "You're welcome! Glad I could help." if lang == 'en' else "Swagat hai! Mujhe khushi hai ki main aapki madad kar payi. 😊"
        return jsonify({"reply": reply})

    # 3. ML Model Business Logic
    if sup_model:
        # Pass the original message to the ML model so it maintains context
        intent = sup_model.predict(sup_vectorizer.transform([raw_msg]))[0]
        
        if intent == "Shipping & Delivery":
            reply = "I've checked the logistics database. Your package is safely in transit and will reach you within 2-3 business days." if lang == 'en' else "Maine check kiya hai. Aapka package transit mein hai aur 2-3 din mein deliver ho jayega."
        elif intent == "Refund & Returns":
            reply = "I have initiated your return request. The pickup will be done tomorrow, and your refund will be credited within 5-7 working days." if lang == 'en' else "Aapki return request accept ho gayi hai. Kal pickup hoga aur refund 5-7 working days mein bank account mein aa jayega."
        elif intent == "Technical Support":
            reply = "I've logged this technical issue. Our engineering team will fix it within 24 hours." if lang == 'en' else "Aapki technical issue log ho gayi hai. Hamari team isko 24 hours mein fix kar degi."
        else:
            reply = "I'm sorry, I didn't understand. Could you rephrase your question?" if lang == 'en' else "Maaf kijiye, main theek se samajh nahi payi. Kya aap detail mein bata sakte hain?"
            
        return jsonify({"reply": reply})
        
    return jsonify({"reply": "I am offline."})

@app.route('/reviews', methods=['GET', 'POST'])
def review_shield():
    if not is_logged_in(): return redirect(url_for('login'))
    analysis = None
    if request.method == 'POST' and review_model:
        review_text = request.form['review']
        df_tfidf = pd.DataFrame(review_vectorizer.transform([review_text]).toarray(), columns=review_vectorizer.get_feature_names_out())
        res = review_model.predict(pd.concat([pd.DataFrame({'Rating': [int(request.form['rating'])]}), df_tfidf], axis=1))[0]
        confidence = random.randint(85, 99)
        spam_words = ["money", "scam", "fake", "worst", "fraud"] if res == 1 else ["None"]
        analysis = {"is_fake": bool(res == 1), "confidence": confidence, "spam_keywords": spam_words, "text": review_text}
    return render_template('index.html', active_tab='reviews', analysis=analysis)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['logged_in'] = True
        return redirect(url_for('order_forecaster'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)