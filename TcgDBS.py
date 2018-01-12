from TcgPlayer import *

class TcgDbs(TcgPlayer):
    def __init__(self, game, url):
        super().__init__(game, url)
        self.rarityMap = {'Common':'C', 'Uncommon': 'UC','Rare':'R', 'Special Rare':'SPR',
        'Super Rare':'SR', 'Secret Rare':'SCR', 'Expansion Rare':'EX'}
    def descriptorGrab(self, rows, n_d):
        d = {'Description':'Skill', 'Number':'Card Number','Card Type':'Type','Special Trait':'Special Traits', 'Name':'Card Name'}
        for i in range(0, len(rows)):
            crit = re.sub('\n', '' , rows[i].text).replace(":",'')
            if crit == "Rarity":
                rarityVal = re.sub('\n', ' ', rows[i].find_next('dd').text)
                n_d["Rarity"] = self.rarityMap.get(rarityVal, rarityVal)
            else: n_d[d.get(crit, crit)] = re.sub('\n', ' ', rows[i].find_next('dd').text)
