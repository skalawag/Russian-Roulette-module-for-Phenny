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
        self.accepting_all = []

    def reset(self):
        self.GAME_IN_PROGRESS = 0
        self.PLAYERS = []
        self.BANG = 0
        self.R_TIME = None
        self.CHALLENGE_MADE = 0
        self.CHALLENGER = None
        self.CHALLENGED = None
        self.CATCH_ACCEPT = 0

    def setup(self):
        random.shuffle(self.PLAYERS)
        self.GAME_IN_PROGRESS = 1

        # make sure both players are in db
        if game.CHALLENGER not in db.db.keys():
            db.add_player(self.CHALLENGER)
        if game.CHALLENGED not in db.db.keys():
            db.add_player(self.CHALLENGED)

        # update timer
        db.update_timer(self.CHALLENGER)
        db.update_timer(self.CHALLENGED)

    def announce_and_cleanup(self, phenny, accident=None):
        winner = self.PLAYERS[1] # survivor
        loser = self.PLAYERS[0]
        db.update_score(winner, loser)
        if not accident:
            phenny.say("%s pulls the trigger!" % (self.PLAYERS[0]))
            phenny.say(random.choice(['BANG!', 'KA-POW!', 'BOOM!', 'BAM!', 'BLAMMO!', 'BOOM! BOOM!']))
            time.sleep(1)
            phenny.say(random.choice(EXCLAMATIONS) % (game.PLAYERS[0]))
            phenny.say("%s's new percentage is: %.2f%%" % (winner, db.get_percentage(winner)))
        else:
            phenny.say(random.choice(['BANG!', 'KA-POW!', 'BOOM!', 'BAM!', 'BLAMMO!', 'BOOM! BOOM!']))
            phenny.say("OH MAN! Did you see that!?")
            phenny.say("%s accidentally blew his brains out!" % (self.PLAYERS[0]))
            phenny.say("%s's new percentage is: %.2f%%" % (winner, db.get_percentage(winner)))
        self.GAME_IN_PROGRESS = 0

    def click(self, phenny):
        phenny.say("%s pulls the trigger!" % (self.PLAYERS[0]))
        time.sleep(1)
        phenny.say('CLICK')
        phenny.say(random.choice(RELIEF) % (self.PLAYERS[0]))
        self.PLAYERS = [self.PLAYERS[1], self.PLAYERS[0]]

    def announce_start(self, phenny):
        # Announce first player
        phenny.say("A coin toss will decide the first player....")
        time.sleep(2)
        phenny.say("%s, you win!" % (game.PLAYERS[0]))

class db():
    def __init__(self):
        self.storage = shelve.open('roulette.db')
        try:
            self.db = self.storage['roulette']
        except:
            # {'player':{'wins':i, 'losses':j, last_defended:date, ....}, ...}
            self.storage['roulette'] = {}
            self.db = {}
        self.storage.close()

    def display_self(self):
        print self.db

    def save_db(self):
        f = shelve.open('roulette.db')
        f['roulette'] = self.db
        f.close()

    def add_player(self, player):
        """Adds a new player to the database
        """
        self.db.setdefault(player,{'wins':0, 'losses':0, 'last_defended':time.time()})
        self.save_db()

    def get_percentage(self, player):
        """
        Get player's win percentage
        """
        return round(float(self.get_wins(player)) / float(self.get_wins(player) + self.get_losses(player)) * 100, 4)

    def update_score(self, p1, p2):
        """
        Update the table for p1 v p2, where p1 is the winner.
        """
        self.db[p1]['wins'] += 1
        self.db[p2]['losses'] += 1
        self.save_db()

    def remove_player(self, player):
        try:
            self.db.pop(player)
            self.save_db()
        except:
            pass

    def get_wins(self, player):
        return self.db[player]['wins']

    def get_losses(self, player):
        return self.db[player]['losses']

    def get_player_record(self, player):
        wins = self.get_wins(player)
        losses = self.get_losses(player)
        return [player, wins, losses, self.get_percentage(player)]

    def get_ranking(self):
        def key(x):
            return x[3]
        def comp(x,y):
            if x < y: return 1
            elif x == y: return 0
            else: return -1
        return sorted([self.get_player_record(player) for player in self.db.keys()], comp, key)

    def check_timer(self, player):
        if time.time() - self.db[player]['last_defended'] > 60 * 60 * 24:
            self.db[player]['wins'] = int(self.db[player]['wins'] * .80)
            self.db[player]['last_defended'] = time.time()
        self.save_db()

    def update_timer(self, player):
        self.db[player]['last_defended'] = time.time()

