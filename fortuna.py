from textx import metamodel_from_file
import time
import sys
import random
import re
from collections import Counter

#loading our model from the given name
def load_model(file_name):
    fortuna_mm = metamodel_from_file('fortuna.tx')

    global fortuna_model
    fortuna_model = fortuna_mm
    fortuna_model = fortuna_mm.model_from_file(file_name)
    return fortuna_model


#starting point. This will load the model and interpet the functions inside the file
def start():
    print("Welcome to Citadel! This is where you interpret your Fortuna files.")
    file_name = input("Please give us the name of your Fortuna File: ")

    model = load_model(file_name)
    user_chips = 2000 + model.chips #in an real scenario, this would a user's money balance that they have put in.
    if model.chips <= user_chips:
        dict = {"chips": model.chips} # dictionary that will track our variables, initialize chips
        dict["balance"] = user_chips - model.chips #also keep track of the user's remaining balance
        print(f"You have entered the program with {dict["chips"]} chips. Your remaning balance is: {dict["balance"]}")
        for function in model.functions:
            interpreter(function, dict) #main interpreter

#function needed to check if the use has not bankrupt before starting a function
def check_chips(current_balance):
    if current_balance <= 0:
        print("\033[31mBankrupt! Ran out of Chips!!\033[0m")
        sys.exit()
    else:
        return True

#interpreter that takes in the TextX class name in order to interpet
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
        interpret_nonparam(function, dict)
    elif function_name == "ParamFunction":
        interpret_param(function, dict)

#
#    ******Pillars*****
#   Essential functions similar to normal programming languages.
#   Have a relatively low cost since they are necessary for the language.
#   Consists of loops, if statements, and variables.
#    ******Pillars*****

#interpreter for for loops
def interpret_for(for_loop, dict):
    for_cost = 20
    dict["chips"] -= for_cost
    check_chips(dict["chips"])
    #keep track of the iterations
    start = for_loop.range_expr.start
    end = for_loop.range_expr.end
    step = for_loop.range_expr.step if for_loop.range_expr.step else 1

    #actual looping, cost of an iterations is the same as i * 5, large loops can be costly.
    for i in range(start, end, step):
        dict[for_loop.var] = i
        dict["chips"] -= i * 5
        if check_chips(dict["chips"]):
            for function in for_loop.body:
                interpreter(function, dict)

#allowing for comparisons
def format_condition(condition):
    condition = re.sub(r'([<>=!]=?|and|or|not)', r' \1 ', condition)
    return condition
#interpeter for while loops
def interpret_while(while_loop, dict):
    while_cost = 20
    for var in dict.keys():
        if var in while_loop.condition:
            replaced = while_loop.condition.replace(var, str(dict[var]))
            formatted_condition = format_condition(replaced)
        else:
          formatted_condition = format_condition(while_loop.condition)  
    
    print(formatted_condition)
    condition = eval(formatted_condition, {}, dict) #evaluate the given conditon
    while condition:
        dict["chips"] -= while_cost #cost is flat
        if check_chips(dict["chips"]):
            for function in while_loop.body:
                interpreter(function, dict)
            condition = eval(formatted_condition, {}, dict)

#interpreter for if statments
def interpret_if(if_statement, dict):
    if_cost = 30

    # Evaluate the main if condition
    for var in dict.keys():
        if var in if_statement.condition:
            replaced = if_statement.condition.replace(var, str(dict[var]))
            formatted_condition = format_condition(replaced)
            break
    else:
        formatted_condition = format_condition(if_statement.condition)

    condition = eval(formatted_condition, {}, dict)

    # If the main if condition is true
    if condition:
        dict["chips"] -= if_cost
        check_chips(dict["chips"])
        for function in if_statement.body:
            interpreter(function, dict)
        return

    # Evaluate all elif conditions
    for elif_cond, elif_body in zip(if_statement.elseif, if_statement.elif_body):
        for var in dict.keys():
            if var in elif_cond:
                replaced = elif_cond.replace(var, str(dict[var]))
                formatted_elif = format_condition(replaced)
                break
        else:
            formatted_elif = format_condition(elif_cond)

        elif_condition = eval(formatted_elif, {}, dict)

        if elif_condition:
            dict["chips"] -= if_cost
            check_chips(dict["chips"])
            # Treat elif_body as a single callable object
            interpreter(elif_body, dict)
            return

    # If no elif conditions were true, check for else
    if hasattr(if_statement, 'else_body') and if_statement.else_body:
        dict["chips"] -= if_cost
        check_chips(dict["chips"])
        for function in if_statement.else_body:
            interpreter(function, dict)
