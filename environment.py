import random   # Shuffle (Deck - cards)

# --------------------
# Helper functions

def card_matrix_build():
    """
    Return list of unique card types
    
    Structure: [[Card Type, Card Value],]
    
    Index is used in defining game state
    """
    return [['Distance', 25], ['Distance', 50], ['Distance', 75], ['Distance', 100], ['Distance', 200], 
            ['Remedy', 'Gasoline'], ['Remedy', 'Spare Tire'], ['Remedy', 'Repairs'], ['Remedy', 'End of Limit'], ['Remedy', 'Roll'], 
            ['Safety', 'Extra Tank'], ['Safety', 'Puncture-Proof'], ['Safety', 'Driving Ace'], ['Safety', 'Right-of-Way'], 
            ['Hazard', 'Out of Gas'], ['Hazard', 'Flat Tire'], ['Hazard', 'Accident'], ['Hazard', 'Speed Limit'], ['Hazard', 'Stop']
           ]

def action_matrix_build(card_matrix):
    """
    card_matrix (list) - list of unique card options
    
    Return list of all possible actions
    
    List Structure: 
        Indicies: 0 - 75 (76 actions) - normal play of cards (discard or on a team's pile)
            [[Team index | -1 (Discard), Card Type, Card Value],]
            e.g. [[-1, 'Distance', 25], [-1, 'Distance', 50], ...]
        Indicies: 76 - 90 (15 actions) - coup fourre options
            [[Team index, 'Coup Fourre', Card Value | 'Do not play'],]
            e.g. [[0, 'Coup Fourre', 'Extra Tank'], [0, 'Coup Fourre', 'Puncture-Proof'], ...]
        Indicies: 91 - 96 (6 actions) - extension options
            [[Team index, 'Extension', Yes | No],]
            e.g. [[0, 'Extension', 'Yes'], [0, 'Extension', 'No'], [1, 'Extension', 'Yes'], ...]
        
    """
    
    action_list = []
    
    # Indicies: 0 - 75 - normal play of cards in either discard (team_option[0] = -1) or on a team's piles
    team_options = [-1, 0, 1, 2]
    
    for t in team_options:
        for c in card_matrix:
            action_list.append([t, c[0], c[1]])
    
    # Add coup fourre options
    team_options = [0, 1, 2]
    card_options = ['Extra Tank', 'Puncture-Proof', 'Driving Ace', 'Right-of-Way', 'Do not play']
    
    for t in team_options:
        for c in card_options:
            action_list.append([t, 'Coup Fourre', c])
    
    # Add extension options
    team_options = [0, 1, 2]
    card_options = ['Yes', 'No']
    
    for t in team_options:
        for c in card_options:
            action_list.append([t, 'Extension', c])
    
    return action_list

def safety_counter(hazard_value):
    """
    Return the Safety Card Value that counters the given hazard
    """
    
    safety_choices = ['Extra Tank', 'Puncture-Proof', 'Driving Ace', 'Right-of-Way', 'Right-of-Way']
    hazard_index = ['Out of Gas', 'Flat Tire', 'Accident', 'Speed Limit', 'Stop'].index(hazard_value)
    return safety_choices[hazard_index]

