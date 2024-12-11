from textx import metamodel_from_file
import time
import sys
import random
from collections import Counter

#loading our model from the given name
def load_model(file_name):
    fortuna_mm = metamodel_from_file('fortuna.tx')

    global fortuna_model
    fortuna_model = fortuna_mm
    fortuna_model = fortuna_mm.model_from_file("test.fort")
    return fortuna_model


#starting point. This will load the mdoel and interpet the functions inside the file
def start():
    print("Welcome to Citadel! This is where you interpret your Fortuna files.")
    #file_name = input("Please give us the name of your Fortuna File: ")

    model = load_model("yes")
    user_chips = 120
    if model.chips <= user_chips:
        dict = {"chips": model.chips} # dictionary that will track our variables, initialize chips
        for function in model.functions:
            interpreter(function, dict) #main interpreter

def check_chips(current_balance):
    print(current_balance)
    if current_balance <= 0:
        print("ERGGG no money!!!")
        sys.exit()
    else:
        return True 
def interpreter(function, dict):
    function_name = function.__class__.__name__
    if function_name == "ForLoop":
        interpret_for(function, dict)
    elif function_name == "WhileLoop":
        interpret_while(function, dict)
    elif function_name == "IfStatement":
        interpret_if(function, dict)
    elif function_name == "VariableDeclaration":
        interpet_var(function, dict)
    elif function_name == "Call":
        interpret_call(function, dict)
    elif function_name == "Calculation":
        interpret_calc(function, dict)
    elif function_name == "Roulette":
        interpret_roulette(function, dict)
    elif function_name == "RouletteAccess":
        interpret_access(function, dict)
    elif function_name == "NonParamFunction":
        interpret_nonparam(function)
    elif function_name == "ParamFunction":
        interpret_param(function, dict)

#interpetting pillars
def interpret_for(for_loop, dict):
    print("entered for")
    for_cost = 5
    dict["chips"] -= for_cost 
    start = for_loop.range_expr.start
    print(start)
    end = for_loop.range_expr.end
    print(end)
    step = for_loop.range_expr.step if for_loop.range_expr.step else 1

    for i in range(start, end, step):
        dict[for_loop.var] = i
        dict["chips"] -= i
        if check_chips(dict["chips"]):
            for function in for_loop.body:
                interpreter(function, dict)

def interpret_while(while_loop, dict):
    print("entered while")
    while_cost = 5
    condition = eval(while_loop.condition, {}, dict)
    while condition:
        dict["chips"] -= while_cost
        if check_chips(dict["chips"]):
            for function in while_loop.body:
                interpreter(function, dict)
            # Reevaluate the condition in case it's changed in the loop body
            condition = eval(while_loop.condition, {}, dict)

def interpret_if(if_statement, dict):
    print("entered if")
    if_cost = 1
    print(if_statement.condition)
    condition = eval(if_statement.condition, {}, dict)
    if condition:
        print("entered here")
        dict["chips"] -= if_cost
        if check_chips(dict["chips"]):
                print("entered here?")
                print(if_statement.body)
                for function in if_statement.body:
                    interpreter(function, dict)
    elif if_statement.else_body:
        dict["chips"] -= if_cost
        if check_chips(dict["chips"]):
            for function in if_statement.else_body:
                interpreter(function, dict)

def interpet_var(variable_declaration, dict):
    print("entered var")
    var_cost = 3
    value = variable_declaration.value
    dict[variable_declaration.name] = value
    dict["chips"] -= var_cost
    check_chips(dict["chips"])

#interpreting instruments
def interpret_call(call, dict):
    value = call.calling
    if call.ending == "!":
        dict["chips"] -= 25
        check_chips(dict["chips"])
        print("\033[35mBy Law:\033[0m")
        print(value)
        return
    dict["chips"] -= 5
    check_chips(dict["chips"])
    decision = random.randint(0 ,1)
    if decision == 1:
            print("\033[33mSuccessful Call!\033[0m")
            print(value)
            if call.ending.startswith("$"):
                earnings = 5 * call.ending.count("$")
                print(f"You earned {earnings} chips.")
                dict["chips"] += 5 * call.ending.count("$")
            else:
                print("Invalid ending character")
    else:
        print("\033[31mUnsuccessful Call.\033[0m")
                