#initialization for variables, keep in dictionary
def interpet_var(variable_declaration, dict):
    var_cost = 5
    value = eval(str(variable_declaration.value), {}, dict)
    dict[variable_declaration.name] = value
    dict["chips"] -= var_cost
    check_chips(dict["chips"])


#    ******Instruments*****
#   The functions necessary for output.
#   Outputs have a twist however.
#   Instruments have two output types: Betful and Lawful.
#   Betful output involves the using placing a bet and playing the instrument game.
#   Lawful output is when you need the output straight away, but will cost you.
#   These is how you will print values, make calculations and access arrays.
#    ******Instruments*****

#calls is how you print, however it is a coin toss. If you win the coin toss, you get the call
def interpret_call(call, dict):
    value = call.calling
    if value in dict.keys():
        value = call.calling.replace(value, str(dict[value]))
    if call.ending == "!": #checks if lawful call, if so, avoid game and just print
        dict["chips"] -= 75
        check_chips(dict["chips"])
        print("\033[35mBy Law:\033[0m")
        print(value)
        return
    dict["chips"] -= 25 * call.ending.count("$") #normal cost of calling
    check_chips(dict["chips"]) 
    decision = random.randint(0 ,1) #coin toss
    if decision == 1:
            print("\033[33mSuccessful Call!\033[0m")
            print(value)
            if call.ending.startswith("$"):
                earnings = 50 * call.ending.count("$") #The amount of blinds added at the end of the function, the higher the payout
                print(f"You earned {earnings} chips.")
                dict["chips"] += earnings
            else:
                print("Invalid ending character")
    else:
        print("\033[31mUnsuccessful Call.\033[0m")
                
#Calculation is the function that evualates mathematical expressions
#However, the result will be a into a die of size result + 15
#In the calculation call, you have to guess if the die roll will be over the calculated result, under the result, or Bullseye, right on the dot.
def interpret_calc(calc, dict):
    print("\033[32mCalculation!\033[0m")
    #checks for lawful call
    if calc.ending == "!":
        dict["chips"] -= 75
        check_chips(dict["chips"])
        result = eval(str(calc.calculation), {}, dict)
        print("\033[35mBy Law:\033[0m")
        print(result)
        return
    
    if calc.ending.startswith("$"):
        dict["chips"] -= 50 * calc.ending.count("$")
        result = eval(str(calc.calculation), dict)
        die = result + 15
        roll = random.randint(1, die)
        bet = calc.bet
        if bet == "over" or bet == "under" or bet == "bullseye": #checks what the user guessed on
            if roll > result:
                print("Over!")
                if bet == "over":
                    print("\033[33mYou guessed correctly!\033[0m")
                    earnings = 100 * calc.ending.count("$")
                    print(f"you earned: {earnings} chips")
                    dict["chips"] += earnings
                else:
                    print("\033[31mYou guessed wrong.\033[0m")
            elif roll < result:
                print("Under!")
                if bet == "under":
                    print("\033[33mYou guessed correctly!\033[0m")
                    earnings = 100 * calc.ending.count("$")
                    print(f"you earned: {earnings} chips")
                    dict["chips"] += earnings
                else:
                    print("\033[31mYou guessed wrong.\033[0m")
            else:
                print("Bullseye!")
                if bet == "bullseye":
                    print("\033[33mYou guessed correctly!\033[0m")
                    earnings = 200 * calc.ending.count("$") #hitting a bullseye will net higher earnings
                    print(f"you earned: {earnings} chips")
                    dict["chips"] += earnings
                else:
                    print("\033[31mYou guessed wrong.\033[0m")
            print(result) #calculations will print out your result regardless if win or lose
    else:
        print("Invalid ending")

