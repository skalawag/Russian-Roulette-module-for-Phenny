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
        self.CHAMPION = None
        # The structure of the db is as follows.  {'roulette':
        # {'player1': {'opp1-name': [wins,losses], 'opp2-name: [wins,
        # losses], }, 'player2: {'opp1-name': [wins,losses],}...}}}
        self.db = shelve.open('roulette.db')
        try:
            self.record = self.db['roulette']
        except:
            self.db.setdefault('roulette',{})
            self.record = {}
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
            return [(item[0], \
                         round(float(item[1])/float(item[1] + item[2]),4) * 100) \
                        for item in res]
        except: 
            print "Problem in get_records"

    def get_total_number_of_matches_played_for_each_player(self):
        try:
            res = []
            for name in self.record.keys():
                record = [name, 0]
                for opp in self.record[name].keys():
                    record[1] += self.record[name][opp][0] # adding wins against opp
                    record[1] += self.record[name][opp][1] # adding losses against opp
                res.append(record)
            return res
        else: print "Problem in stats.get_total_number_of_matches_played_for_each_player"

    def get_champion(self):
        """ Find the best record."""
        def comp(x,y):
            if x > y: return -1
            elif x < y: return 1
            else: return 0
        try:
            winner = sorted(self.get_records(), comp, lambda x: x[1])[0]
            res = "The current champion of Russian Roulette is %s, whose record is %d%%!" % \
                (winner[0], winner[1])
            self.CHAMPION = winner[0]
            return res
        except: 
            print "Problem in get_champion"

    def update_players(self, winner, loser, abort=0):
        # Each player records only his own wins against each
        # opponent.  This assumes that an entry exists for each
        # player and each opponent under that player.
        try:
            self.record[winner][loser][0] += 1
            self.record[loser][winner][1] += 1
            self.refresh_db()
        except:
            print "Problem updating players."

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

def champion(phenny, input):
    phenny.say(stats.get_champion())
champion.commands = ['rchamp']

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
    elif input.group(2) == stats.CHAMPION:
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
    elif input.group(2) == 'BOT':
        game.CATCH_ACCEPT = 1
        game.GAME_IN_PROGRESS = 1
        phenny.say("BOT accepts the challenge!")
        phenny.say("Let the game begin!")
        game.PLAYERS = ['BOT', input.nick]
        
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

def total_matches(player):
    total_matches = stats.get_total_number_of_matches_played_for_each_player()
    return [item for item in total_matches if item[0] == player][1]

def rstat_him(phenny, input):
    try:
        total = total_matches(input.group(2))
        res = [item for item in stats.get_records() if item[0] == input.group(2)][0]
        phenny.say("%s has won %d%% of %d  matches." % (res[0], res[1], total))
    except: pass
rstat_him.commands = ['rstat']

def rstat_me(phenny, input):
    try:
        total = total_matches(input.nick)
        res = [item for item in stats.get_records() if item[0] == input.nick][0]
        phenny.say("%s, you have won %d%% of your %d matches." % (res[0],res[1],total))
    except: pass
rstat_me.commands = ['rstat-me','rstats-me', 'rstatme', 'rstatsme']                           

def get_stats_for_all(phenny, input):
    res = stats.get_all_stats()
    for item in res:
        phenny.say(item)
get_stats_for_all.commands = ['roulette-stats', 'r-stats', 'rstats']

def get_ranking(phenny):
    try:
        record = stats.get_records()
        for item in record:
            phenny.say("%d$%% %s" % (item[1], item[0]))
    except: print "Problem in get_ranking."
get_ranking.commands = ['rranking', 'rall']

def get_my_percentage(phenny, input):
    try:
        total = total_matches(input.nick)
        record = stats.get_records()
        for item in record:
            if input.nick == item[0]:
                phenny.say("%s, you have won %d%% of %d matches" % (input.nick, item[1], total))
get_my_percentage.commands = ['.rme']

def get_diff(phenny, input):
    try: 
        records = stats.get_records()
        p1 = [item for item in records if input.nick == item[0]][0]
        p2 = [item for item in records if input.group(2) == item[0]][0]
        if not p1 or not p2:
            pass
        elif p1[1] > p2[1]:
            phenny.say("%s leads by %d%%" % (p1[0], p1[1] - p2[1]))
        else:
            phenny.say("%s leads by %d%%" % (p2[0], p2[1] - p1[1]))
    except: pass
get_diff.commands = ['rdiff']

if __name__ == '__main__':
    print __doc__