def actions_space(state, card_matrix, action_matrix):
    """
    Return all available actions given the current game state
    
    state ([int]) - current game state
    card_matrix (list) - lookup card info by index
    action_matrix (list) - lookup action info by index
    
    Return ([int]) - action indicies
    """
    
    # Break state list into variables for easier legibility of code
    number_of_players = state[0]
    play_status = state[1]
    extension_team = state[2]
    team_current_index = state[3]
    last_action_index = state[5]
    team_status = []  #2D shape ( 2 or 3 rows (teams), 8 (see below) (speed status, battle status, distance points, 200's played) )
                        # team status index: 0 = Speed Status; 1 = Battle Status; 2 = Distance points; 3 = 200's played
                        #     4 = Extra Tank; 5 = Puncture Proof; 6 = Driving Ace; 7 = Right-of-Way
    team_status.append(state[16:24])  # Team 1 (0 index)
    team_status.append(state[24:32])  # Team 2
    if state[32] > -1:
        team_status.append(state[32:40])  # Team 3
    player_hand = [Card(card_matrix[c][0], card_matrix[c][1]) for c in state[40:46] if c > -1]
    
    # Variable to hold valid actions - use set to prevent duplicate action potentials (e.g. player has 2 cards of the same value)
    player_actions = set()
    
    if play_status == 0 or play_status == 3:
        # Normal game play

        for card in player_hand:

            # Play options - cards that can be played on the "table" (not discarded)
            if card.type == "Safety":
                # Safeties can be played on own team at any point
                player_actions.add(action_matrix.index([team_current_index, card.type, card.value]))
            elif card.type == "Distance":
                # Distance can be played on own team:
                #   Team cannot exceed 1,000 distance points (or 700 if Extension has not yet been called for 2, 3, or 6 player games)
                #   Top card in Battle Pile is Roll OR Right-of-Way Safety has been played and no other Hazard card is top of battle pile
                #   Distance = 200 - Team cannot play more than 2 200 distance cards
                #   Distance > 50 = Top card in Speed Pile is End of Limit or null OR Right-of-Way Safety has been played

                # Team will not exceed 700/1,000 if played
                if (number_of_players == 4):
                    max_points = 1000
                else:
                    max_points = 700 if extension_team == -1 else 1000

                if (team_status[team_current_index][2] + card.value) <= max_points:

                    if team_status[team_current_index][1] == 4:
                        # Battle Status: Team can go

                        if card.value <= 50:
                            # Status of Speed Pile is irrelevant
                            player_actions.add(action_matrix.index([team_current_index, card.type, card.value]))
                        else:
                            if team_status[team_current_index][0] == 0:
                                # No speed limit, ensure distance of 200 can be played
                                if card.value < 200 or team_status[team_current_index][3] < 2:
                                    player_actions.add(action_matrix.index([team_current_index, card.type, card.value]))

            elif card.type == "Remedy":
                # Remedies can be played on own team to counter a hazard unless own team has appropriate safety already played

                if card.value == "Roll" and team_status[team_current_index][1] == 3:
                    player_actions.add(action_matrix.index([team_current_index, card.type, card.value]))                    
                elif card.value == "End of Limit":
                    # Speed Pile
                    if team_status[team_current_index][0] == 1:
                        player_actions.add(action_matrix.index([team_current_index, card.type, card.value]))
                
                # Battle Pile
                elif card.value == 'Gasoline' and team_status[team_current_index][1] == 0:
                    player_actions.add(action_matrix.index([team_current_index, card.type, card.value]))
                elif card.value == 'Spare Tire' and team_status[team_current_index][1] == 1:
                    player_actions.add(action_matrix.index([team_current_index, card.type, card.value]))
                elif card.value == 'Repairs' and team_status[team_current_index][1] == 2:
                    player_actions.add(action_matrix.index([team_current_index, card.type, card.value]))

            else:
                # Card Type: Hazard - can only be played on oponents

                # Can always play on oponents unless they have a safety in place (can be played on top of other hazards)
                safety_value = safety_counter(card.value)
                safety_index = ["Extra Tank", "Puncture-Proof", "Driving Ace", "Right-of-Way"].index(safety_value) + 4

                for i in range(len(team_status)):
                    if i == team_current_index:
                        continue

                    if team_status[i][safety_index] == 0:
                        player_actions.add(action_matrix.index([i, card.type, card.value]))

            # Discard - all cards can be discarded
            player_actions.add(action_matrix.index([-1, card.type, card.value]))

    elif play_status == 1:
        # Coup Fourre Check (hazard played) - Evaluate possible actions
        hazard_value = action_matrix[last_action_index][2]
        safety_value = safety_counter(hazard_value)
        has_safety = False
        
        for card in player_hand:
            if card.type == "Safety" and card.value == safety_value:
                has_safety = True
        
        if has_safety == True:
            # Player has the safety, give them the option to play it or not
            player_actions.add(action_matrix.index([team_current_index, "Coup Fourre", safety_value]))
            player_actions.add(action_matrix.index([team_current_index, "Coup Fourre", "Do not play"]))

        # (else:) Player does not have safety, start the next player's turn (return an empty list)

    elif play_status == 2:
        # Extension Check - Current player reached 700 points, provide options to go into Extended play
        player_actions.add(action_matrix.index([team_current_index, "Extension", "Yes"]))
        player_actions.add(action_matrix.index([team_current_index, "Extension", "No"]))

    # Convert player actions to a list (Set cannot be used with certain functions like random.choice)
    return list(player_actions)