def interpret_calc(calc, dict):
    print(calc.calculation)
    result = eval(str(calc.calculation), dict)
    print(f"This was the result: {result}")
    dice = result + 15
    print(dice)
    roll = random.randint(0, dice)
    print(roll)
    bet = calc.bet
    if bet == "over" or bet == "under" or bet == "bullseye":
        if roll > result:
            print("Over!")
            if bet == "over":
                print("You win!")
            else:
                print("Loss!")
        elif roll < result:
            print("Under!")
            if bet == "under":
                print("You win!")
            else:
                print("Loss!")
        else:
            print("Bullseye!")
        print(result)


def interpret_roulette(roulette, dict):
    colors = []

    for i, element in enumerate(roulette.elements):
        if i == 0:
            colors.append("green")
        elif i % 2 == 1:
            colors.append("red")
        else:
            colors.append("black")
    # Evaluate each expression in the elements list
    elements = [eval(str(element), {}, dict) for element in roulette.elements]
    # Store the array in the dictionary using the given name
    dict[roulette.name] = {"element": elements, "colors": colors}

def interpret_access(access, dict):
    name = access.array
    index = eval(str(access.index), {}, dict)
    if name in dict:
        roulette = dict[name]
        elements = roulette["element"]
        index_colors = roulette["colors"]
        if 0 <= index < len(elements):
            element = elements[index]
            color = index_colors[index]

            colors = ['green', 'red', 'black']
            color_choice = random.choice(colors)
            if color_choice == color:
                print(f"{elements[index]}")
            else:
                print("Spin unsuccessful")
    else:
        print("Array does not exist")

#Interpretting Wheels
def interpret_nonparam(nonparam):
    name = nonparam.name
    if name == "Test":
        print("Hello!")
    elif name == "Blackjack":
        black_jack()


def interpret_param(param, dict):
    name = param.name
    print(name)
    if name == "Poker":
        interpret_Poker(param, dict)
    elif name == "HorseRace":
        horse_Race(param)
    elif name == "Baccarat":
        baccarat(param)
    elif name == "call":
        interpret_call(param, dict)
    else:
        print("Still worked!")


# Poker Implementation
def interpret_Poker(param, dict):
    hands = param.params[0]
    deck = create_deck()
    shuffle_deck(deck)
        
    # Deal hands
    hands = deal_hands(deck, hands)
        
    # Print each player's hand
    for i, hand in enumerate(hands, start=1):
        print(f"Player {i}'s hand: {', '.join(hand)}")
        
    # Compare hands and determine the winner
    compare_hands(hands)
    
def create_deck():
    suits = ['H', 'D', 'C', 'S']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    return [f"{rank} {suit}" for suit in suits for rank in ranks]

# Step 2: Shuffle the deck
def shuffle_deck(deck):
    random.shuffle(deck)

# Step 3: Deal hands
def deal_hands(deck, num_players, cards_per_hand=5):
    return [deck[i*cards_per_hand:(i+1)*cards_per_hand] for i in range(num_players)]

# Step 4: Rank hands
def rank_hand(hand):
    rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
                   '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    card_ranks = sorted([rank_values[card.split()[0]] for card in hand], reverse=True)
    rank_counts = Counter(card_ranks)
    
    # Determine hand ranking (simplified poker rules)
    if len(rank_counts) == 5 and card_ranks[0] - card_ranks[4] == 4:
        return (5, card_ranks)  # Straight
    elif 4 in rank_counts.values():
        return (4, card_ranks)  # Four of a kind
    elif sorted(rank_counts.values()) == [2, 3]:
        return (3, card_ranks)  # Full house
    elif 3 in rank_counts.values():
        return (2, card_ranks)  # Three of a kind
    elif list(rank_counts.values()).count(2) == 2:
        return (1, card_ranks)  # Two pair
    elif 2 in rank_counts.values():
        return (0.5, card_ranks)  # One pair
    else:
        return (0, card_ranks)  # High card