game = game()
db = db()

# Game Play
def play_game(phenny):
    #setup
    db.display_self()
    game.setup()
    game.announce_start(phenny)
    if random.choice([x for x in range(30)]) == 1:
        game.announce_and_cleanup(phenny, accident=1)
    else:
        rounds = random.randint(1,6)
        for x in range(rounds):
            phenny.say("%s spins the cylinder..." % (game.PLAYERS[0]))
            time.sleep(2)
            if x < rounds - 1:
                game.click(phenny)
            else:
                game.announce_and_cleanup(phenny)

####################################
# Commands
def challenge(phenny, input):
    if not input.group(2):
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
    elif input.group(2) in game.accepting_all:
        game.CHALLENGE_MADE = 1
        game.R_TIME = time.time()
        game.CHALLENGER = input.nick.strip()
        game.CHALLENGED = str(input.group(2).strip())
        game.PLAYERS = [game.CHALLENGED, game.CHALLENGER]
        phenny.say("%s accepts all challenges!" % (input.group(2)))
        play_game(phenny)
        game.reset()
        db.save_db()
    else:
        game.CHALLENGE_MADE = 1
        game.R_TIME = time.time()
        game.CHALLENGER = input.nick.strip()
        game.CHALLENGED = str(input.group(2).strip())
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
accept.commands = ['accept', 'yes', 'acc', 'hell-yeah', 'pff', 'bring-it', 'die!']

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
decline.commands = ['decline', 'no', 'get-lost', 'buzz-off']

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
    for player in db.db.keys():
       db.check_timer(player)
    db.save_db()
    ranking = db.get_ranking()
    if ranking is not None:
        for item in ranking:
            phenny.say("%s: %.2f%%" % (item[0], item[3]))
    else:
        phenny.say("There is no record.")
display_ranking.commands = ['rstats']

def print_db(phenny, input):
    db.display_self()
print_db.commands = ['rprintdb']

def remove_player(phenny, input):
    if input.nick != 'skalawag':
        phenny.say('Only skalawag can do that.')
    elif input.group(2) == 'all':
        db.db = {}
        db.update_db()
    else:
        db.remove_player(input.group(2))
remove_player.commands = ['rremove']

def accept_all(phenny, input):
    game.accepting_all.append(input.nick)
    phenny.say("%s is accepting ALL CHALLENGES!!!" % input.nick)
accept_all.commands = ['bringiton', 'bringit', 'bringit!', 'kill_me']

def rescind_accept_all(phenny, input):
    if input.nick in game.accepting_all:
        game.accepting_all.remove(input.nick)
        phenny.say("%s is no longer accepting challenges!" % input.nick)
rescind_accept_all.commands = ['rescind']

def open_challenges(phenny, input):
    phenny.say("Accepting all challenges:")
    phenny.say("%s" % "NO_IAM_BOT")
    if game.accepting_all:
        for name in game.accepting_all:
            phenny.say("%s" % name)
open_challenges.commands = ['ropen\?']

def snipe(phenny, input):
    pass

def roulette_help(phenny, input):
    c1 = "'roulette', 'r' [player-name]: Challenge a player."
    c2 = "'undo': Undo a challenge.",
    c3 = "'yes', 'acc', 'hell-yeah', 'pff', 'die!': Accept a challenge."
    c4 = "'decline', 'no', 'get-lost', 'buzz-off': Decline a challenge."
    c5 = "'rstats': List current roulette stats for all players."
    c6 = "'bringiton', 'bringit', 'bringit!', 'kill_me': Accept all incoming challenges."
    c7 = "'rescind': Rescind your open call for challenges."
    c8 = "'ropen?': Who is accepting all incoming challenges?"
    phenny.say("Roulette commands (prefix a command with a '.', e.g., '.r'):")
    phenny.say("%s" % c1)
    phenny.say("%s" % c2)
    phenny.say("%s" % c3)
    phenny.say("%s" % c4)
    phenny.say("%s" % c5)
    phenny.say("%s" % c6)
    phenny.say("%s" % c7)
    phenny.say("%s" % c8)
roulette_help.commands = ['rhelp']

if __name__ == '__main__':
    print __doc__