# --------------------
# Card
class Card():
    """
    Representation of a single card in the deck
    """
    
    def __init__ (self, card_type, card_value):
        # Type: Hazard, Remedy, Safety, Distance
        self.type = card_type
        # Value: Either the name of the card or point value
        self.value = card_value
    
# --------------------
# Deck
class Deck():
    """
    Represents the full deck of cards
    
    Attributes
        cards ([Card]) - all cards not yet in play (i.e. face-down deck on the table)
        cards_discard ([Card]) - cards that have been discarded
    
    Expected Card Counts:
        106 - full deck for 4 or 6 players
            46 - distance
            38 - remedy
            4 - safety
            18 - hazard
        101 - full deck for 2 or 3 players
            13 - hazard (1 of each type removed)
        Start of game, after dealing 6 cards:
            2 players - 89
            3 players - 83
            4 players - 82
            6 players - 70
    """
    
    def __init__ (self, card_matrix, players_count):
        """
        card_matrix (int) - reference of unique cards in the deck
        players_count (int) - number of game players
        """
        
        # All cards not yet in play (i.e. the deck, face-down on the table)
        self.cards = []
        
        # Cards which have been discarded and may no longer be played
        self.cards_discard = []
        
        # Setup the playable deck
        self.build(card_matrix, players_count)
        
        # Shuffle the deck
        random.shuffle(self.cards)
    
    def build(self, card_matrix, players_count):
        # Initialize the cards in the deck (assumes the deck has been cleared)
        num_of_cards = [10, 10, 10, 12, 4, 6, 6, 6, 6, 14, 1, 1, 1, 1]
    
        if players_count < 4:
            num_of_cards.extend([2, 2, 2, 3, 4])
        else:
            num_of_cards.extend([3, 3, 3, 4, 5])
        
        for i in range(len(card_matrix)):
            self.cards += num_of_cards[i] * [Card(card_matrix[i][0], card_matrix[i][1])]
    
    def draw(self):
        return self.cards.pop()
    
# --------------------
# Team
class Team():
    """
    A team can have:
        1 player - games with 2 or 3 total players
        2 players - games with 4 or 6 total players
    
    Attributes:
    
    General
        name (str) - team name (e.g. "Team 1")
    
    Card lists: full history of cards played
        safety_area ([Card]) - safety cards played (including coup fourre)
        speed_pile ([Card]) - speed limit and end-of-limit hazard cards played
        battle_pile ([Card]) - hazards, remedies, and go cards
        distance_pile ([Card]) - distance cards played
    
    State: current state of the team (these are applied after all logic - e.g. Flat Tire may be last battle_pile card but with a safety the status may indicate otherwise)
        safety_played ([str]) - card value of any safeties played (convenience function to easily identify safety cards)
        speed_status (int) - 0 = No speed limit; 1 = Speed limit
        battle_status (int) - 0 = Out of Gas; 1 = Flat Tire; 2 = Accident; 3 = Stop; 4 = Go
        distance_points (int) - total distance traveled by the team
        distance_200 (int) - number of 200 Distance cards played (max 2 per team)
    """
    
    def __init__ (self, team_number):
        self.name = "Team {0}".format(team_number)
        self.safety_pile = []
        self.speed_pile = []
        self.battle_pile = []
        self.distance_pile = []
        self.safety_played = []
        self.speed_status = 0
        self.battle_status = 3
        self.distance_points = 0
        self.distance_200 = 0
        
# --------------------
# Player
class Player():
    """
    A player (AI or human)
    
    Attributes:
    name (str) - name of the player
    team (Team) - team the player is on (to share played cards)
    hand ([Card]) - cards the player is holding
    """
    
    def __init__ (self, name, team):
        self.name = name
        self.team = team
        self.hand = []
        
    
    def draw(self, deck):
        """
        Draw a card if there are cards remaining
        """
        
        if len(deck.cards) > 0:
            self.hand.append(deck.draw())
    
    def find_card(self, card_type, card_value):
        """
        Return (Card) the first card matching the card type and value (returns None if no matching card - should be impossible and represents programmatic error)
        """
        
        for i in range(len(self.hand)):
            if self.hand[i].type == card_type and self.hand[i].value == card_value:
                return self.hand.pop(i)
        
        return None
    
    def reward_last_action(self, action_history):
        """
        Return the reward for the last action taken by the player
            If player has not yet taken an action, 0 is returned
        """
        # Start from the end of the Action History and add/subtract rewards until first occurrance of current player
        total_reward = 0
        last_action_found = False
        for act in reversed(action_history):
            if act[0] == self:
                total_reward += act[3]
                last_action_found = True
                break
            else:
                if act[0].team == self.team:
                    total_reward += act[3]
                else:
                    total_reward -= act[3]
        
        return total_reward if last_action_found else 0
    
