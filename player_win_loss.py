import urllib.request
from bs4 import BeautifulSoup
from functools import reduce


def find_win_loss_averages(player_name, target_split="recent"):
	print(player_name)
	url = "https://lol.gamepedia.com/Special:RunQuery/MatchHistoryPlayer?MHP%5Bname%5D=" + player_name + "&MHP%5Blimit%5D=20&MHP%5Btext%5D=No&pfRunQueryFormName=MatchHistoryPlayer"
	html_doc = urllib.request.urlopen(url)

	soup = BeautifulSoup(html_doc, 'html.parser')
	player_table = soup.find_all('table')[0]

	table_rows = player_table.find_all('tr')
	print(len(table_rows))

	header = table_rows[1].find_all("th")
	header_text = [element.text.strip() for element in header]
	kill_index = header_text.index("K")
	death_index = header_text.index("D")
	assist_index = header_text.index("A")
	cs_index = header_text.index("CS")
	tournament_index = header_text.index("Tournament") #1
	useful_index = [kill_index, death_index, assist_index, cs_index]
	#print(table_rows)

	if target_split == "recent":
		target_split = table_rows[3].find_all("td")[1].text.strip()
	print(target_split) #= "LCS 2019 Spring Playoffs"#"LCS 2019 Spring"
	target_split = "NA LCS 2019 Spring"
	win_color = "#C6EFCE"
	lose_color = "#FFC7CE"

	wins = []
	losses = []


	for i in range(3, len(table_rows)-1):
		row_elements = table_rows[i].find_all("td")
		split = row_elements[1].text.strip()

		if split == target_split:
			game_text = [element.text.strip() for element in row_elements]
			useful = [int(game_text[j]) for j in useful_index]
			score = useful[0] * 3 - useful[1] + useful[2] * 2 + useful[3] * 0.02

			color_string = table_rows[i]["style"].split(";")[0].split(":")[1]

			if color_string == "var(--color-winner)":
				wins.append(score)
			else:
				losses.append(score)

	win_avg = reduce(lambda x, y: x + y, wins) / len(wins)
	loss_avg = reduce(lambda x, y: x + y, losses) / len(losses)

	return (player_name, wins, win_avg, losses, loss_avg)


players = ["Doublelift", "Impact", "Jensen", "CoreJJ", "Xmithie"]


#find_win_loss_averages("Arrow")
sorted_players = []

for player in players:
	results = find_win_loss_averages(player)
	sorted_players.append((results[0], results[2]))

sorted_players = sorted(sorted_players, key=lambda x: x[1], reverse=True)
print(sorted_players)

#print(find_win_loss_averages("Doublelift"))

results = {
	"Jensen": 140.68,
	"Doublelift": 144.7,
	"Xmithie": 114.76,
	"Impact": 141.34,
	"CoreJJ": 121.2
}

