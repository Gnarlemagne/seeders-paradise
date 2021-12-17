
class Player:
    """Simple player class used to keep track of a player's important stats in the seeding process"""

    def __init__(self, id, tag, seed_id, true_seed):
        self.id = id
        self.tag = tag
        self.seed_id = seed_id
        self.true_seed = true_seed
        self.h2h = None # Head to head stats populated by the seedmap once all players are imported

class Set:
    """A simple class used by the Bracket class to evaluate and print sets that are projected to happen"""

    def __init__(self, higher_seed, lower_seed, bracket=None):
        self.higher_seed = higher_seed # Player instance
        self.lower_seed = lower_seed # Player or Set instance (in case of bye)
        self.bracket = bracket # The bracket this set exists in
        self.rating = 9999 # A rating for this set (Higher = worse)

    def get_strings(self, align_for_bye=False):
        """Output a text representation of the set
        If the player has a bye and the lower seed is a Set instance, it will print the low-seed set to the left of the top player's undetermined set

        Args:
            align_for_bye (Boolean, default=False): If true, will add space before the set to make it align with other r1's with byes 
        """

        player_string = f"[ {self.higher_seed.tag:>20}   ]"

        if (isinstance(self.lower_seed, Player)):
            player2_string = f"[ {self.lower_seed.tag:>20}   ]"

            if (align_for_bye):
                player_string = (" " * 26) + "     " + player_string
                player2_string = (" " * 26) + "     " + player2_string
            
            return player_string, player2_string
        
        elif (isinstance(self.lower_seed, Set)):
            r1_p1, r1_p2 = self.lower_seed.get_strings(align_for_bye=False)
            ret1 = r1_p1 + "_____" + player_string
            ret2 = r1_p2 + "     " + player2_string

            return ret1, ret2
        
        raise "You shouldn't be here lol"
    
    def __str__(self):
        s1, s2 = self.get_strings(align_for_bye=self.asymmetrical_bracket)
        return s1 + "\r\n" + s2



class Bracket:
    """A class used to view and manipulate a bracket based only on seeding and player data"""

    def __init__(self):
        self.seed_map = {} # A dict which contains Player instances keyed on their seed
        self.new_seed_map = {} # A dict which contains Player instances keyed on their new seed
        self.bracket_size = 0
        self.score = 99999999 # A higher score is bad

    def add_player(self, player):
        """Add a player to the seedmap and properly insert it into the data
        """
        self.seed_map[player.true_seed] = player
        self.new_seed_map[player.true_seed] = player
        self.bracket_size += 1

    def __str__(self):
        ret = ""
        for i in range(1, self.bracket_size + 1):
            ret += (f'{i:3} {self.seed_map[i].tag}\r\n')

        return ret