#Roulettes are the arrays of this language, every element is assigned a color with the first being green, and the rest being red or black
def interpret_roulette(roulette, dict):
    dict["chips"] -= 30
    check_chips(dict["chips"])
    colors = []

    #assigns colors to the elements
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

#Roulette elements can be acesssed through a roulette spin
#If the wheel lands on a color that matches the element you are looking for, output the element
#Else, no output and the spin is considered unsucessful
#Can be lawful
def interpret_access(access, dict):
    if access.ending == "!":
        dict["chips"] -= 100
        check_chips(dict["chips"])
        print("By Law.")
        name = access.array
        roulette = dict[name]
        elements = roulette["colors"]
        index = eval(str(access.index), {}, dict)
        print(f"{elements[index]}")
        return
    
    if access.ending.startswith("$"):
        dict["chips"] -= 40 * access.ending.count("$")
        earnings = 80 * access.ending.count("$")
        check_chips(dict["chips"])
        name = access.array #gather name of roulette to verify it exists
        index = eval(str(access.index), {}, dict) #get the index
        if name in dict:
            roulette = dict[name] #find the specific roulette 
            elements = roulette["element"] #gather the elements
            index_colors = roulette["colors"] #gather the colors
            if 0 <= index < len(elements):
                element = elements[index]
                color = index_colors[index]
                #spinning the wheel
                colors = ['green', 'red', 'black']
                color_choice = random.choice(colors)
                if color_choice == color:
                    print("\033[33mSuccessful Spin!.\033[0m")
                    print(f"You earned: {earnings} chips.")
                    dict["chips"] += earnings
                    print(element)
                else:
                    print("\033[31mSpin unsuccessful.\033[0m")
            else:
                print("Index out of bounds.")
        else:
            print("Array does not exist")
    else:
        print("Ending is incorrect.")

#    ******Wheels*****
#   The functions necesary for getting more money.
#   Classic casino game.
#   Bets have to be placed.
#   Some functions may need parameters while others don't.
#   Bets are pricey but if won, will net high earnings to keep the program running.
#    ******Wheels*****


#interpeting functions with no parameters 
def interpret_nonparam(nonparam, dict):
    name = nonparam.name
    if name == "Blackjack":
        black_jack(nonparam, dict)
    elif name == "check":
        check_balance(dict)
    else:
        print("Invalid function.")

#interpretting functions with parameters
def interpret_param(param, dict):
    name = param.name
    if name == "Poker":
        interpret_Poker(param, dict)
    elif name == "HorseRace":
        horse_Race(param, dict)
    elif name == "Baccarat":
        baccarat(param, dict)
    elif name == "call":
        interpret_call(param, dict)
    else:
        print("Invalid function.")

#helper function that helps user check balance at any time. Does not cost anything and is marked with an Free x.
def check_balance(dict):
    chips = dict["chips"]
    user_balance = dict["balance"] + chips
    print(f"Your chip count is: {chips}. Your total balance is {user_balance}.")

# Poker Implementation
def interpret_Poker(param, dict):
    print("\033[32mPoker!\033[0m")
    if param.ending.startswith("$"):
        dict["chips"] -= 50 * param.ending.count("$") * param.params[0] #account for number of competing hands
        check_chips(dict["chips"])
        poker_payout = 1000
        earnings = poker_payout * param.ending.count("$") * param.params[0]
        hands = param.params[0]
        deck = create_deck()
        shuffle_deck(deck)
            
        # Deal hands
        hands = deal_hands(deck, hands)
            
        # Print each player's hand
        for i, hand in enumerate(hands, start=1):
            print(f"Player {i}'s hand: {', '.join(hand)}")
            
        # Compare hands and determine the winner
        compare_hands(hands, dict, earnings)
    else:
        print("wrong ending.")
    
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
def compare_hands(hands, dict, earnings):
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
        print("\033[33mYou won!\033[0m")
        print(f"Earned: {earnings} chips.")
        dict["chips"] += earnings

    else:
        print("\033[31mYou lost!\033[0m")

