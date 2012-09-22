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
        self.GOD = []

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
            # {'player':{'wins':i, 'losses':j, last-defended:date, ....}, ...}
            self.storage['roulette'] = {}
            self.db = {}
        self.storage.close()

    def display_self(self):
        print self.db

    def save_db(self):
        f = shelve.open('roulette.db')
        f['roulette'] = self.db

    def add_player(self, player):
        """Adds a new player to the database
        """
        self.db.setdefault(player,{'wins':0, 'losses':0, 'last-defended':time.time()}
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
        self.db['all_players'].remove(p)
        self.db['scores'] = [item for item in self.db['scores'] if item[0] != p and item[1] != p]
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
        return losses

class stats():

    def get_player_record(self, player):
        wins = db.get_wins(player)
        losses = db.get_losses(player)
        res = [player, wins, losses, (float(wins) / float(losses + wins)) * 100]
        return res

    def get_ranking(self):
        def key(x):
            return x[3]
        def comp(x,y):
            if x < y: return 1
            elif x == y: return 0
            else: return -1
        try:
            unfiltered = sorted([self.get_player_record(player) for player in db.db['all_players']], comp, key)
            return [x for x in unfiltered if x != None]
        except:
            return None

    def super_dead(self):
        """
        the player who loses 3 or 4 in a row gets superdead -- goes to 0
        """
        pass

game = game()
db = db()
stats = stats()

# Game Play
def play_game(phenny):
    #setup
    random.shuffle(game.PLAYERS)
    game.GAME_IN_PROGRESS = 1

    # make sure both players are in db
    if game.CHALLENGER not in db.db['all_players']:
        db.add_player(game.CHALLENGER)
    if game.CHALLENGED not in db.db['all_players']:
        db.add_player(game.CHALLENGED)

    # Announce first player
    phenny.say("A coin toss will decide the first player....")
    time.sleep(2)
    phenny.say("%s, you win!" % (game.PLAYERS[0]))

    # check if we make a god
    if random.randint(1,365) == 1:
        game.GOD.append(game.CHALLENGER)
        game.GOD.append(20)

    # possible accidental death
    if game.GOD:
        rounds = random.randint(1,6)
        if game.PLAYERS[0] == game.GOD[0] and rounds % 2 == 0:
            pass
        elif game.PLAYERS[1] == game.GOD[0] and rounds % 2 != 0:
            rounds += 1
        game.GOD[1] -= 1
        if game.GOD[1] < 1:
            game.GOD = []
            # play game
        for x in range(rounds):
            phenny.say("%s spins the cylinder..." % (game.PLAYERS[0]))
            time.sleep(2)
            if x < rounds - 1:
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
                db.display_self()
                # make announcements and cleanup
                phenny.say(random.choice(['BANG!', 'KA-POW!', 'BOOM!', 'BAM!', 'BLAMMO!', 'BOOM! BOOM!']))
                time.sleep(1)
                phenny.say(random.choice(EXCLAMATIONS) % (game.PLAYERS[0]))
                res = db.get_score(winner, loser)
                phenny.say('%d:%d  %s vs. %s' % (res[2][0], res[2][1], res[0], res[1]))
                game.GAME_IN_PROGRESS = 0
    elif random.choice([x for x in range(30)]) == 1:
        phenny.say(random.choice(['BANG!', 'KA-POW!', 'BOOM!', 'BAM!', 'BLAMMO!', 'BOOM! BOOM!']))
        phenny.say("OH MAN! Did you see that!?")
        phenny.say("%s accidentally blew his brains out!" % (game.PLAYERS[0]))
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
            if x < rounds - 1:
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
                db.display_self()
                # make announcements and cleanup
                phenny.say(random.choice(['BANG!', 'KA-POW!', 'BOOM!', 'BAM!', 'BLAMMO!', 'BOOM! BOOM!']))
                time.sleep(1)
                phenny.say(random.choice(EXCLAMATIONS) % (game.PLAYERS[0]))
                res = db.get_score(winner, loser)
                phenny.say('%d:%d  %s vs. %s' % (res[2][0], res[2][1], res[0], res[1]))
                game.GAME_IN_PROGRESS = 0
# Commands
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
        #db.check(game.CHALLENGER, game.CHALLENGED)
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

def display_ranking(phenny,input):
    ranking = stats.get_ranking()
    if ranking is not None:
        for item in ranking:
            phenny.say("%s: %.2f%%" % (item[0], item[3]))
    else:
        phenny.say("There is no record.")
display_ranking.commands = ['rstats']

def remove_player(phenny, input):
    if input.nick != 'skalawag':
        pass
    else:
        db.remove_player(input.group(2))
remove_player.commands = ['rremove']

if __name__ == '__main__':
    print __doc__
