from textx import metamodel_from_file
import os
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
    print("Welcome to Citadel! This is where you interpret your Fortuna",
          "files.")
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
    if function_name == "WhileLoop":
        interpret_while(function, dict)
    if function_name == "IfStatement":
        interpret_if(function, dict)
    if function_name == "VariableDeclaration":
        interpet_var(function, dict)
    if function_name == "Call":
        interpret_call(function)
    if function_name == "Calculation":
        interpret_calc(function, dict)
    if function_name == "Roulette":
        interpret_roulette(function, dict)
    if function_name == "NonParamFunction":
        interpret_nonparam(function)
    if function_name == "ParamFunction":
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
        dict["chips"] -= if_cost
        if check_chips(dict["chips"]):
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
def interpret_call(call):
    value = call.calling
    decision = random.randint(0 ,1)
    print(f"This was the decision: {decision}")
    if decision == 1:
        print(value)

def interpret_calc(calc, dict):
    result = eval(calc.calculation, {}, dict)
    dice = result + 15
    print(dice)
    roll = random.randint(0, dice)
    print(roll)
    bet = calc.bet
    if bet == "over" or bet == "under" or bet == "bullseye":
        if roll >= result:
            print("Over!")
            if bet == "over":
                print("You win!")
            else:
                print("Loss!")
        elif roll <= result:
            print("Under!")
            if bet == "under":
                print("You win!")
            else:
                print("Loss!")
        else:
            print("Bullseye!")
        print(result)

def interpret_roulette(roulette, dict):
    # Evaluate each expression in the elements list
    elements = [eval(str(element), {}, dict) for element in roulette.elements]
    # Store the array in the dictionary using the given name
    dict[roulette.name] = elements

#Interpretting Wheels
def interpret_nonparam(nonparam):
    name = nonparam.name
    if name == "Test":
        print("Hello!")


def interpret_param(param, dict):
    name = param.name
    if name == "Poker":
        interpret_Poker(param, dict)
    else:
        print("Still worked!")

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

def black_jack():
    deck = create_deck()
    shuffle_deck(deck)

    
if __name__ == "__main__":
    start()


    