# --------------------
# Game
class Game():
    """
    A single game
        Technically a "hand", represents cards shuffled and play until a team reaches 1,000 distance points or no further action can be taken by any player
        Players:
            2 or 3 - each player is independent (team = player)
            4 or 6 - players in pairs on teams
        The order the players are passed determines:
            Order of play
            Team members:
                4 - a & c; b & d
                6 - a & d; b & e; c & f
    
    Class Variables:
        card_matrix (list) - list of unique cards in the deck
        
        action_matrix (list) - list of all potential actions for the game (97 possible actions: index 0 - 96)
    
    Attributes:
        teams ([Team]) - list of teams
        
        players ([Player]) - list of players in game play order
        
        player_current (Player) - the current player (set by start_turn)
        
        play_status (int) - indicates current status of play - used to control game flow, values:
            0 = Normal (play advances to next player)
            1 = Coup Fourre Check (hazard has been played, provide team players opportunity to call Coup Fourre)
            2 = Extension Check (Current player reached 700, next action to determine if they wish to call for an Extension)
            3 = Safety Bonus Turn (Current player played a Safety, next action to provide an additional bonus turn)
            4 = Game Over
        
        Coup Fourre Check Handling - used when a hazard is played against a team, to check if the team wishes to call coup fourre (if possible)
            coup_fourre_player (Player|None) - player who played the hazard card (started the coup fourre check)
            coup_fourre_team (Team|None) - team who had the hazard played against (these players are checked for coup fourre status)
            coup_fourre_hazard (str) - card value of the hazard played against the team (e.g. "Out of Gas", "Stop", "Speed Limit", etc.)
        
        deck (Deck) - deck of cards
            deck.cards ([Card]) - cards not yet drawn ("face-down on table")
            deck.cards_discard ([Card]) - cards discarded by players ("face-up, out-of-play")
        
        player_actions ([int]) - index list of actions the current player can take
        
        player_state ([int]) - list of current state of game for the current player
        
        action_history ([[Player, [int], int, int]]) - history/log of all actions taken in the game in order they were played, each list element contains:
            Player - the Player who took the action
            State - the state of the game when the player selected the action
            Action Index - the index of the actions class variable that was taken
            Reward - point value reward from the action (Distance card, Safety, Coup Fourre, playing all 4 safeties, etc.)
        
        extension_team (Team|None) - (2, 3, or 6 players) None = extended play has not been called; Team = the team who reached 700 and called for Extension
    
    Methods:
        __init__ - creates a new Game object, initalizes all variables, deals 6 cards to each player, starts first player (calls start_turn)
            player_names ([str]) - list of strings, names of the players (in game play and team selection order)
        
        start_turn - sets current player based on play status, draws a card (if applicable), determines allowed actions for the current player
                        Note: this method is called internally, there should not be a need during normal game play to call this method explicitly
        
        play_action - ("Step") executes the desired action for the current player, sets game variables, starts next player's turn (calls start_turn) if applicable
            action_index (int) - the index of the action to be played
            
        final_team_points - Return a list of final points by team in team order
            Return ([int])
            
        state - Return the state for the current player
            Return ([int])
    """
    
    # Class variables
    card_matrix = card_matrix_build()
    action_matrix = action_matrix_build(card_matrix)
    
    def __init__ (self, player_names):
        players_count = len(player_names)
        
        # Setup the players
        if players_count < 4:
            self.teams = []
            self.players = []
            for i in range(players_count):
                self.teams.append(Team(i + 1))
                self.players.append(Player(player_names[i], self.teams[i]))
                self.teams[i].name = f"Team {i + 1} ({player_names[i]})"
        else:
            teams_count = players_count // 2
            self.teams = [Team(i + 1) for i in range(teams_count)]
            self.players = [Player(player_names[i], self.teams[i % teams_count]) for i in range(players_count)]
            for i in range(teams_count):
                self.teams[i].name = "Team {0} ({1})".format(i + 1, ', '.join(player_names[i::teams_count]))
        
        # Setup the playing deck
        self.deck = Deck(self.card_matrix, players_count)
        
        # Deal 6 cards to each player (1 card at a time to each player)
        for i in range(6):
            for p in self.players:
                p.draw(self.deck)
        
        # Initalize current player
        self.player_current = self.players[-1]
        self.play_status = 0
        
        # Initalize Coup Fourre Check Handling
        self.coup_fourre_player = None
        self.coup_fourre_team = None
        self.coup_fourre_hazard = None
        
        # Initalize player actions (int list corresponding to the index for the actions class variable)
        self.player_actions = []
        self.player_state = []
        self.action_history = []
        
        # Extension variables
        self.extension_check = False
        self.extension_team = None
        
        # Start first player's turn
        self.start_turn()
        
    def start_turn(self):
        """
        Begin the next player's turn
        
        Play Status:
            0 Normal - normal game play, play advances to the next player, that player draws a card and available actions are evaluated
            1 Coup Fourre Check - a hazard has been played, players are evaluated and given opportunity to play counter safety
            2 Extension Check - 2, 3, or 6 players; player reached 700 points, available actions consistent of Yes/No of an Extension
            3 Safety Bonus Turn - current player played a safety and gets a bonus turn
        """
        
        # Setup current player
        if self.play_status == 0:
            # Normal game play - advance to next player
            
            if len(self.deck.cards) > 0:
                player_current_index = self.players.index(self.player_current)
                player_next_index = player_current_index + 1 if player_current_index < len(self.players) - 1 else 0
                self.player_current = self.players[player_next_index]
                self.player_current.draw(self.deck)
            
            else:
                # No cards left in the deck, advance to the next player with cards remaining in their hand
                player_index = self.players.index(self.player_current)
                player_next_index = -1
                
                while player_next_index == -1:
                    player_index = player_index + 1 if player_index < len(self.players) - 1 else 0
                    if len(self.players[player_index].hand) > 0:
                        player_next_index = player_index
                
                self.player_current = self.players[player_next_index]
            
        elif self.play_status == 1:
            # Coup Fourre Check - Hazard has been played
            player_index = self.players.index(self.player_current)
            player_next_index = -1

            while player_next_index == -1:
                player_index = player_index + 1 if player_index < len(self.players) - 1 else 0

                if self.players[player_index].team == self.coup_fourre_team:
                    # Found next player on the team
                    player_next_index = player_index
                    self.player_current = self.players[player_next_index]
                    
                    # Evaluating action will determine if this player has the safety (this will take care of instance where person has no cards as well)
                    
                elif self.players[player_index] == self.coup_fourre_player:
                    # This is the player that played the hazard to begin with
                    
                    # Turn off the coup fourre check variables to exit the coup fourre check (return to normal play)
                    self.play_status = 0
                    self.coup_fourre_player = None
                    self.coup_fourre_team = None
                    self.coup_fourre_hazard = None
                    
                    # Play returns to next player with cards in their hand
                    while player_next_index == -1:
                        player_index = player_index + 1 if player_index < len(self.players) - 1 else 0
                        if len(self.players[player_index].hand) > 0:
                            player_next_index = player_index
                    
                    self.player_current = self.players[player_next_index]
                    
                    # Draw to start new turn (normal play)
                    self.player_current.draw(self.deck)
            
        elif self.play_status == 3:
            # Extra turn - set to current player unless they do not have any cards (then next player with cards)
            player_index = self.players.index(self.player_current)
            player_next_index = -1
                
            while player_next_index == -1:
                if len(self.players[player_index].hand) > 0:
                    player_next_index = player_index
                else:
                    player_index = player_index + 1 if player_index < len(self.players) - 1 else 0
                
            self.player_current = self.players[player_next_index]
            self.player_current.draw(self.deck)
            
        # Note: Extension Check and Safety Bonus Turn - current player does not change
        
        # State-Action space: populate current game state and possible actions
        self.player_state = self.state()
        self.player_actions = actions_space(self.player_state, self.card_matrix, self.action_matrix)
        
        # If the game state was a 2 (Extension check) or 3 (extra turn), set game play status to 0 (normal) as the next action will resolve these
        if self.play_status == 2 or self.play_status == 3:
            self.play_status = 0
            
        if len(self.player_actions) == 0:
            # No actions possible for current player, start next player's turn
            self.start_turn()
    
    def play_action(self, action_index):
        """
        Plays selected action and ends the player's turn
        """
        
        # Retrieve information about the action to take
        action = self.action_matrix[action_index]
        if action[1] == "Coup Fourre":
            played_card = None if action[2] == "Do not play" else self.player_current.find_card("Safety", action[2])
        elif action[1] == "Extension":
            played_card = None
        else:
            played_card = self.player_current.find_card(action[1], action[2])
            
        # Action history
        #  Initalize reward to 0
        #  This implementation allows for:
        #    Adding additional history entries where Extension is achieved by non-calling team
        #    Reference to current play is not altered and represents the true current player
        action_history_add = [[self.player_current, self.player_state, action_index, 0]]
        
        if action[0] == -1:
            # Discard the selected card
            self.deck.cards_discard.append(played_card)
            
        elif action[1] == "Distance":
            # Add card to team's Distance Pile
            self.player_current.team.distance_pile.append(played_card)
            
            # Increment team's distance points
            self.player_current.team.distance_points += action[2]
            
            # If 200, increment team's 200 card counter
            if action[2] == 200:
                self.player_current.team.distance_200 += 1
            
            # Increment action reward for point value
            action_history_add[0][3] += action[2]
            
            # Check End of Game and Extension
            team_points = self.player_current.team.distance_points
            
            if len(self.players) != 4:
                # Extension play possible
                
                if self.extension_team is None and team_points == 700:
                    # Player can call Extension if desired (change play status for next setup)
                    self.play_status = 2
                elif self.extension_team is not None and team_points == 1000:
                    # End Game: Player has reached Extension
                    
                    # Add reward points for: trip completed (400)
                    action_history_add[0][3] += 400
                    
                    # Add reward points for extension
                    action_history_add[0][3] += 200
                    
                    # If player's team is not the team that called the extension, give 200 points to other team (if applicable) as well
                    if self.extension_team != self.player_current.team:
                        for t in self.teams:
                            if t != self.player_current.team and t != self.extension_team:
                                player_representative = [p for p in self.players if p.team == t][0]
                                action_history_add.append([player_representative, [], -1, 200])
                    
                    # Add reward points if Shut-out (500)
                    shut_out_achieved = True
                    for t in self.teams:
                        if t != self.player_current.team and t.distance_points > 0:
                            shut_out_achieved = False
                            break
                    
                    if shut_out_achieved == True:
                        action_history_add[0][3] += 500
                    
                    # Add reward points if delayed action (300)
                    if len(self.deck.cards) == 0:
                        action_history_add[0][3] += 300
                    
                    # Add reward points if safe trip (no 200's) (300)
                    if self.player_current.team.distance_200 == 0:
                        action_history_add[0][3] += 300
                    
                    # Set the Game Over variable
                    self.play_status = 4
            
            elif team_points == 1000:
                # End Game: Team has reached 1,000 points
                
                # Add reward points for: trip completed (400)
                action_history_add[0][3] += 400

                # Add reward points if Shut-out (500)
                shut_out_achieved = True
                for t in self.teams:
                    if t != self.player_current.team and t.distance_points > 0:
                        shut_out_achieved = False
                        break

                if shut_out_achieved == True:
                    action_history_add[0][3] += 500

                # Add reward points if delayed action (300)
                if len(self.deck.cards) == 0:
                    action_history_add[0][3] += 300

                # Add reward points if safe trip (no 200's) (300)
                if self.player_current.team.distance_200 == 0:
                    action_history_add[0][3] += 300

                # Set the Game Over variable
                self.play_status = 4
        
        elif action[1] == "Remedy":
            # Remedy type: Speed or Battle
            if action[2] == "End of Limit":
                # Add card to team's Speed Pile
                self.player_current.team.speed_pile.append(played_card)
                
                # Update team's Speed status
                self.player_current.team.speed_status = 0
            
            else:
                # Add card to team's Battle Pile
                self.player_current.team.battle_pile.append(played_card)
                
                # Update team's Battle status
                if action[2] == "Roll" or 'Right-of-Way' in self.player_current.team.safety_played:
                    self.player_current.team.battle_status = 4
                else:
                    self.player_current.team.battle_status = 3
        
        elif action[1] == "Hazard":
            # Team receiving hazard
            team_hazard = self.teams[action[0]]
            
            if action[2] == "Speed Limit":
                # Add card to team's Speed Pile
                team_hazard.speed_pile.append(played_card)
                
                # Update team's Speed status
                team_hazard.speed_status = 1
            
            else:
                # Add card to team's Battle Pile
                team_hazard.battle_pile.append(played_card)
                
                # Update team's Battle status
                team_hazard.battle_status = ["Out of Gas", "Flat Tire", "Accident", "Stop"].index(action[2])
            
            # Coup Fourre check - setup variable to begin the process of checking for coup fourre
            self.play_status = 1
            self.coup_fourre_player = self.player_current
            self.coup_fourre_team = team_hazard
            self.coup_fourre_hazard = action[2]
        
        elif action[1] == "Safety" or action[1] == "Coup Fourre":
            # Safety played (Coup Fourre logic is similar, using same code block to reduce redundant code)
            
            if action[2] != "Do not play":
                # A Safety or Coup Fourre has been played
            
                # Add card to team's safety pile
                self.player_current.team.safety_pile.append(played_card)
                
                # Add the card's value to the team's safety played
                self.player_current.team.safety_played.append(action[2])
                
                # Add reward points for safety played (100)
                action_history_add[0][3] += 100
                
                # Add reward points if all 4 safeties played by this team (300)
                if len(self.player_current.team.safety_played) == 4:
                    action_history_add[0][3] += 300
                
                # Process the Speed Pile/Status (only for "Right-of-Way")
                if action[2] == "Right-of-Way" and self.player_current.team.speed_status == 1:
                    # Top card of speed pile is a Speed Limit, it is possible, however, there are multiple Speed Limit card's stacked
                    while len(self.player_current.team.speed_pile) > 0 and self.player_current.team.speed_pile[-1].value == "Speed Limit":
                        self.deck.cards_discard.append(self.player_current.team.speed_pile.pop())

                    # Team should no longer have a Speed Limit applied
                    self.player_current.team.speed_status = 0

                # Process the Battle Pile/Status
                battle_pile_process = True

                while battle_pile_process:
                    # Are there cards left?
                    if len(self.player_current.team.battle_pile) > 0:
                        top_card = self.player_current.team.battle_pile[-1]
                        
                        # Is the top card a Remedy?
                        if top_card.type == "Remedy":
                            # Team can "Go" (whatever last issue was, it was fixed)
                            self.player_current.team.battle_status = 4
                            battle_pile_process = False
                        else:
                            # Top Card is a Hazard, Does the team have the corresponding Safety
                            safety_value = safety_counter(top_card.value)
                            if safety_value in self.player_current.team.safety_played:
                                # Remove the card and keep processing
                                self.deck.cards_discard.append(self.player_current.team.battle_pile.pop())
                            else:
                                # Team does not have a Safety, the hazard applies
                                self.player_current.team.battle_status = ["Out of Gas", "Flat Tire", "Accident", "Stop"].index(top_card.value)
                                battle_pile_process = False
                    else:
                        # No more cards left to process, team can "Go"
                        self.player_current.team.battle_status = 4
                        battle_pile_process = False
                
                # Was the Safety played as a Coup Fourre?
                if action[1] == "Coup Fourre":
                    # Add reward points for Coup Fourre
                    action_history_add[0][3] += 300
                    
                    # Player now has one less card, immediately draw a card
                    self.player_current.draw(self.deck)
                    
                    # Set all coup fourre variables to None (clear the coup fourre check)
                    self.coup_fourre_player = None
                    self.coup_fourre_team = None
                    self.coup_fourre_hazard = None
                    
                # Player get's a bonus turn
                self.play_status = 3
        
        elif action[1] == "Extension":
            # Player has responded to Extension option
            
            if action[2] == "Yes":
                # Extension mode should be enabled
                self.extension_team = self.player_current.team
            
            else:
                # End Game: Player does not want to enter extension, end of game has been reached
                
                # Add reward points for: trip completed (400)
                action_history_add[0][3] += 400

                # Add reward points if Shut-out (500)
                shut_out_achieved = True
                for t in self.teams:
                    if t != self.player_current.team and t.distance_points > 0:
                        shut_out_achieved = False
                        break

                if shut_out_achieved == True:
                    action_history_add[0][3] += 500

                # Add reward points if delayed action (300)
                if len(self.deck.cards) == 0:
                    action_history_add[0][3] += 300

                # Add reward points if safe trip (no 200's) (300)
                if self.player_current.team.distance_200 == 0:
                    action_history_add[0][3] += 300

                # Set the Game Over variable
                self.play_status = 4
        
        # Store action history
        self.action_history.extend(action_history_add)
        
        # Move to next player (or End Game)
        if self.play_status < 4:
            # Ensure there are either cards left in the deck or at least one player has a card left in their hand
            if len(self.deck.cards) > 0 or sum([len(p.hand) for p in self.players]) > 0:
                self.start_turn()
            else:
                # Game Over (no more plays possible)
                self.play_status = 4
    
    def final_team_points(self):
        """
        Return a list of final points by team
        """
        
        team_points = [0 for i in range(len(self.teams))]
        
        for act in self.action_history:
            team_idx = self.teams.index(act[0].team)
            team_points[team_idx] += act[3]
        
        return team_points
    
    def state(self):
        """
        Return the state for the current player
        
        List structure (by index) - shape(32,)
            0     Number of players (2, 3, 4, 6)
            1     Game play status (0 = Normal; 1 = Coup Fourre check; 2 = Extension check; 3 = Bonus turn)
            2     Extension team (-1 = Not in extension play; 0-2 = Team index who called for an extension)
            3     Current player team number index (0, 1, 2)
            4     Number of cards left in deck (unplayed; recognition this is not an infinite horizon)
            5-15  Action (index) history taken by other players prior to the current player's turn (-1 for n/a) most recent action first (reverse order)
            16    Team 1 Speed Status (0 = No speed limit; 1 = Speed Limit)
            17    Team 1 Battle Status (0 = Out of Gas; 1 = Flat Tire; 2 = Accident; 3 = Stop; 4 = Go)
            18    Team 1 Distance points
            19    Team 1 Number of 200 distance point cards played (0, 1, 2)
            20    Team 1 Extra Tank (0 = No; 1 = Yes)
            21    Team 1 Puncture Proof (0 = No; 1 = Yes)
            22    Team 1 Driving Ace (0 = No; 1 = Yes)
            23    Team 1 Right-of-Way (0 = No; 1 = Yes)
            24-31 Team 2 (same as Team 1)
            32-39 Team 3 (same as Team 1) (-1 for n/a)
            40-46 Cards (index) in current player hand (-1 for n/a)
        
        Notes:
            The following game elements are not included in the state. I am beginning with "minimal" information at first.
            
            A key strategy is counting cards, for example, counting number of "Accident" cards already played. This can influence discarding extra Repairs remedy cards.
                Currently, this is not explicitly in the State
                The prior actions taken since last turn is in the State, the model could potentially learn from this component of state
            
            Another important component of the game is to know the relationship among cards (e.g. Out of Gas > Gasoline > Extra Tank).
                I am not certain if/how to model this to assist with training an optimal policy

        """
        
        state_list = [-1] * 47
        
        # Number of players
        state_list[0] = len(self.players)
        
        # Game play status
        state_list[1] = self.play_status
        
        # Extension team
        state_list[2] = -1 if self.extension_team is None else self.teams.index(self.extension_team)
        
        # Current Player's Team Index
        state_list[3] = self.teams.index(self.player_current.team)
        
        # Number of cards left in deck
        state_list[4] = len(self.deck.cards)
        
        # Action History since player's last turn
        i = 5
        for act in reversed(self.action_history):
            if act[0] == self.player_current:
                break
            else:
                state_list[i] = act[2]
                i += 1
        
        # Teams info
        i = 16
        for t in self.teams:
            state_list[i] = t.speed_status
            i += 1
            state_list[i] = t.battle_status
            i += 1
            state_list[i] = t.distance_points
            i += 1
            state_list[i] = t.distance_200
            i += 1
            state_list[i] = 1 if "Extra Tank" in t.safety_played else 0
            i += 1
            state_list[i] = 1 if "Puncture-Proof" in t.safety_played else 0
            i += 1
            state_list[i] = 1 if "Driving Ace" in t.safety_played else 0
            i += 1
            state_list[i] = 1 if "Right-of-Way" in t.safety_played else 0
            i += 1
        
        # Cards in current player's hand
        i = 40
        for c in self.player_current.hand:
            state_list[i] = self.card_matrix.index([c.type, c.value])
            i += 1
        
        return state_list
        