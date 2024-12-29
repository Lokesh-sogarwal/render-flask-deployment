from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests
import datetime

app = Flask(__name__)

# Replace these with your Zoho API credentials
CLIENT_ID = '1000.M5TZZI5JCFA2CVBM17W14NR90T84EX'
CLIENT_SECRET = '4d377e32a10f45f2201187f5aa559fbae06a322876'
REDIRECT_URI = 'http://localhost:5055/callback'
ACCESS_TOKEN = ''  # Initially empty; will be set after successful OAuth flow

# Base URL for Zoho Meeting API
ZOHO_MEETING_API_BASE = "https://meeting.zoho.com/api/v1"


@app.route('/')
def index():
    # Check if the access token is available; if not, redirect to the login page
    if not ACCESS_TOKEN:
        return redirect(url_for('login'))
    return render_template('index.html')


@app.route('/login')
def login():
    # Redirect the user to Zoho OAuth login page
    auth_url = f"https://accounts.zoho.com/oauth/v2/auth?client_id={CLIENT_ID}&response_type=code&scope=ZohoMeeting.fullaccess.all&redirect_uri={REDIRECT_URI}"
    return redirect(auth_url)


@app.route('/create_meeting', methods=['POST'])
def create_meeting():
    # Check if the access token is available
    if not ACCESS_TOKEN:
        return jsonify({"error": "Access token not set. Please authenticate first."}), 400

    meeting_topic = request.form.get('topic')
    start_time = request.form.get('start_time')  # Format: YYYY-MM-DDTHH:mm:ss
    duration = int(request.form.get('duration'))  # In minutes

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "meetingTopic": meeting_topic,
        "startDate": start_time,
        "duration": duration,
        "timezone": "UTC"
    }

    try:
        response = requests.post(f"{ZOHO_MEETING_API_BASE}/meetings", headers=headers, json=data)

        if response.status_code == 201:
            meeting_data = response.json()
            return render_template('meeting.html', meeting=meeting_data)
        else:
            return jsonify({"error": response.json()}), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500


@app.route('/callback')
def callback():
    code = request.args.get('code')
    if code:
        token_url = "https://accounts.zoho.com/oauth/v2/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
            "code": code
        }
        try:
            response = requests.post(token_url, data=data)
            print(f"Token Response: {response.json()}")  # Print the response to see its content

            if response.status_code == 200:
                global ACCESS_TOKEN
                ACCESS_TOKEN = response.json().get('access_token')

                # Log the access token for debugging purposes
                print(f"New Access Token: {ACCESS_TOKEN}")

                # Redirect to the main page after success
                return redirect(url_for('index'))
            else:
                return jsonify(
                    {"error": "Failed to get access token", "details": response.json()}), response.status_code
        except requests.exceptions.RequestException as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "No code received"}), 400


if __name__ == '__main__':
    app.run(debug=True, port=5055)
