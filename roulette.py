#! /usr/bin/env python
# coding=utf-8
"""
roulette.py - Phenny Russian Roulette Module
Copyright 2012, Mark Scala
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

"""
* TODO: choice of weapons: double barrel shotgun?
"""

import random, time, shelve

RELIEF = ["%s wipes the sweat from his brow.",
          "I think %s peed his pants.",
          "%s weeps a tear of relief.",
          ]
EXCLAMATIONS = ["Holy, cow! %s blew his head off!",
                "OH SNAP! %s brain matter is everywhere!",
                "%s falls to the floor like a sack of flour!",
                "%s does the obituary mambo!",
                ]
CHANGE = ["%s, it's your turn.", "%s, wipe that smirk off your face. It's your turn!"]

class game():
    def __init__(self):
        self.GAME_IN_PROGRESS = 0
        self.PLAYERS = []
        self.BANG = 0
        self.R_TIME = None
        self.CHALLENGE_MADE = 0
        self.CHALLENGER = None
        self.CHALLENGED = None

    def reset(self):
        self.GAME_IN_PROGRESS = 0
        self.PLAYERS = []
        self.BANG = 0
        self.R_TIME = None
        self.CHALLENGE_MADE = 0
        self.CHALLENGER = None
        self.CHALLENGED = None

class stats():
    def __init__(self):
        self.db = shelve.open('roulette.db')
        try:
            self.record = self.db['roulette']
        except:
            self.db.setdefault('roulette',{})
            self.record = {}
        self.db.close()

    def cull_zero_stats(self):
        names = self.record.keys()
        for name in names:
            opps = self.record[name].keys()
            for opp in opps:
                if self.record[name][opp] == 0 and self.record[opp][name] == 0:
                    self.record[name].pop(opp)
                    self.record[opp].pop(name)

    def refresh_db(self):
        self.db = shelve.open('roulette.db')
        self.db['roulette'] = self.record
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
        self.cull_zero_stats()
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
        self.cull_zero_stats()
        all = self.record.keys()
        res = []

        # this is ugly because of my choice above.
        for player in all:
            for opponent in self.record[player].keys():
                if self.get_players_records(opponent, player) not in res:
                    res.append(self.get_players_records(player, opponent))
        return res

game = game()    
stats = stats()

def play_game(phenny):
    #setup
    random.shuffle(game.PLAYERS)
    bullet = random.choice([1, 2, 3])
    game.BANG = 0
    game.GAME_IN_PROGRESS = 1

    # Announce first player
    phenny.say("A coin toss will decide the first player....")
    time.sleep(2)
    phenny.say("%s, you win!" % (game.PLAYERS[0]))

    while 1:
        # `spin' cylindar
        spin = random.choice([1, 2, 3])
        if spin == bullet:
            game.BANG = 1
        phenny.say("%s spins the cylinder..." % (game.PLAYERS[0]))
        time.sleep(3)

        # announce result
        if game.BANG == 0:
            phenny.say("%s pulls the trigger!" % (game.PLAYERS[0]))
            time.sleep(random.choice([1, 2, 3])) 
            phenny.say('CLICK')
            time.sleep(1)
            phenny.say(random.choice(RELIEF) % (game.PLAYERS[0]))
            game.PLAYERS = [game.PLAYERS[1], game.PLAYERS[0]]

        elif game.BANG == 1:
            phenny.say("%s pulls the trigger!" % (game.PLAYERS[0]))
            # update winner, loser and score
            winner = game.PLAYERS[1] # survivor
            loser = game.PLAYERS[0]
            stats.update_players(winner, loser) 

            # make announcements and cleanup
            phenny.say(random.choice(['BANG!', 'KA-POW', 'BOOM!', 'BAM!']))
            time.sleep(1)
            phenny.say(random.choice(EXCLAMATIONS) % (game.PLAYERS[0]))
            phenny.say("Congratulations, %s, you are the winner." % (game.PLAYERS[1]))
            phenny.say(stats.get_players_records(winner, loser))

            game.GAME_IN_PROGRESS = 0
            break

        elif BANG == 2:
            phenny.say("LOL! %s cannot bring himself to pull the trigger!" % (game.PLAYERS[0]))
            # update the winner, loser and score
            winner = game.PLAYERS[1]
            loser = game.PLAYERS[0]
            stats.update_players(winner, loser, abort=1)
            
            # make announcement
            phenny.say("Congratulations, %s, you are the winner." % (game.PLAYERS[1]))
            phenny.say("Since %s aborted, you are awarded 2 points." % (game.PLAYERS[0]))
            phenny.say(stats.get_players_records(winner, loser))

            game.GAME_IN_PROGRESS = 0
            break

        elif game.BANG == 3:
            # make announcement
            phenny.say("LOL! %s cannot bring himself to pull the trigger!" % (game.PLAYERS[0]))
            phenny.say("But we'll give him a break this time.")

            game.GAME_IN_PROGRESS = 0
            break

        else:
            # problem
            print "You shouldn't have gotten here. There is an error in the game loop."
            break
        
        stats.refresh_db()


def abort(phenny,input):
    # forfeit the game at any time
    if game.GAME_IN_PROGRESS == 0:
        pass
    elif input.nick != game.PLAYERS[0]:
        pass
    elif random.choice([0,1]) == 1:
        game.BANG = 2
    else:
        game.BANG = 3
abort.commands = ['abort']

def challenge(phenny, input):
    if game.GAME_IN_PROGRESS == 1:
        pass
    elif game.R_TIME and (time.time() - game.R_TIME < 60):
        phenny.say("%s, there is a standing challenge." % (input.nick))
    else:
        game.CHALLENGE_MADE = 1
        game.R_TIME = time.time()
        game.CHALLENGER = input.nick.strip()
        game.CHALLENGED = str(input.group(2).strip())
        stats.check(game.CHALLENGER, game.CHALLENGED) 
        phenny.say("%s challenged %s to Russian Roulette!" % (game.CHALLENGER, game.CHALLENGED))
        phenny.say("%s, do you accept?" % (game.CHALLENGED))
challenge.commands = ['roulette', 'r']

def accept(phenny, input):
    if game.CHALLENGE_MADE == 0:
        phenny.say("%s, no one has challenged you to Russian Roulette. Get a life!" % (input.nick))
    elif game.CHALLENGE_MADE == 1 and input.nick != game.CHALLENGED:
        phenny.say("%s, let %s speak for himself!" % (input.nick, game.CHALLENGED))
    else:
        game.GAME_IN_PROGRESS = 1
        phenny.say("%s accepts the challenge!" % input.nick)
        phenny.say("Let the game begin!")
        game.PLAYERS = [game.CHALLENGED, game.CHALLENGER]
        
        # GAME STARTS HERE
        play_game(phenny)
        game.reset()
accept.commands = ['accept', 'yes', 'acc', 'hell-yeah', 'pff']



def decline(phenny, input):
    insults = ['%s, %s is yellow and will not play.',
           '%s, %s is a fraidy-cat, and will not play.',
           '%s, %s is going to run home and cry.',
           ]
    if game.CHALLENGE_MADE == 0:
        phenny.say("%s, there has been no challenge to Russian Roulette. Get a life!" %s (input.nick))
    elif game.CHALLENGE_MADE == 1 and input.nick != game.CHALLENGED:
        phenny.say("%s, let %s speak for himself!" % (input.nick, game.CHALLENGED))
    else:
        insult = random.choice(insults)
        phenny.say(insult % (game.CHALLENGER, input.nick))
        game.reset()
decline.commands = ['decline', 'no', 'get-lost']

def undo(phenny, input):        
    if input.nick == game.CHALLENGER:
        reset() 
        phenny.say("%s has retracted the challenge." % (input.nick))
    else:
        if (time.time() - game.R_TIME) > 300: 
            reset() 
            phenny.say("The challenge has been expired.")
        else:
            phenny.say("The challenge has not expired, yet. Hold your horses.")
undo.commands = ['undo']

def rstat_me(phenny, input):
    res = stats.get_my_stats(input.nick)
    for item in res:
        phenny.say(item)
rstat_me.commands = ['rstat-me','rstats-me']                           

def get_stats_for_all(phenny, input):
    res = stats.get_all_stats()
    for item in res:
        phenny.say(item)
get_stats_for_all.commands = ['roulette-stats', 'r-stats', 'rstats']

if __name__ == '__main__':
    print __doc__
