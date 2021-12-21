import math
from collections import deque
class Player:
    """Simple player class used to keep track of a player's important stats in the seeding process"""

    def __init__(self, id, tag, seed_id, true_seed):
        self.id = id
        self.tag = tag
        self.seed_id = seed_id
        self.true_seed = true_seed
        self.h2h = None # Head to head stats populated by the seedmap once all players are imported
        
    def get_string(self):
        return f"[ {self.true_seed:>3} {self.tag:>20} ]"

class Set:
    """A simple class used by the Bracket class to evaluate and print sets that are projected to happen"""

    def __init__(self, higher_seed, lower_seed, bracket=None):
        """
        Args:
            higher_seed (Player): The higher seeded player of the matchup
            lower_seed (Player): The lower seeded player of the matchup
            bracket (Bracket, optional): The bracket which this set takes place in. Defaults to None.
        """
        self.higher_seed = higher_seed # Player instance
        self.lower_seed = lower_seed # Player or Set instance (in case of bye)
        self.bracket = bracket # The bracket this set exists in
        self.rating = 9999 # A rating for this set (Higher = worse)

    def get_strings(self):
        """Output a text representation of the set
        If the player has a bye and the lower seed is a Set instance, it will print the low-seed set to the left of the top player's undetermined set
        """
        
        align_right = True

        if (isinstance(self.lower_seed, Player)):
            
            if min(self.lower_seed.true_seed, self.higher_seed.true_seed) > self.bracket.last_power_of_2():
                align_right = False

            if (align_right):
                player_string = (" " * 28) + "     " + self.higher_seed.get_string()
                player2_string = (" " * 28) + "     " + self.lower_seed.get_string()
            
            return player_string, player2_string
        
        elif (isinstance(self.lower_seed, Set)):
            r1_p1, r1_p2 = self.lower_seed.get_strings()
            ret1 = r1_p1 + "__   " + self.higher_seed.get_string()
            ret2 = r1_p2 + "  `->" + "[" + " "*26 + "]"

            return ret1, ret2
        
        raise "You shouldn't be here lol"
    
    def __str__(self):
        s1, s2 = self.get_strings()
        return s1 + "\r\n" + s2



class Bracket:
    """A class used to view and manipulate a bracket based only on seeding and player data"""

    def __init__(self):
        self.seed_map = {} # A dict which contains Player instances keyed on their seed
        self.new_seed_map = {} # A dict which contains Player instances keyed on their new seed
        self.bracket_size = 0
        self.score = 99999999 # A higher score is bad
        self.sets = []

    def add_player(self, player):
        """Add a player to the seedmap and properly insert it into the data
        """
        self.seed_map[player.true_seed - 1] = player
        self.new_seed_map[player.true_seed - 1] = player
        self.bracket_size += 1

    def print_seeding(self):
        ret = ""
        for s, player in sorted(self.new_seed_map.items()):
            ret += (f'{player.true_seed:>3} {player.tag}\r\n')

        print(ret)
    
    def is_imbalanced(self):
        return self.bracket_size != self.last_power_of_2()
    
    def last_power_of_2(self):
        return 2 ** int(math.log(self.bracket_size, 2))
    
    def generate_sets(self):
        """Use bracketing algorithm to generate correct byes
        """
        
        # How many players are there more than would take to be a symmetrical bracket
        excess = self.bracket_size - self.last_power_of_2()
        
        # Round 1 will have the lowest players face off against each other
        # This array will ultimately be thinned out to half its size by round 2, with winners fighting players with byes
        # So we calculate r1 to contain all the lowest seeds necessary so that when cut in half, they add to the remaining players with byes to a power of 2
        r1 = list(range(self.bracket_size - (2*excess), self.bracket_size))
        r2 = list(range(self.last_power_of_2() - excess))
        
        # Compound r1 into proper pairs
        r1 = deque(r1)
        while r1:
            match = (r1.popleft(), r1.pop())
            r2.append(match)
        
        r2 = deque(r2)
        while r2:
            set_ = self._set_from_seed(r2.popleft(), r2.pop())
            self.sets.append(set_)
        
        return self.sets
        
    def _set_from_seed(self, seed1, seed2):
        if (isinstance(seed2, tuple)):
            seed2 = self._set_from_seed(seed2[0], seed2[1])
        else:
            seed2 = self.new_seed_map[seed2]
        
        return Set(self.new_seed_map[seed1], seed2, self)
    
    def __str__(self):
        out = ""
        for s in self.sets:
            out += str(s) + "\n\n"
        
        return out
        