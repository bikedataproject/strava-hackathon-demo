from flask import Flask, render_template, redirect, session, request, url_for
from os import urandom, environ
import requests
import json
import polyline
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.secret_key = urandom(80)


@app.route('/')
def home():
    return redirect(f'https://www.strava.com/oauth/authorize?client_id={environ["clientid"]}&response_type=code&redirect_uri={environ["endpoint"]}/get/bearer&approval_prompt=force&scope=activity:read_all')

@app.route('/get/bearer')
def get_bearer():
    code = request.args.get('code')
    if code is not None:
        response = requests.request(
            "POST", "https://www.strava.com/oauth/token", data={'client_id': environ["clientid"],
                                                                'client_secret':environ["clientsecret"],
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
        logging.info(data)
        trajectories = []
        for d in data:
            trajectories.append(polyline.decode(
                d['map']['summary_polyline'], geojson=True))
        return render_template('routes.html', data=data, mapboxtoken=environ['mapboxtoken'], trajectories=trajectories)
    return redirect('/')

@app.route('/reset')
def reset_session():
    for key in ['bearertoken']:
        if key in session:
            del session[key]
    return redirect('/')


if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0', debug=True)
