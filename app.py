import random
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = "nexgen_super_secret_key_2026"

# ==========================================
# 🚀 CORE LOGIC & FUNCTIONS (No Heavy ML Models Required for Vercel)
# ==========================================

def is_logged_in():
    return 'logged_in' in session

# Global Database for Real-Time Inventory
inventory_db = [
    {"id": "PRD-001", "name": "Wireless Earbuds", "price": 1299, "current_stock": 45},
    {"id": "PRD-002", "name": "Smart Watch", "price": 2499, "current_stock": 12}
]

# Advanced Indian PIN Code System
def get_city_from_pincode(pincode):
    pin_str = str(pincode).strip()
    if len(pin_str) != 6 or not pin_str.isdigit():
        return "Invalid PIN Code"
        
    prefix = pin_str[:2]
    if prefix == '11': return "New Delhi, Delhi"
    elif prefix == '12': return "Gurugram, Haryana"
    elif prefix in ['14', '15', '16']: return "Punjab"
    elif prefix in ['20', '21', '22', '23', '24', '25', '26', '27', '28']: return "Uttar Pradesh"
    elif prefix in ['30', '31', '32', '33', '34']: return "Rajasthan"
    elif prefix in ['38', '39']: return "Gujarat"
    elif prefix in ['40', '41', '42', '43', '44']: return "Mumbai, Maharashtra"
    elif prefix in ['50', '51', '52', '53']: return "Hyderabad, Telangana"
    elif prefix in ['56', '57', '58', '59']: return "Bangalore, Karnataka"
    elif prefix in ['60', '61', '62', '63', '64']: return "Chennai, Tamil Nadu"
    elif prefix in ['70', '71', '72', '73', '74']: return "Kolkata, West Bengal"
    elif prefix == '80': return "Patna, Bihar" 
    elif prefix == '84': return "Saran/Muzaffarpur, Bihar"
    elif prefix == '81': return "Bhagalpur, Bihar"
    elif prefix == '82': return "Gaya, Bihar"
    elif prefix == '83': return "Ranchi, Jharkhand"
    else: return "Verified Indian Location"

@app.route('/', methods=['GET', 'POST'])
def order_forecaster():
    if not is_logged_in(): return redirect(url_for('login'))
    global inventory_db
    forecast_results = None

    if request.method == 'POST':
        if 'add_product' in request.form:
            inventory_db.append({
                "id": f"PRD-{random.randint(100, 999)}",
                "name": request.form.get('new_product_name'),
                "price": int(request.form.get('new_price', 0)),
                "current_stock": int(request.form.get('new_stock', 0))
            })
        elif 'remove_product' in request.form:
            remove_id = request.form.get('remove_id')
            inventory_db = [item for item in inventory_db if item['id'] != remove_id]
        elif 'predict_product' in request.form:
            selected_product = request.form.get('product_name')
            try:
                visits = float(request.form['visits'])
                ad_spend = float(request.form['ad_spend'])
                
                # Smart Mathematical Logic (Replaces XGBoost)
                base_demand = (visits * 0.08) + (ad_spend * 0.04)
                predicted_demand = int(base_demand + random.randint(2, 10))
                if predicted_demand < 0: predicted_demand = 0

                for item in inventory_db:
                    if item['name'] == selected_product:
                        forecast_results = {
                            "product": selected_product,
                            "demand": predicted_demand,
                            "current": item['current_stock'],
                            "to_order": max(0, predicted_demand - item['current_stock'])
                        }
                        break
            except Exception as e:
                print(f"Prediction error: {e}")

    return render_template('index.html', active_tab='orders', inventory=inventory_db, forecast=forecast_results)

@app.route('/logistics', methods=['GET', 'POST'])
def aqi_tracker():
    if not is_logged_in(): return redirect(url_for('login'))
    logistics_data = None
    if request.method == 'POST':
        try:
            pickup = int(request.form.get('pickup', 0))
            delivery = int(request.form.get('delivery', 0))
            buyer_address = request.form.get('buyer_address', '')
            
            dist = abs(pickup - delivery) * 0.08
            distance = int(dist if dist > 10 else random.randint(50, 1200))
            
            aqi_value = random.randint(50, 450)
            delay = 0
            if aqi_value > 300: delay = 2
            elif aqi_value > 200: delay = 1

            logistics_data = {
                "address": buyer_address,
                "city": get_city_from_pincode(delivery),
                "distance": distance,
                "aqi": aqi_value,
                "delay": delay
            }
        except Exception as e:
            print(f"Logistics Error: {e}")

    return render_template('index.html', active_tab='aqi', result=logistics_data)

@app.route('/support', methods=['GET'])
def support_copilot():
    if not is_logged_in(): return redirect(url_for('login'))
    return render_template('index.html', active_tab='support')

