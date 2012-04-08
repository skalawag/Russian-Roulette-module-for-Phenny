#! /usr/bin/env python
# coding=utf-8
"""
roulette.py - Phenny Russian Roulette Module
Copyright 2012, Mark Scala
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
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
        self.CATCH_ACCEPT = 0
        # if someone wins N in a row, give him a prize
        self.LAST_WINNER = [None, 0]

    def reset(self):
        self.GAME_IN_PROGRESS = 0
        self.PLAYERS = []
        self.BANG = 0
        self.R_TIME = None
        self.CHALLENGE_MADE = 0
        self.CHALLENGER = None
        self.CHALLENGED = None
        self.CATCH_ACCEPT = 0

class stats():
    def __init__(self):
        self.CHAMPION = ['dummy',0.0]
        self.ALL_TIME_CHAMPION = ['skalawag', 89.889000]
        self.record = {}

        # The structure of the db is as follows.  {'roulette':
        # {'player1': {'opp1-name': [wins,losses], 'opp2-name: [wins,
        # losses], }, 'player2: {'opp1-name': [wins,losses],}...}}}
        self.db = shelve.open('roulette.db')

        try:
            self.record = self.db['roulette']
        except:
            self.db['roulette'] = {}

        try: 
            self.ALL_TIME_CHAMPION = self.db['alltime']
        except:
            self.db['alltime'] = self.ALL_TIME_CHAMPION

        self.db.close()
    
    ## DB operations
    def refresh_db(self):
        self.db = shelve.open('roulette.db')
        self.db['roulette'] = self.record
        self.db['alltime'] = self.ALL_TIME_CHAMPION
        self.db.close()
        
    def check(self, player1, player2):
        if player1 in self.record.keys():
            if player2 in self.record[player1].keys():
                pass
            else:
                self.record[player1].setdefault(player2, [0,0])
        else:
            self.record.setdefault(player1, {player2: [0,0]})

        if player2 in self.record.keys():
            if player1 in self.record[player2].keys():
                pass
            else:
                self.record[player2].setdefault(player1, [0,0])
        else:
            self.record.setdefault(player2, {player1: [0,0]})

    def get_players_records(self, player1, player2):
        p1vp2 = self.record[player1][player2]
        return p1vp2
        
    def get_records(self):
        """ Return a list of all players and their records. """
        try: 
            res = [] # a list of all players and their records
            for name in self.record.keys():
                record = [name, 0, 0]
                for opp in self.record[name].keys():
                    record[1] += opp[0] # wins
                    record[2] += opp[1] # losses
                    res.append(record)
            return res
        except: 
            print "Problem in get_records"
    
    def update_players(self, winner, loser, abort=0):
        try:
            self.record[winner][loser][0] += 1
            self.record[loser][winner][1] += 1
            self.refresh_db()
        except:
            print "Problem updating players."

    def special_update(self, winner, loser):
        try:
            self.record[winner][loser][0] += 10
        except: pass

game = game()    
stats = stats()

# Diagnostic
def print_db(phenny,input):
    if input.nick == 'skalawag':
        phenny.say('%s' % (str( stats.record)))
    else: pass
print_db.commands = ['rdb']

def print_champ(phenny, input):
    if input.nick == 'skalawag':
        phenny.say('%s' % (stats.CHAMPION))
    else: pass
print_champ.commands = ['rprc']

# Game Play
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
            time.sleep(1) 
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
            if game.LAST_WINNER[0] == game.PLAYERS[1]:
                game.LAST_WINNER[1] += 1
            else:
                game.LAST_WINNER = [game.PLAYERS[1], 1]
            # make announcements and cleanup
            phenny.say(random.choice(['BANG!', 'KA-POW!', 'BOOM!', 'BAM!', 'BLAMMO!', 'BOOM! BOOM!']))
            time.sleep(1)
            phenny.say(random.choice(EXCLAMATIONS) % (game.PLAYERS[0]))
            if game.LAST_WINNER[1] < 3:
                phenny.say("Congratulations, %s, you are the winner." % (game.PLAYERS[1]))
            else:
                phenny.say("Congratulations, %s, you are a Super Winner." % (game.PLAYERS[1]))
                phenny.say("You win 10 extra points!")
                stats.special_update(winner,loser)
            res = stats.get_players_records(game.PLAYERS[1], game.PLAYERS[0])
            phenny.say('%d:%d  %s vs. %s' % (res[0], res[1], game.PLAYERS[1], game.PLAYERS[0]))
            game.GAME_IN_PROGRESS = 0
            break

        else:
            # problem
            print "You shouldn't have gotten here. There is an error in the game loop."
            break
    reset_champion()

def challenge(phenny, input):
    if input.group(2) == '':
        pass
    elif game.GAME_IN_PROGRESS == 1:
        pass
    elif game.R_TIME and (time.time() - game.R_TIME < 60):
        phenny.say("%s, there is a standing challenge." % (input.nick))
    elif input.nick == input.group(2):
        phenny.say("%s, suicide is not a good idea." % input.nick)
        phenny.say("If you dial 1-800-273-8255, a nice person will explain this to you.")
    elif input.group(2) == "NO_IAM_BOT":
        game.CHALLENGE_MADE = 1
        game.R_TIME = time.time()
        game.CHALLENGER = input.nick.strip()
        game.CHALLENGED = input.group(2)
        stats.check(game.CHALLENGER, game.CHALLENGED)
        phenny.say("NO_IAM_BOT accepts!")
        game.PLAYERS = [game.CHALLENGED, game.CHALLENGER]
        play_game(phenny)
        game.reset()
        stats.refresh_db()
    elif input.group(2) == stats.CHAMPION[0]:
        game.CHALLENGE_MADE = 1
        game.R_TIME = time.time()
        game.CHALLENGER = input.nick
        game.CHALLENGED = input.group(2)
        stats.check(game.CHALLENGER, game.CHALLENGED)
        phenny.say("The Champion always accepts!")
        game.PLAYERS = [game.CHALLENGED, game.CHALLENGER]
        play_game(phenny)
        game.reset()
        stats.refresh_db()
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
    elif game.CATCH_ACCEPT == 1:
        pass
    elif input.group(2) == 'NO_IAM_BOT':
        game.CATCH_ACCEPT = 1
        game.GAME_IN_PROGRESS = 1
        phenny.say("NO_IAM_BOT accepts the challenge!")
        phenny.say("Let the game begin!")
        game.PLAYERS = ['NO_IAM_BOT', input.nick]
        
        # GAME ==========
        play_game(phenny)

        game.reset()
        stats.refresh_db()
    else:
        game.CATCH_ACCEPT = 1
        game.GAME_IN_PROGRESS = 1
        phenny.say("%s accepts the challenge!" % input.nick)
        phenny.say("Let the game begin!")
        game.PLAYERS = [game.CHALLENGED, game.CHALLENGER]
        
        # GAME ==========
        play_game(phenny)

        game.reset()
        stats.refresh_db()
accept.commands = ['accept', 'yes', 'acc', 'hell-yeah', 'pff']

def decline(phenny, input):
    insults = ['%s, %s is yella and will not play.',
           '%s, %s is a fraidy-cat, and will not play.',
           '%s, %s is going to run home and cry.',
           ]
    if game.CHALLENGE_MADE == 0:
        phenny.say("%s, there has been no challenge to Russian Roulette. Get a life!" % (input.nick))
    elif game.CHALLENGE_MADE == 1 and input.nick != game.CHALLENGED:
        phenny.say("%s, let %s speak for himself!" % (input.nick, game.CHALLENGED))
    else:
        insult = random.choice(insults)
        phenny.say(insult % (game.CHALLENGER, input.nick))
        game.reset()
decline.commands = ['decline', 'no', 'get-lost']

def undo(phenny, input):        
    if input.group(2) == '':
        pass
    elif game.GAME_IN_PROGRESS == 1:
        pass
    elif game.CHALLENGE_MADE == 0:
        pass
    elif input.nick == game.CHALLENGER:
        game.reset() 
        phenny.say("%s has retracted the challenge." % (input.nick))
    else:
        if (time.time() - game.R_TIME) > 300: 
            game.reset() 
            phenny.say("The challenge has been expired.")
        else:
            phenny.say("The challenge has not expired, yet. Hold your horses.")
undo.commands = ['undo']

## STATISTICS HELPERS
def total_wins(player):
    try:
        res = 0
        p = stats.record[player] 
        for key in p.keys():
            res += p[key][0]
        return res
    except: print "Problem in total_wins"

def total_losses(player):
    try:
        res = 0
        p = stats.record[player] 
        for key in p.keys():
            res += p[key][1] 
        return res
    except: print "Problem in total_losses"

def win_percentage(player):
    try:
        return (float(total_wins(player)) / (total_losses(player) + \
                                                      total_wins(player))) * 100
    except: pass

# COMMANDS
def reset_champion():
    try:
        best = [None, 0]
        for name in stats.record.keys():
            if win_percentage(name) > best[1]:
                best = [name, win_percentage(name)]
            else: pass
        stats.CHAMPION = best
        if stats.CHAMPION[1] > stats.ALL_TIME_CHAMPION and total_wins(stats.CHAMPION) > 6:
            stats.ALL_TIME_CHAMPION = stats.CHAMPION
        stats.refresh_db()
    except: pass

def all_time_high(phenny, input):
    reset_champion()
    try:
        phenny.say('%s has the all-time high percentage of %.3f%%' \
                       % (stats.ALL_TIME_CHAMPION[0], stats.ALL_TIME_CHAMPION[1]))
    except: pass
all_time_high.commands = ['alltime', 'ralltime', 'rall-time', 'uberchamp']

def champion(phenny, input):
    reset_champion()
    try:
        phenny.say('%s is the current champion, winning %.3f%% of his matches.' \
                       % (stats.CHAMPION[0],stats.CHAMPION[1]))
    except: print "Error in champion"
champion.commands = ['rchamp']

def rstat_him(phenny, input):
    try: 
        wins = total_wins(input.group(2))
        losses = total_losses(input.group(2))
        perc = win_percentage(input.group(2))
        phenny.say('%s has won %s out of %s (%.3f%%)' \
                       % (input.group(2), wins, wins + losses, perc))
    except: pass
rstat_him.commands = ['rstat']

def rstat_me(phenny, input):
    try:
        wins = total_wins(input.nick)
        losses = total_losses(input.nick)
        perc = win_percentage(input.nick)
        phenny.say('%s, you have won %s out of %s (%.3f%%)' \
                       % (input.nick, wins, wins + losses, perc))
    except: 
        phenny.say("Problem in rstat_me")
rstat_me.commands = ['rstat-me','rstats-me', 'rstatme', 'rstatsme']                           

def get_ranking(phenny, input):
    try: 
        def compare(x,y):
            if x < y: return 1
            elif x > y: return -1
            else: return 0
        def key(x):
            return x[1]
        names = stats.record.keys()
        res = sorted([(name, win_percentage(name)) for name in names], compare, key)
        for item in res:
            phenny.say('%.3f%%  %s' % (item[1], item[0]))
    except: print "Problem in get_ranking."
get_ranking.commands = ['rranking', 'rall', 'rstats']

def get_my_percentage(phenny, input):
    try: 
        res = win_percentage(input.nick)
        phenny.say('%s, you have won %.3f%% of your matches' % (input.nick,res))
    except: print "Problem in global get_my_percentage."
get_my_percentage.commands = ['rme']

def get_diff(phenny, input):
    try: 
        players = input.group(2).split()
        if len(players) != 2:
            pass
        p1 = win_percentage(players[0])
        p2 = win_percentage(players[1])
        if p1 > p2:
            phenny.say('%s leads by %.3f%%' % (players[0],p1-p2))
        else:
            phenny.say('%s leads by %.3f%%' % (players[1],p2-p1))
    except: pass
get_diff.commands = ['rdiff']

if __name__ == '__main__':
    print __doc__
