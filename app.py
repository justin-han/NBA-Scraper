from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import re
import plotly.graph_objects as go
import json
import plotly
import requests

app = Flask(__name__)

def extract(first_name, last_name):
    last_letter = last_name[0].lower()
    last_five = last_name[0:5].lower()
    first_two = first_name[0:2].lower()

    url = f'https://www.basketball-reference.com/players/{last_letter}/{last_five}{first_two}01.html'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'}
    r = requests.get(url, headers)
    
    soup = BeautifulSoup(r.content, 'html.parser')
    return soup

seasons_year = []
points_year = []
assists_year = []
rebounds_year = []
steals_year = []
blocks_year = []

seasons2_year = []
points2_year = []
assists2_year = []
rebounds2_year = []
steals2_year = []
blocks2_year = []

# returns the dictionary for all five statistical categories for every season of the player
def transform(soup):
    seasons_year.clear()
    points_year.clear()
    assists_year.clear()
    rebounds_year.clear()
    steals_year.clear()
    blocks_year.clear()

    seasons2_year.clear()
    points2_year.clear()
    assists2_year.clear()
    rebounds2_year.clear()
    steals2_year.clear()
    blocks2_year.clear()
    years = soup.find_all('tr', id = re.compile('^per_game'))
    for year in years:
        seasons = year.find('th', {'data-stat': 'season'}).text
        points = year.find('td', {'data-stat': 'pts_per_g'}).text
        assists = year.find('td', {'data-stat': 'ast_per_g'}).text
        rebounds = year.find('td', {'data-stat': 'trb_per_g'}).text
        steals = year.find('td', {'data-stat': 'stl_per_g'}).text
        blocks = year.find('td', {'data-stat': 'blk_per_g'}).text

        seasons_year.append(seasons)
        points_year.append(float(points))
        assists_year.append(float(assists))
        rebounds_year.append(float(rebounds))
        steals_year.append(float(steals))
        blocks_year.append(float(blocks))

        seasons2_year.append(seasons)
        points2_year.append(float(points))
        assists2_year.append(float(assists))
        rebounds2_year.append(float(rebounds))
        steals2_year.append(float(steals))
        blocks2_year.append(float(blocks))
    return

def line_graph(season, points, assists, rebounds):
    x = list(range(0, len(season)))
    y1 = points
    y2 = assists    
    y3 = rebounds

    layout = go.Layout(title = f'Career points, assists, and rebounds visualized')
    trace1 = go.Scatter(x = x, y = points, mode = 'lines+markers', name = 'Points')
    trace2 = go.Scatter(x = x, y = assists, mode = 'lines+markers', name = 'Assists')
    trace3 = go.Scatter(x = x, y = rebounds, mode = 'lines+markers', name = 'Rebounds')
    data = [trace1, trace2, trace3]
    figure = go.Figure(data = data, layout = layout)
    figure.update_xaxes(ticktext = season, tickvals = x)
    return json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder)

def radar_chart(points, assists, rebounds, steals, blocks):
    categories = ['Points', 'Assists', 'Rebounds', 'Steals', 'Blocks']
    avg_points = standardize(points, 30.12)
    avg_assists = standardize(assists, 11.19)
    avg_rebounds = standardize(rebounds, 16.22)
    avg_steals = standardize(steals, 2.71)
    avg_blocks = standardize(blocks, 3.5)
    all_averages = [avg_points, avg_assists, avg_rebounds, avg_steals, avg_blocks]

    trace = go.Scatterpolar(r = all_averages, theta = categories, fill = 'toself')
    data = [trace]
    layout = go.Layout(title = f'Radar chart of all 5 statistical categories visualized', polar = {'radialaxis' : {'visible': False, 'range' : [0, 1]}})
    figure = go.Figure(data = data, layout = layout)
    return json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder)

def standardize(list, max):
    average = sum(list)/len(list)
    return average/max 

@app.route("/")
def nba_data():
    return render_template('index.html')

@app.route("/", methods=["POST"])
def nba_name():
    text = request.form['text'].split()
    first = text[0]
    last = text[1]
    player = extract(first, last)
    transform(player)
    return render_template('index.html')

@app.route("/chart1")
def chart1():
    graphJSON = line_graph(seasons_year, points_year, assists_year, rebounds_year)
    return render_template('chart.html', graphJSON = graphJSON)

@app.route("/chart2")
def chart2():
    graphJSON = radar_chart(points2_year, assists2_year, rebounds2_year, steals2_year, blocks2_year)
    return render_template('chart.html', graphJSON = graphJSON)

if __name__ == "__main__":
    app.run(debug=True)