# Step 5: Compare hands
def compare_hands(hands):
    hand_rankings = []

    for hand in hands:
        hand_rank = rank_hand(hand)
        hand_rankings.append((hand, hand_rank))

    # Sort by hand rank first (higher rank wins), then by card ranks if needed
    hand_rankings.sort(key=lambda x: (x[1][0], x[1][1]), reverse=True)

    winning_hand, winning_rank = hand_rankings[0]

    # Output the winning hand and its type
    hand_type = {
        5: "Straight",
        4: "Four of a Kind",
        3: "Full House",
        2: "Three of a Kind",
        1: "Two Pair",
        0.5: "One Pair",
        0: "High Card"
    }

    print(f"The winning hand is: {winning_hand}")
    print(f"The hand type is: {hand_type[winning_rank[0]]}")

    if hands[0] == winning_hand:
        print("User won!")
    else:
        print("User lost!")

# Black jack Implementation
def black_jack():
    player_value = random.randint(2, 21)
    dealer_value = random.randint(2, 21)

    print(f"{player_value} and {dealer_value}")

    if player_value == 21 and dealer_value == 21:
        print("Tie!")
        return
    elif player_value == 21:
        print("BlackJack!")
        return
    elif dealer_value == 21:
        print("Dealer Blackjack!")
        return

    while player_value < 17:
            player_value += random.randint(1, 11)
    
    print(f"Player value: {player_value} ")
    if player_value == 21:
        print("Blackjack!")
        return
    elif player_value > 21:
        print("Bust!")
        return
    
    while dealer_value < 17:
        dealer_value += random.randint(1, 11)
    
    print(f"Delear value: {dealer_value}")
    if dealer_value == 21:
        print("Dealer Blackjack!")
        return
    elif dealer_value > 21:
        print("Dealear Bust!")
        return
    
    if player_value > dealer_value:
        print("Player win!")
    elif player_value == dealer_value:
        print("Tie!")
    else:
        print("Dealer Won!")

 # Horse Race Implmentation
def horse_Race(player_horse):
   num_horses = 7
   horses = [0] * num_horses
   race_distance = 25

   print("Horse Race has begun!")

    #keep race going
   while True:
    #update position of horse
    for i in range(num_horses):
        horses[i] += random.randint(1, 3)

    for i, position in enumerate(horses):
        if position >= race_distance:
            print(f"Horse {i + 1} beats the race at {position} meters!")
            print(f"Horse {i + 1} wins!")
            if i + 1 == player_horse:
                print("Player won!")
            else:
                print("player lost!")
            return
        
    winning_horse, highest_position = max(enumerate(horses), key=lambda x: x[1])
    print(f"\nHorse {winning_horse + 1} is in the lead at {highest_position} meters...")
    time.sleep(0.2)

#baccarat implementation
def draw_card():
    """Draw a card with values between 1 and 9, inclusive."""
    return random.randint(1, 9)

def calculate_score(hand):
    """Calculate the Baccarat score of a hand."""
    return sum(hand) % 10

def baccarat(bet):
    # Initial hands
    player_hand = [draw_card(), draw_card()]
    banker_hand = [draw_card(), draw_card()]

    print(f"Player's cards: {player_hand}, Score: {calculate_score(player_hand)}")
    print(f"Banker's cards: {banker_hand}, Score: {calculate_score(banker_hand)}")

    player_score = calculate_score(player_hand)
    banker_score = calculate_score(banker_hand)

    # Simplified third card rule
    if player_score < 6:
        player_hand.append(draw_card())
        player_score = calculate_score(player_hand)
        print(f"Player draws a card: {player_hand[-1]}. New score: {player_score}")

    if banker_score < 6:
        banker_hand.append(draw_card())
        banker_score = calculate_score(banker_hand)
        print(f"Banker draws a card: {banker_hand[-1]}. New score: {banker_score}")

    print(f"Final Player's hand: {player_hand}, Score: {player_score}")
    print(f"Final Banker's hand: {banker_hand}, Score: {banker_score}")

    # Determine winner
    if player_score > banker_score:
        print("Player bet wins!")
        if bet == "Player":
            print("User won!") 
        else:
            print("Loss")
    elif banker_score > player_score:
        print("Banker bet wins!")
        if bet == "Banker":
            print("User Won!")
        else:
            print("Loss!")
    else:
        print("It's a tie!")    
           

        

    
if __name__ == "__main__":
    start()


    
