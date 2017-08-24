from TcgPlayer import *

class TcgDragoborne(TcgPlayer):
    def __init__(self, game, url):
        super().__init__(game, url)

    def headerFix(self, x):
        d = {"Name":"Card Name", "Description":"Card Text", "Number":"Card Number"}
        for i in x: i = i.replace(':', '')
        for i in x: i = d.get(i, i)
        return x
