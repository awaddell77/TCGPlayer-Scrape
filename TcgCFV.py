from TcgPlayer import *

class TcgCfv(TcgPlayer):
    def __init__(self, game, url):
        super().__init__(game, url)
    def descriptorGrab(self, rows, n_d):
        for i in range(0, len(rows)):
            crit = re.sub('\n', '' , rows[i].text)
            if crit == "Description:": n_d["Card Effect"] = re.sub('\n', ' ', rows[i].find_next('dd').text)
            elif crit == "Unit / Grade / Skill:":
                info = re.sub('\n', ' ', rows[i].find_next('dd').text)
                data = info.split(' / ')
                n_d["Unit"] = data[0]
                n_d["Grade / Skill"] = data[1] + ' / ' + data[2]
            elif crit == "Critical / Trigger:":
                info = re.sub('\n', ' ', rows[i].find_next('dd').text)
                data = info.split(" / ")
                n_d["Critical"] = data[0]
                n_d["Trigger"] = data[1]
            elif crit == "Critical:":
                info = re.sub('\n', ' ', rows[i].find_next('dd').text)
                data = info.replace('/','').strip(' ')
                n_d["Critical"] = data
            elif crit == "Nation / Race / Clan:":
                info = re.sub('\n', ' ', rows[i].find_next('dd').text)
                data = info.split(' / ')
                n_d["Nation"] = data[0]
                n_d["Race"] = data[1]
                n_d["Clan"] = data[2]
            elif crit == "Power / Shield:":
                info = re.sub('\n', ' ', rows[i].find_next('dd').text)
                data = info.split(' / ')
                n_d["Power"] = data[0]
                n_d["Shield"] = data[1]
            elif crit == "Number - Rarity:":
                info = re.sub('\n', ' ', rows[i].find_next('dd').text)
                data = info.split(' - ')
                n_d["Card Number"] = data[0].strip(' ')
                n_d["Rarity"] = data[1].strip(' ')
            else:
                n_d[re.sub('\n', '' , rows[i].text)] = re.sub('\n', ' ', rows[i].find_next('dd').text)
