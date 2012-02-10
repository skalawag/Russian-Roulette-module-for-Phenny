#! /usr/bin/env python
# coding=utf-8
"""
roulette.py - Phenny Russian Roulette Module
Copyright 2012, Mark Scala
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

"""
* DONE: test .abort function
* DONE: grant two points for an abort
* DONE: format .rstats like rstats-me for a cleaner look
* DONE: add simple persistence
* TODO: auto-cull 0:0 stats
* TODO: .rematch! (on a timer?), double or nothing option (with !)
* TODO: choice of weapons: double barrel shotgun?
* TODO: timer on challenges
* TODO: change decline messages so they don't say "win"
"""

import random, time, shelve

class stats():
    def __init__(self):
        self.db = shelve.open('roulette.db')
        try:
            self.record = self.db['roulette']
        except:
            self.record = {}
        self.db.close()

    def refresh_db(self):
        self.db = shelve.open('roulette.db')
        self.record = self.db['roulette'] 
        self.db.close()


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
        try:
            records = self.record[who]
        except:
            return None
        wins = 0
        losses = 0
        for key in records.keys():
            rec = who + ' vs. ' + key
            wins += records[key]
            losses += self.record[key][who]
            res.append("%d:%d  %s" % (records[key], self.record[key][who], rec))
        res.append("%d:%d  Overall" % (wins, losses))
        return res

    def update_players(self, winner, loser, abort=0):
        # each player records only his own wins against each
        # opponent.  This assumes that an entry exists for each
        # player and each opponent under that player.
        if abort:
            self.record[winner][loser] += 2
        else:
            self.record[winner][loser] += 1
            self.refresh_db()

    def get_players_records(self, player1, player2):
        p1_v_p2 = self.record[player1][player2]
        p2_v_p1 = self.record[player2][player1]
        return "%d:%d  %s vs %s" % (p1_v_p2, p2_v_p1, player1, player2)

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
        self.challenge_made = 0
        self.challenger = None
        self.challenged = None
        self.result = None
        self.time_of_challenge = None # set an expiry on challenge
                                      # (not implemented)
        self.winner = None 
        self.loser = None
        self.abort = 0
        self.game_ongoing = 0


    def report_score(self,phenny, winner,loser):
        # how to report this? 
        phenny.say(self.statistics.get_players_records(winner, loser))

    def update_score(self, winner, loser, abort=0):
        # Update the records of the winner
        self.statistics.update_players(winner, loser, abort)

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
        self.abort = 0
        self.game_ongoing = 0

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
        if spin == g.loaded_cylindar:
            g.result = 1
        else:
            g.result = 0
        phenny.say("%s spins the cylinder..." % (g.players[0]))
        time.sleep(3)
        #phenny.say("%s pulls the trigger!" % (g.players[0]))


        # announce result
        if g.result == 0:
            phenny.say("%s pulls the trigger!" % (g.players[0]))
            time.sleep(random.choice([1, 2, 3])) 
            phenny.say('CLICK')
            time.sleep(1)
            phenny.say(random.choice(relief) % (g.players[0]))
            g.players = [g.players[1], g.players[0]]

        elif g.result == 1:
            phenny.say("%s pulls the trigger!" % (g.players[0]))

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

        elif g.result == 2:
            phenny.say("LOL! %s cannot bring himself to pull the trigger!" % (g.players[0]))
            # update the winner, loser and score
            g.winner = g.players[1]
            g.loser = g.players[0]
            g.update_score(g.winner,g.loser,abort=1)
            
            # make announcement
            phenny.say("Congratulations, %s, you are the winner." % (g.players[1]))
            phenny.say("Since %s aborted, you are awarded 2 points." % (g.players[0]))
            g.report_score(phenny, g.winner, g.loser) 
            g.game_ongoing = 0
            g.reset()

            break
        elif g.result == 3:
            phenny.say("LOL! %s cannot bring himself to pull the trigger!" % (g.players[0]))
            phenny.say("But we'll give him a break this time.")

            # make announcement
            g.report_score(phenny, g.winner, g.loser) 
            g.game_ongoing = 0
            g.reset()

            break
        else:
            # problem
            print "You shouldn't have gotten here. There is an error in the game loop."

            break

def abort(phenny,input):
    # forfeit the game at any time
    if input.nick != g.players[0]:
        pass
    elif random.choice([0,1]) == 1:
        g.result = 2
    else:
        g.result = 3
abort.commands = ['abort']

def challenge(phenny, input):
    if g.game_ongoing == 1:
        pass
    else:
        g.game_ongoing = 1
        g.time_of_challenge = time.time()
        g.challenger = input.nick.strip()
        g.challenge_made = 1
        g.challenged = input.group(2).strip()
        g.statistics.check(g.challenger, g.challenged) # ADDED
        phenny.say("%s challenged %s to Russian Roulette!" % (g.challenger, g.challenged))
        phenny.say("%s, do you accept?" % (g.challenged))
challenge.commands = ['roulette', 'r']

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
accept.commands = ['accept', 'yes', 'acc', 'hell-yeah', 'pff']

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
        g.reset()
decline.commands = ['decline', 'no', 'get-lost']

def undo(phenny, input):        
    if input.nick == g.challenger:
        g.reset()
        phenny.say("%s has retracted the challenge." % (input.nick))
    else:
        if (time.time() - g.time_of_challenge) > 300: 
            g.reset()
            phenny.say("The challenge has been expired.")
        else:
            phenny.say("The challenge has not expired, yet. Hold your horses.")
undo.commands = ['undo']

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