# Black jack Implementation
# Checks if any of the get a 21 and if not, keep hitting until any of them above 17 which then they compare.
def black_jack(nonparam, dict):
    print("\033[32mBlackJack!\033[0m")
    if nonparam.ending.startswith("$"):
        dict["chips"] -= 75 * nonparam.ending.count("$")
        check_chips(dict["chips"])
        black_jack_payout = 150
        earnings = black_jack_payout * nonparam.ending.count("$")
        player_value = random.randint(2, 21)
        dealer_value = random.randint(2, 21)

        print(f"Player hand: {player_value} and Dealer hand:{dealer_value}")

        if player_value == 21 and dealer_value == 21:
            print("Tie!")
            dict["chips"] += 75
            return
        elif player_value == 21:
            print("\033[33mBlackJack!\033[0m")
            print(f"You earned: {earnings} chips.")
            dict["chips"] += earnings
            return
        elif dealer_value == 21:
            print("\033[31mDealer Blackjack.\033[0m")
            return

        while player_value < 17:
                player_value += random.randint(1, 11)
        
        print(f"Player value: {player_value} ")
        if player_value == 21:
            print("\033[33mBlackJack!\033[0m")
            print(f"You earned: {earnings} chips.")
            dict["chips"] += earnings
            return
        elif player_value > 21:
            print("\033[31mBust.\033[0m")
            return
        
        while dealer_value < 17:
            dealer_value += random.randint(1, 11)
        
        print(f"Delear value: {dealer_value}")
        if dealer_value == 21:
            print("\033[31mDealer Blackjack.\033[0m")
            return
        elif dealer_value > 21:
            print("\033[33mDealer Bust!\033[0m")
            print(f"You earned: {earnings} chips.")
            dict["chips"] += earnings
            return
        
        if player_value > dealer_value:
            print("\033[33mPlayer Win!\033[0m")
            print(f"You earned: {earnings} chips.")
            dict["chips"] += earnings
        elif player_value == dealer_value:
            print("Tie!")
            dict["chips"] += 75 * nonparam.ending.count("$")
        else:
            print("\033[31mDealer won.\033[0m")
    else:
        print("wrong ending.")

 # Horse Race Implmentation
def horse_Race(player_horse, dict):
   if player_horse.ending.startswith("$"):
    dict["chips"] -= 100 * player_horse.ending.count("$")
    check_chips(dict["chips"])
    horse_payout = 200
    earnings = horse_payout * player_horse.ending.count("$")
    num_horses = 7
    horses = [0] * num_horses
    race_distance = 25

    print("\033[32mHorse Race has begun!\033[0m")

        #keep race going
    while True:
        #update position of horse
        for i in range(num_horses):
            horses[i] += random.randint(1, 3)

        for i, position in enumerate(horses):
            if position >= race_distance:
                print(f"Horse {i + 1} beats the race at {position} meters!")
                print(f"Horse {i + 1} wins!")
                if i + 1 in player_horse.params:
                    print("\033[33mPlayer Horse won!\033[0m")
                    print(f"You earned: {earnings} chips.")
                    dict["chips"] += earnings
                else:
                    print("\033[31mPlayer horse lost.\033[0m")
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

def baccarat(bet, dict):
    print("\033[32mBaccarat!\033[0m")
    if bet.ending.startswith("$"):
        dict["chips"] -= 60 * bet.ending.count("$")
        check_chips(dict["chips"])
        payout = 120
        earnings = payout * bet.ending.count("$")
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
            if "Player" in bet.params:
                print("\033[33mYou won!\033[0m")
                print(f"You earned: {earnings} chips.")
                dict["chips"] += earnings
            else:
                print("\033[31mYou lost.\033[0m")
        elif banker_score > player_score:
            print("Banker bet wins!")
            if "Banker" in bet.params:
                print("\033[33mYou won!\033[0m")
                print(f"You earned: {earnings} chips.")
                dict["chips"] += earnings
            else:
                print("\033[31mYou lost.\033[0m")
        else:
            print("It's a tie!")
            dict["chips"] += 60 * bet.ending.count("$")    
           

        

    
if __name__ == "__main__":
    start()


    