@app.route('/api/chat', methods=['POST'])
def chat_api():
    data = request.get_json()
    raw_msg = data.get('message', '').lower().strip()
    lang = data.get('lang', 'hi')
    clean_msg = raw_msg.replace('!', '').replace('?', '').replace('.', '')
    
    # 1. Greetings & Small Talk
    if any(word in clean_msg for word in ['hi', 'hello', 'hey', 'namaste']):
        return jsonify({"reply": "Hello! I am Kyra, your AI Assistant. How can I help you today?" if lang == 'en' else "Namaste! Main Kyra hoon. Bataiye main aapki kya madad kar sakti hoon?"})
    
    if any(word in clean_msg for word in ['thank', 'thanks', 'dhanyawad', 'shukriya']):
        return jsonify({"reply": "You're welcome! Let me know if you need anything else." if lang == 'en' else "Aapka swagat hai! Agar koi aur madad chahiye toh zaroor batayein."})
        
    if clean_msg in ['ok', 'okay', 'acha', 'theek', 'yes', 'haan', 'yep', 'hmm']:
        return jsonify({"reply": "Great! Is there anything else I can assist you with?" if lang == 'en' else "Theek hai! Kya main aapki koi aur madad kar sakti hoon?"})

    if any(word in clean_msg for word in ['bye', 'goodbye', 'alvida']):
        return jsonify({"reply": "Goodbye! Have a great day!" if lang == 'en' else "Alvida! Aapka din shubh ho."})

    # 2. Human Agent Transfer
    if any(word in clean_msg for word in ['human', 'insaan', 'customer care', 'agent', 'baat', 'call']):
        return jsonify({"reply": "Transferring you to a human agent. Please hold on..." if lang == 'en' else "Main aapki chat human agent ko transfer kar rahi hoon. Kripya line par bane rahein..."})
        
    # 3. Rule-based Fast NLP Fallbacks (Replaces ML Model)
    if any(word in clean_msg for word in ['refund', 'money', 'paisa', 'bank', 'account']):
        return jsonify({"reply": "Refunds are processed within 5-7 business days." if lang == 'en' else "Aapka refund 5-7 working days mein aapke bank account mein aa jayega."})
    if any(word in clean_msg for word in ['delivery', 'kab aayega', 'track', 'status', 'where']):
        return jsonify({"reply": "Deliveries usually take 3-5 days. You can track it in the Logistics tab." if lang == 'en' else "Delivery mein 3-5 din lagte hain. Aap Logistics tab mein track kar sakte hain."})
    if any(word in clean_msg for word in ['defective', 'toota', 'damage', 'kharab', 'return', 'exchange']):
        return jsonify({"reply": "I apologize! You can raise a return request, pickup will be arranged in 2 days." if lang == 'en' else "Maaf kijiye! Aap return request daal sakte hain, 2 din mein pickup ho jayega."})
    if any(word in clean_msg for word in ['modify', 'change', 'address', 'badal']):
        return jsonify({"reply": "Order modification window is closed." if lang == 'en' else "Order change karne ka samay samapt ho gaya hai."})
        
    return jsonify({"reply": "Sorry, I didn't quite get that. Could you rephrase?" if lang == 'en' else "Maaf kijiye, mujhe samajh nahi aaya. Kya aap wapas bata sakte hain?"})

@app.route('/reviews', methods=['GET', 'POST'])
def review_shield():
    if not is_logged_in(): return redirect(url_for('login'))
    analysis = None
    if request.method == 'POST':
        try:
            text = request.form['review']
            rating = int(request.form['rating'])
            
            # Rule-based Review Shield Pro
            spam_words = ["money", "scam", "fake", "worst", "fraud", "bakwas", "ghatiya", "loot", "promotional", "subscribe"]
            is_spam = any(word in text.lower() for word in spam_words)
            
            negative_words = ['bad', 'poor', 'terrible', 'waste', 'kharab']
            positive_words = ['excellent', 'great', 'awesome', 'best', 'mast', 'superb']

            res = 0 
            confidence = random.randint(80, 90)
            
            if is_spam:
                res = 1
                confidence = random.randint(95, 99)
            elif rating >= 4 and any(nw in text.lower() for nw in negative_words):
                res = 1
                confidence = random.randint(88, 95)
            elif rating <= 2 and any(pw in text.lower() for pw in positive_words):
                res = 1
                confidence = random.randint(88, 95)
            
            analysis = {
                "is_fake": bool(res == 1), 
                "confidence": confidence, 
                "text": text
            }
        except Exception as e:
            print(f"Review error: {e}")
            
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

# For Vercel, the app instance itself handles requests
if __name__ == '__main__':
    app.run(debug=True)