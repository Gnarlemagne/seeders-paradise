# Base Modules
import os

import configparser

from seeders_paradise.reseed_lib import Set, Player, Bracket
from seeders_paradise.smash_gg import SmashGG
from seeders_paradise.smash_gg import verify_auth_token

CONFIG_FILE_PATH = "config.ini"


def run():
    """Main function which runs the tourney seed redistributor
    """
    if not os.path.isfile(CONFIG_FILE_PATH):
        # Create the configuration file as it doesn't exist yet
        with open(CONFIG_FILE_PATH, "w") as cfgfile:
            cfg = configparser.ConfigParser()
            cfg.add_section("API")
            cfg.set("API", "smashgg_api_key", "")
            cfg.set("API", "api_version", "alpha")
            cfg.write(cfgfile)

    with open(CONFIG_FILE_PATH) as f:
        config = configparser.RawConfigParser(allow_no_value=True)
        config.read_file(f)


    auth_token = config.get("API", "smashgg_api_key")
    api_ver = config.get("API", "api_version")

    # test API key
    name, token = enter_and_verify_auth_token(auth_token, api_ver)

    # Overwrite old settings if applicable
    if (token != auth_token):
        config.set("API", "smashgg_api_key", token)

        with open(CONFIG_FILE_PATH, "w") as cfgfile:
            config.write(cfgfile)

        auth_token = token

    smashgg = SmashGG(auth_token, api_ver)

    print("Welcome,", name)

    while True:
        turl = input("Please enter the URL of the tourney you would like to reseed\n").split("/")
        slug = None
        for i, section in enumerate(turl):
            if section == "tournament":
                slug = turl[i+1]

        print(slug)

        try:
            tourney_name, tourney_events = smashgg.get_tourney_info(slug)
            break
        except Exception as e:
            print("Error, invalid tourney URL")
            continue

    print()
    print("Tournament: " + str(tourney_name))
    print("Please select an event: ")
    for i, event in enumerate(tourney_events):
        print(" " + str(i+1) + ". " + event["name"])

    selection = -1
    while (selection < 0 or selection >= len(tourney_events)):
        try:
            selection = int(input()) - 1
        except:
            continue

    event = tourney_events[selection]
    print()
    print("Seeding for " + str(event["name"]) + ":")

    seed_map = smashgg.get_seeding(event["id"])
    print(seed_map)
    
    bracket = Bracket()
    for s, p in seed_map.items():
        player = Player(p["id"], p["tag"], p["seed_id"], s)
        bracket.add_player(player)
    
    print(bracket)




def enter_and_verify_auth_token(auth_token=None, api_ver="alpha"):

    if (auth_token):
        new_token = auth_token
    else:
        new_token = input("Please enter your smash.gg API authentication token\r\nThis can be found at https://smash.gg/admin/profile/developer by clicking \"Create new Token\".\n")

    # Test the new auth token
    authenticated = False

    while not authenticated:
        try:
            name = verify_auth_token(new_token, api_ver)
            authenticated = True
        except ValueError as e:
            new_token = input("The Authentication Token you entered did not work. Please try again.\n")

    return name, new_token

if __name__ == '__main__':
    run()

