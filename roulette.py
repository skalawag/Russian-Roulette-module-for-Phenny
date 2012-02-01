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

    def get_my_stats(self, who):
        res = []
        records = self.record[who]
        for key in records.keys():
            rec = who + ' vs. ' + key
            res.append("%d:%d  %s" % (records[key], self.record[key][who], rec))
        return res
                
    def update_players(self, winner, loser):
        # each player records only his own wins against each
        # opponent.  This assumes that an entry exists for each
        # player and each opponent under that player.
        self.record[winner][loser] += 1

    def get_players_records(self, player1, player2):
        p1_v_p2 = self.record[player1][player2]
        p2_v_p1 = self.record[player2][player1]
        return "%12s: %2d %12s: %2d" % (player1, p1_v_p2, player2, p2_v_p1)

    def get_all_stats(self):
        # returns a list of annoucement strings suitable for
        # phenny.say
        all = self.record.keys()
        res = []
        # this is ugly because of my choice above.
        for player in all:
            for opponent in self.record[player].keys():
                if self.get_players_records(opponent, player) not in res:
                    res.append(self.get_players_records(player, opponent))
        return res

class game():
    def __init__(self):
        self.statistics = stats()
        self.players = []
        self.loaded_cylindar = None
        self.bullet = None
        self.game_ongoing = 0
        self.challenge_made = 0
        self.challenger = None
        self.challenged = None
        self.result = None
        self.time_of_challenge = None # set an expiry on challenge
                                      # (not implemented)
        self.winner = None 
        self.loser = None


    def report_score(self,phenny, winner,loser):
        # how to report this? 
        phenny.say(self.statistics.get_players_records(winner, loser))

    def update_score(self, winner, loser):
        # Update the records of the winner
        self.statistics.update_players(winner, loser)

    def reset(self):
        self.players = []
        self.loaded_cylindar = None
        self.bullet = None
        self.game_ongoing = 0
        self.challenge_made = 0
        self.challenger = None
        self.challenged = None
        self.result = None
        self.time_of_challenge = None
        self.winner = None
        self.loser = None

g = game()    

relief = ["%s wipes the sweat from his brow.",
          "I think %s peed his pants.",
          "%s weeps a tear of relief.",
          ]
exclamations = ["Holy, cow! %s blew his head off!",
                "OH SNAP! %s brain matter is everywhere!",
                "%s falls to the floor like a sack of flour!",
                "%s does the obituary mambo!",
                ]
change = ["%s, it's your turn.", "%s, wipe that smirk off your face. It's your turn!"]

def play_game(phenny):
    # setup
    random.shuffle(g.players)
    g.loaded_cylindar = random.choice([1, 2, 3])
    g.game_ongoing = 1

    # Announce first player
    phenny.say("A coin toss will decide the first player....")
    time.sleep(2)
    phenny.say("%s, you win!" % (g.players[0]))

    while 1:
        # `spin' cylindar
        spin = random.choice([1, 2, 3])
        phenny.say("%s spins the cylinder..." % (g.players[0]))
        time.sleep(3)

        # pull trigger
        phenny.say("%s pulls the trigger!" % (g.players[0]))
        if g.loaded_cylindar == spin:
            g.result = 1
        else: 
            g.result = 0

        # announce result
        if g.result == 1:
            
            # update winner, loser and score
            g.winner = g.players[1] # survivor
            g.loser = g.players[0]
            g.update_score(g.winner, g.loser)

            # make announcements and cleanup
            phenny.say(random.choice(['BANG!', 'KA-POW', 'BOOM!', 'BAM!']))
            time.sleep(1)
            g.game_ongoing = 0
            phenny.say(random.choice(exclamations) % (g.players[0]))
            phenny.say("Congratulations, %s, you are the winner." % (g.players[1]))
            g.report_score(phenny, g.winner, g.loser) 
            break
        else:
            phenny.say('CLICK')
            time.sleep(1)
            phenny.say(random.choice(relief) % (g.players[0]))
            g.players = [g.players[1], g.players[0]]


def challenge(phenny, input):
    g.time_of_challenge = time.time()
    g.challenger = input.nick.strip()
    g.challenge_made = 1
    g.challenged = input.group(2).strip()
    g.statistics.check(g.challenger, g.challenged) # ADDED
    phenny.say("%s challenged %s to Russian Roulette!" % (g.challenger, g.challenged))
    phenny.say("%s, do you accept?" % (g.challenged))
challenge.commands = ['callout', 'roulette']

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
    insults = ['%s, %s is yellow and you win.',
           '%s, %s is a fraidy-cat, and you win.',
           '%s, %s is a yellow, and you win.',
           '%s, %s is going to run home and cry --- you win by default.',
           ]
    if g.challenge_made == 0:
        phenny.say("%s, there has been no challenge to Russian Roulette. Get a life!" %s (input.nick))
    elif g.challenge_made == 1 and input.nick != g.challenged:
        phenny.say("%s, let %s speak for himself!" % (input.nick, g.challenged))
    else:
        insult = random.choice(insults)
        phenny.say(insult % (g.challenger, input.nick))
decline.commands = ['decline', 'no']

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

def rstat_me(phenny, input):
    res = g.statistics.get_my_stats(input.nick)
    for item in res:
        phenny.say(item)
rstat_me.commands = ['rstat-me','rstats-me']                           

def rstat(phenny, input):
    try:
        names = input.group(2).split()
        phenny.say(g.statistics.get_players_records(names[0], names[1]))
    except:
        phenny.say("%s, try giving me two nicks" % (input.nick))
rstat.commands = ['rstat']
        
def get_stats_for_all(phenny, input):
    stats = g.statistics.get_all_stats()
    for item in stats:
        phenny.say(item)
get_stats_for_all.commands = ['roulette-stats', 'r-stats', 'rstats']

if __name__ == '__main__':
    print __doc__
