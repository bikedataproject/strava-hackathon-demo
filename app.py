from flask import Flask, render_template, redirect, session, request, url_for
from os import urandom
import requests
import json
import polyline

app = Flask(__name__)
app.secret_key = urandom(80)


@app.route('/')
def home():
    if 'clientid' in session and 'clientsecret' in session:
        return redirect('/user/routes')
    return render_template('clientinfo.html')


@app.route('/set/client/data', methods=['GET', 'POST'])
def set_client_id():
    if request.method == 'POST':
        if 'clientid' in request.form and 'clientsecret' in request.form:
            session['clientid'] = request.form['clientid']
            session['clientsecret'] = request.form['clientsecret']
            return redirect(f'https://www.strava.com/oauth/authorize?client_id={session["clientid"]}&response_type=code&redirect_uri=http://pickleplexbootcamp.ddns.net:5000/get/bearer&approval_prompt=force&scope=activity:read_all')
    return redirect('/')


@app.route('/get/bearer')
def get_bearer():
    code = request.args.get('code')
    if code is not None:
        response = requests.request(
            "POST", "https://www.strava.com/oauth/token", data={'client_id': session['clientid'],
                                                                'client_secret': session['clientsecret'],
                                                                'code': code,
                                                                'grant_type': 'authorization_code'})

        session['bearertoken'] = json.loads(response.text)['access_token']
        return redirect('/user/routes')
    return redirect('/')


@app.route('/user/routes')
def show_routes():
    if 'bearertoken' in session:
        response = requests.request(
            "GET", "https://www.strava.com/api/v3/athlete/activities", headers={'Authorization': f'Bearer {session["bearertoken"]}'}
        )
        data = json.loads(response.text)
        for d in data:
            d['map']['summary_polyline_array'] = polyline.decode(
                d['map']['summary_polyline'], geojson=True)
        print(session['bearertoken'])
        return render_template('routes.html', data=data)
    return redirect('/')


if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0', debug=True)
