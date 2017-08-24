from TcgPlayer import *

class TcgDragoborne(TcgPlayer):
    def __init__(self, game, url):
        super().__init__(game, url)

    def headerFix(self, lst):
        #overriding parent headerFix method
        x = lst[:]
        d = {"Name":"Card Name", "Description":"Card Text", "Number":"Card Number"}
        print('Overriden')
        for i in range(0, len(x)):
            x[i] = x[i].replace(':', '')
            x[i] = d.get(x[i], x[i])
        return x
