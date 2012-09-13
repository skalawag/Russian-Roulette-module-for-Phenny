#! /usr/bin/env python
# coding=utf-8
"""
roulette.py - Phenny Russian Roulette Module
Copyright 2012, Mark Scala
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

# TODO:
#
# 1. if a player is a heathen on the first (self) test of the day,
# give him a small advantage against a sheep.
#
# 2. up the number of wins for a superwin to 4 (or 5?) --- remove the
# incentive to game the game.


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

class db():
    def __init__(self):
        self.storage = shelve.open('roulette.db')
        try:
            self.db = self.storage['roulette']
        except:
            # scores = [[p1, p2, score], [p1, p3, score], ...]
            self.storage['roulette'] = {'all_players':[], 'scores':[]}
            self.db = {'all_players':[], 'scores':[]}
        self.storage.close()

    def save_db(self):
        self.db = shelve.open('roulette.db')
        self.db['roulette'] = self.db

    def add_player(self, player):
        """Adds a new player to the database
        """
        # To add a player to the db, first add him to the front of
        # all_players in self.db
        self.db['all_players'] = [player] + self.db['all_players']

        # next, add his score versus each player already in the db.
        for opp in self.db['all_players'][1:]:
            self.db['scores'].append([player, opp, [0,0]])
        self.save_db()

    def get_score(self, p1, p2):
        "Return score for row=p1, col=p2"
        for item in self.db['scores']:
            if item[0] == p1 and item[1] == p2:
                return p1, p2, item[2]
            elif item[0] == p2 and item[1] == p1:
                return p2, p1, item[2]
        return "No score for these players"

    def update_score(self, p1, p2):
        """
        Update the table for p1 v p2, where p1 is the winner.
        """
        for item in self.db['scores']:
            if item[0] == p1 and item[1] == p2:
                item[2][0] += 1
            elif item[0] == p2 and item[1] == p1:
                item[2][1] += 1

    def remove_player(self, p):
        self.db[0].remove(p)
        self.db[1] = [item for item in self.db[1] if item[0] != p and item[1] != p]
        self.save_db()

    def get_wins(self, player):
        wins = 0
        for item in self.db['scores']:
            if item[0] == player:
                wins += item[2][0]
            elif item[1] == player:
                wins += item[2][1]
        return wins

    def get_losses(self, player):
        losses = 0
        for item in self.db['scores']:
            if item[0] == player:
                losses += item[2][1]
            elif item[1] == player:
                losses += item[2][0]

class stats():
    def __init__(self):
        self.CHAMPION = self.get_ranking[0]

    def get_player_record(self, player):
        wins = db.get_wins(player)
        losses = db.get_losses(player)
        return player, wins, losses, (float(wins(player)) / float((losses(player) + wins(player)))) * 100

    def get_ranking(self):
        def key(x):
            return x[3]
        def comp(x,y):
            if x < y: return 1
            elif x == y: return 0
            else: return -1
        return sorted([self.get_player_record(player) for player in db.db['all_players']], comp, key)

    def super_dead(self):
        """
        the player who loses 3 or 4 in a row gets superdead -- goes to 0
        """
        pass




game = game()
db = db()
stats = stats()

# Diagnostic
# def print_db(phenny,input):
#     if input.nick == 'skalawag':
#         phenny.say('%s' % (str( db.record)))
#     else: pass
# print_db.commands = ['rdb']

# def print_champ(phenny, input):
#     if input.nick == 'skalawag':
#         phenny.say('%s' % (db.CHAMPION))
#     else: pass
# print_champ.commands = ['rprc']

# Game Play
def play_game(phenny):
    #setup
    random.shuffle(game.PLAYERS)
    game.GAME_IN_PROGRESS = 1

    # make sure both players are in db
    if game.CHALLENGER not in db.db[0]:
        db.add_player(game.CHALLENGER)
    if game.CHALLENGED not in db.db[0]:
        db.add_player(game.CHALLENGED)

    # Announce first player
    phenny.say("A coin toss will decide the first player....")
    time.sleep(2)
    phenny.say("%s, you win!" % (game.PLAYERS[0]))

    # possible accidental death
    if random.choice([x for x in range(30)]) == 1:
        phenny.say(random.choice(['BANG!', 'KA-POW!', 'BOOM!', 'BAM!', 'BLAMMO!', 'BOOM! BOOM!']))
        phenny.say("OH MAN! Did you see that!?")
        phenny.say("%s accidentally blew his brains out!" % (game.players[0]))
        winner = game.PLAYERS[1] # survivor
        loser = game.PLAYERS[0]
        db.update_score(winner, loser)
        res = db.get_score(winner, loser)
        phenny.say('%d:%d  %s vs. %s' % (res[2][0], res[2][1], res[0], res[1]))
        game.GAME_IN_PROGRESS = 0
    else:
        rounds = random.randint(1,6)
        for x in range(rounds):
            phenny.say("%s spins the cylinder..." % (game.PLAYERS[0]))
            time.sleep(2)
            if x < rounds:
                phenny.say("%s pulls the trigger!" % (game.PLAYERS[0]))
                time.sleep(1)
                phenny.say('CLICK')
                time.sleep(1)
                phenny.say(random.choice(RELIEF) % (game.PLAYERS[0]))
                game.PLAYERS = [game.PLAYERS[1], game.PLAYERS[0]]

            else:
                phenny.say("%s pulls the trigger!" % (game.PLAYERS[0]))
                # update winner, loser and score
                winner = game.PLAYERS[1] # survivor
                loser = game.PLAYERS[0]
                db.update_score(winner, loser)
                # make announcements and cleanup
                phenny.say(random.choice(['BANG!', 'KA-POW!', 'BOOM!', 'BAM!', 'BLAMMO!', 'BOOM! BOOM!']))
                time.sleep(1)
                phenny.say(random.choice(EXCLAMATIONS) % (game.PLAYERS[0]))
                res = db.get_score(winner, loser)
                phenny.say('%d:%d  %s vs. %s' % (res[2][0], res[2][1], res[0], res[1]))
                game.GAME_IN_PROGRESS = 0

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
        phenny.say("NO_IAM_BOT accepts!")
        game.PLAYERS = [game.CHALLENGED, game.CHALLENGER]
        play_game(phenny)
        game.reset()
        db.save_db()
    else:
        game.CHALLENGE_MADE = 1
        game.R_TIME = time.time()
        game.CHALLENGER = input.nick.strip()
        game.CHALLENGED = str(input.group(2).strip())
        db.check(game.CHALLENGER, game.CHALLENGED)
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
        db.save_db()
    else:
        game.CATCH_ACCEPT = 1
        game.GAME_IN_PROGRESS = 1
        phenny.say("%s accepts the challenge!" % input.nick)
        phenny.say("Let the game begin!")
        game.PLAYERS = [game.CHALLENGED, game.CHALLENGER]

        # GAME ==========
        play_game(phenny)

        game.reset()
        db.save_db()
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

# COMMANDS
def display_ranking(phenny):
    ranking = stats.get_ranking()
    for item in ranking:
        phenny.say("%s: %f" % (ranking[0], ranking[3]))
display_ranking.commands = ['rstats']

def remove_player(phenny, input):
    if input.nick != 'skalawag':
        pass
    else db.remove_player(input.group(2))
remove_player.commands = ['rremove']

# def reset_champion():
#     try:
#         best = [None, 0]
#         for name in db.record.keys():
#             if win_percentage(name) > best[1]:
#                 best = [name, win_percentage(name)]
#             else: pass
#         db.CHAMPION = best
#         if db.CHAMPION[1] > db.ALL_TIME_CHAMPION and total_wins(db.CHAMPION) > 6:
#             db.ALL_TIME_CHAMPION = db.CHAMPION
#         db.save_db()
#     except: pass

# def champion(phenny, input):
#     reset_champion()
#     try:
#         phenny.say('%s is the current champion, winning %.3f%% of his matches.' \
#                        % (db.CHAMPION[0],db.CHAMPION[1]))
#     except:
#         phenny.say("There doesn't seem to be a champion at the moment.")
# champion.commands = ['rchamp']

# def rstat_him(phenny, input):
#     try:
#         wins = total_wins(input.group(2))
#         losses = total_losses(input.group(2))
#         perc = win_percentage(input.group(2))
#         phenny.say('%s has won %s out of %s (%.3f%%)' \
#                        % (input.group(2), wins, wins + losses, perc))
#     except: pass
# rstat_him.commands = ['rstat']

# def rstat_me(phenny, input):
#     try:
#         wins = total_wins(input.nick)
#         losses = total_losses(input.nick)
#         perc = win_percentage(input.nick)
#         phenny.say('%s, you have won %s out of %s (%.3f%%)' \
#                        % (input.nick, wins, wins + losses, perc))
#     except:
#         phenny.say("Problem in rstat_me")
# rstat_me.commands = ['rstat-me','rstats-me', 'rstatme', 'rstatsme']

# def get_ranking(phenny, input):
#     try:
#         def compare(x,y):
#             if x < y: return 1
#             elif x > y: return -1
#             else: return 0
#         def key(x):
#             if x[1] == None:
#                 return 0
#             else:
#                 return x[1]
#         names = db.record.keys()
#         res = sorted([(name, win_percentage(name)) for name in names], compare, key)
#         res = [item for item in res if item[1] > 0.0]
#         for item in res:
#             if item[1] == None:
#                 phenny.say('%.3f%%  %s' % (0.00, item[0]))
#             else:
#                 phenny.say('%.3f%%  %s' % (item[1], item[0]))
#     except: print "Problem in get_ranking."
# get_ranking.commands = ['rranking', 'rall', 'rstats']

# def get_my_percentage(phenny, input):
#     try:
#         res = win_percentage(input.nick)
#         phenny.say('%s, you have won %.3f%% of your matches' % (input.nick,res))
#     except: print "Problem in global get_my_percentage."
# get_my_percentage.commands = ['rme']

# def get_diff(phenny, input):
#     try:
#         players = input.group(2).split()
#         if len(players) != 2:
#             pass
#         p1 = win_percentage(players[0])
#         p2 = win_percentage(players[1])
#         if p1 > p2:
#             phenny.say('%s leads by %.3f%%' % (players[0],p1-p2))
#         else:
#             phenny.say('%s leads by %.3f%%' % (players[1],p2-p1))
#     except: pass
# get_diff.commands = ['rdiff']

if __name__ == '__main__':
    print __doc__
