#! /usr/bin/env python
# coding=utf-8
"""
roulette.py - Phenny Russian Roulette Module
Copyright 2012, Mark Scala
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import random, time


class stats():
    def __init__(self):
        self.record = {}

    def check(self, player1, player2):
        if player1 in self.record.keys():
            if player2 in self.record[player1].keys():
                pass
            else:
                self.record[player1].setdefault(player2, 0)
        else:
            self.record.setdefault(player1, {player2: 0})

        if player2 in self.record.keys():
            if player1 in self.record[player2].keys():
                pass
            else:
                self.record[player2].setdefault(player1, 0)
        else:
            self.record.setdefault(player2, {player1: 0})

    def update_players(self, winner, loser):
        # each player records only his own wins against each
        # opponent.  This assumes that an entry exists for each
        # player and each opponent under that player.
        self.record[winner][loser] += 1

    def get_players_records(self, player1, player2):
        p1_v_p2 = self.record[player1][player2]
        p2_v_p1 = self.record[player2][player1]
        return "%s: %d --- %s: %d" % (player1, p1_v_p2, player2, p2_v_p1)

    def get_all_stats(self):
        # returns a list of annoucement strings suitable for
        # phenny.say
        all = self.record.keys()
        res = []
        # this is damn ugly, but ....
        for player in all:
            for opponent in self.record[player].keys():
                if self.get_players_records(opponent, player) not in res:
                    res.append(self.get_players_records(player, opponent))
        return res

class game():

    def __init__(self):
        self.statistics = stats()
        self.players = []
        self.gun = [1, 2, 3]
        self.bullet = None
        self.game_ongoing = 0
        self.challenge_made = 0
        self.challenger = None
        self.challenged = None
        self.result = None
        self.time_of_challenge = None
        self.record = {}
        self.winner = None 
        self.loser = None

    def report_score(self,phenny, winner,loser):
        # how to report this? 
        phenny.say(self.statistics.get_players_records(winner, loser))

    def update_score(self, winner, loser):
        # Update the records of the winner
        self.statistics.update_players(winner, loser)

    def reset(self):
        self.players = None
        self.gun = [1, 2, 3, 4, 5, 6]
        self.bullet = None
        self.game_ongoing = 0
        self.challenge_made = 0
        self.challenger = None
        self.challenged = None
        self.result = None
        self.time_of_challenge = None
        self.winner = None
        self.loser = None

    def spin(self, phenny):
        random.shuffle(self.gun)
        phenny.say("%s spins the cylinder..." % (self.players[0]))
        time.sleep(3)

    def pull_trigger(self, phenny):
        phenny.say("%s pulls the trigger!" % (self.players[0]))
        if self.bullet == self.gun[0]:
            self.result = "BANG!"
        else: 
            self.result = "CLICK"

    def query_player(self):
        return "%s, do you wish to play on?" % self.players[0]

    def toggle_challenge(self):
        if self.challenge_made == 0:
            self.challenge_made = 1
        else:
            self.challenge_made = 0
        
    def toggle_ongoing(self):
        if self.game_ongoing == 0:
            self.game_ongoing = 1
        else:
            self.game_ongoing = 0

    def next_player(self):
        p = self.players[0]
        self.players = [self.players[1], self.players[0]]
        return p
    
    def coin_toss(self):
        random.shuffle(self.players)
        random.shuffle(self.gun)
        self.bullet = self.gun[0]
        random.shuffle(self.gun)
        self.game_ongoing = 1

    def announce(self, phenny):
        if self.result == 'BANG!':
            self.winner = self.players[1]
            self.loser = self.players[0]
            self.update_score(self.winner, self.loser)
            phenny.say('BANG!')
            time.sleep(1)
            self.game_ongoing = 0
            phenny.say("Holy, cow! %s blew his head off!" % (self.players[0]))
            phenny.say("Congratulations, %s, you are the winner." % (self.players[1]))
            self.report_score(phenny, self.winner, self.loser) 
            time.sleep(3)
            phenny.say("Now, please, clean up this mess!")
            self.reset()
        elif self.result == "CLICK":
            phenny.say('CLICK')
            time.sleep(1)
            phenny.say("%s wipes the sweat from his brow." % (self.players[0]))

g = game()    

def play_game(phenny):
    g.coin_toss()
    phenny.say("A coin toss will decide the first player....")
    time.sleep(2)
    phenny.say("%s, you win!" % (g.players[0]))
    while 1:
        g.spin(phenny)
        g.pull_trigger(phenny)
        g.announce(phenny)
        if g.game_ongoing == 0:
            break
        else:
            g.next_player()
            phenny.say("%s, it's your turn. Good luck!" % (g.players[0]))
            time.sleep(2)

def challenge(phenny, input):
    g.time_of_challenge = time.time()
    g.challenger = input.nick.strip()
    g.challenge_made = 1
    g.challenged = input.group(2).strip()
    g.statistics.check(g.challenger, g.challenged) # ADDED
    phenny.say("%s challenged %s to Russian Roulette!" % (g.challenger, g.challenged))
    phenny.say("%s, do you accept?" % (g.challenged))
challenge.commands = ['challenge']

def accept(phenny, input):
    if g.challenge_made == 0:
        phenny.say("%s, there has been no challenge to Russian Roulette. Get a life!" %s (input.nick))
    elif g.challenge_made == 1 and input.nick != g.challenged:
        phenny.say("%s, let %s speak for himself!" % (input.nick, g.challenged))
    else:
        phenny.say("%s accepts the challenge!" % input.nick)
        phenny.say("Let the game begin!")
        g.players = [g.challenged, g.challenger]
        play_game(phenny)
accept.commands = ['accept', 'yes']

def decline(phenny, input):
    if g.challenge_made == 0:
        phenny.say("%s, there has been no challenge to Russian Roulette. Get a life!" %s (input.nick))
    elif g.challenge_made == 1 and input.nick != g.challenged:
        phenny.say("%s, let %s speak for himself!" % (input.nick, g.challenged))
    else:
        insult = insults[random.randint(0, length(insults)-1)]
        phenny.say(insult % (g.challenger, input.nick))
decline.commands = ['decline', 'no']

insults = ['%s, %s is yellow and you win.',
           '%s, %s is a fraidy-cat, and you win.',
           '%s, %s is a yellow, and you win.',
           '%s, %s is going to run home and cry --- you win by default.',
           ]

def undo_challenge(phenny, input):        
    if input.nick == g.challenger:
        g.reset()
        phenny.say("%s has retracted the challenge." % (input.nick))
    else:
        if (time.time() - g.time_of_challenge) > 300: 
            g.reset()
            phenny.say("The challenge has been expired.")
        else:
            phenny.say("The challenge has not expired, yet. Hold your horses.")
undo_challenge.commands = ['undo-roulette']

def score(phenny, input):
    try:
        names = input.group(2).split()
        phenny.say(g.statistics.get_players_records(names[0], names[1]))
    except:
        phenny.say("%s, try giving me two nicks" % (input.nick))
score.commands = ['score']
        
def get_stats_for_all(phenny, input):
    stats = g.statistics.get_all_stats()
    for item in stats:
        phenny.say(item)
get_stats_for_all.commands = ['roulette-stats', 'r-stats', 'rstats']

if __name__ == '__main__':
    print __doc__
