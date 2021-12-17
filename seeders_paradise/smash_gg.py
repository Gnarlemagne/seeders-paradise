import json

from graphqlclient import GraphQLClient

class SmashGG:
    """
    A library which accesses the smash.gg API to do stuff with tourney seeds
    """

    def __init__(self, api_key, api_version):
        self.api_key = api_key
        self.tourney_slug = None
        
        self.api = GraphQLClient('https://api.smash.gg/gql/' + api_version)
        self.api.inject_token('Bearer ' + api_key)

    def load_tourney(self, tourney_slug):
        self.tourney_slug = tourney_slug

    def get_tourney_info(self, tourney_slug):
        tourney_data = self.api.execute('''
            query TournamentQuery($slug:String){
                tournament(slug: $slug){
                    id
                    name
                    events {
                        id
                        name
                    }
                }
            }
            ''',
            {
            "slug": tourney_slug
            }
        )

        data = json.loads(tourney_data)
        if 'errors' in data:
            raise data['errors']

        name = data['data']['tournament']['name']
        events = data['data']['tournament']['events']

        return (name, events)

    def _get_event_phases(self, event_id):
        event_data = self.api.execute('''
            query EventQuery($event:ID!){
                event(id: $event){
                    id
                    name
                    phases {
                        id
                        name
                        phaseOrder
                    }
                }
            }
            ''',
            {
            "event": event_id
            }
        )

        data = json.loads(event_data)
        if 'errors' in data:
            raise data['errors']

        return data['data']['event']['phases']

    def get_seeding(self, event_id):
        """Gets a dict mapping of player data keyed to their seed number

        Args:
            event_id (String): GraphQL ID of the event in question

        Returns:
            Dictionary:
                   {
                       [seed_number]: {
                        "id": (string),
                        "tag": (string),
                        "seed_id": (string)
                      },
                    [seed number]: {...},
                    ...
                }
                            
        """
        phases = self._get_event_phases(event_id)

        phase_id = -1
        phase_order = 9999999

        for phase in phases:
            if phase["phaseOrder"] < phase_order:
                phase_order = phase["phaseOrder"]
                phase_id = phase["id"]

        phase_data = self.api.execute('''
            query PhaseSeeds($phaseId: ID!, $page: Int!, $perPage: Int!) {
                phase(id:$phaseId) {
                    id
                    seeds(query: {
                        page: $page
                        perPage: $perPage
                    })
                    {
                        pageInfo {
                            total
                            totalPages
                        }
                        nodes {
                            id
                            seedNum
                            players {
                                id
                                prefix
                                gamerTag
                            }
                        }
                    }
                }
            }
            ''',
            {
                "phaseId": phase_id,
                "page": 1,
                "perPage": 500
            }
        )

        data = json.loads(phase_data)

        seeds = data['data']['phase']['seeds']['nodes']
        seed_map = {}

        for s in seeds:
            p_data = s["players"][0]
            seed_map[s["seedNum"]] = {
                "id": p_data["id"],
                "tag": p_data["gamerTag"],
                "seed_id": s["id"]
            }
        
        return seed_map
    

def verify_auth_token(token, api_ver):
        client = GraphQLClient('https://api.smash.gg/gql/' + api_ver)
        client.inject_token('Bearer ' + token)
        admin_data = client.execute('''
            query AuthKeyConfirm{
                currentUser {
                    player {
                        gamerTag
                    }
                }
            }
            '''
        )

        data = json.loads(admin_data)
        if 'errors' in data:
            raise ValueError(data['errors'])
        
        return data['data']['currentUser']['player']['gamerTag']