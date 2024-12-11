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
    user_chips = 2000
    if model.chips <= user_chips:
        dict = {"chips": model.chips} # dictionary that will track our variables, initialize chips
        dict["balance"] = user_chips - model.chips
        print(f"You have entered the program with {dict["chips"]} chips. Your remaning balance is: {dict["balance"]}")
        for function in model.functions:
            interpreter(function, dict) #main interpreter

def check_chips(current_balance):
    if current_balance <= 0:
        print("\033[31mBankrupt! Ran out of Chips!!\033[0m")
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
        interpret_nonparam(function, dict)
    elif function_name == "ParamFunction":
        interpret_param(function, dict)

#interpetting pillars
def interpret_for(for_loop, dict):
    for_cost = 50
    dict["chips"] -= for_cost 
    start = for_loop.range_expr.start
    end = for_loop.range_expr.end
    step = for_loop.range_expr.step if for_loop.range_expr.step else 1

    for i in range(start, end, step):
        dict[for_loop.var] = i
        dict["chips"] -= i * 5
        if check_chips(dict["chips"]):
            for function in for_loop.body:
                interpreter(function, dict)

def interpret_while(while_loop, dict):
    while_cost = 20
    condition = eval(while_loop.condition, {}, dict)
    while condition:
        dict["chips"] -= while_cost
        if check_chips(dict["chips"]):
            for function in while_loop.body:
                interpreter(function, dict)
            # Reevaluate the condition in case it's changed in the loop body
            condition = eval(while_loop.condition, {}, dict)

def interpret_if(if_statement, dict):
    if_cost = 30
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
    var_cost = 1
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
    dict["chips"] -= 5 * call.ending.count("$")
    check_chips(dict["chips"])
    decision = random.randint(0 ,1)
    if decision == 1:
            print("\033[33mSuccessful Call!\033[0m")
            print(value)
            if call.ending.startswith("$"):
                earnings = 10 * call.ending.count("$")
                print(f"You earned {earnings} chips.")
                dict["chips"] += earnings
            else:
                print("Invalid ending character")
    else:
        print("\033[31mUnsuccessful Call.\033[0m")
                

def interpret_calc(calc, dict):
    print("\033[32mCalculation!\033[0m")
    if calc.ending == "!":
        dict["chips"] -= 25
        check_chips(dict["chips"])
        result = eval(str(calc.calculation), {}, dict)
        print("\033[35mBy Law:\033[0m")
        print(result)
        return
    
    if calc.ending.startswith("$"):
        dict["chips"] -= 10 * calc.ending.count("$")
        result = eval(str(calc.calculation), dict)
        dice = result + 15
        roll = random.randint(0, dice)
        bet = calc.bet
        if bet == "over" or bet == "under" or bet == "bullseye":
            if roll > result:
                print("Over!")
                if bet == "over":
                    print("\033[33mYou guessed correctly!\033[0m")
                    earnings = 20 * calc.ending.count("$")
                    print(f"you earned: {earnings} chips")
                    dict["chips"] += earnings
                else:
                    print("You guessed wrong!")
            elif roll < result:
                print("Under!")
                if bet == "under":
                    print("\033[33mYou guessed correctly!\033[0m")
                    earnings = 20 * calc.ending.count("$")
                    print(f"you earned: {earnings} chips")
                    dict["chips"] += earnings
                else:
                    print("You guessed wrong!")
            else:
                print("Bullseye!")
                print("\033[33mYou guessed correctly!\033[0m")
                earnings = 50 * calc.ending.count("$")
                print(f"you earned: {earnings} chips")
                dict["chips"] += earnings
            print(result)
    else:
        print("Invalid ending")


def interpret_roulette(roulette, dict):
    dict["chips"] -= 5
    check_chips(dict["chips"])
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
    if access.ending == "!":
        dict["chips"] -= 25
        check_chips(dict["chips"])
        print("By Law.")
        name = access.array
        roulette = dict[name]
        elements = roulette["colors"]
        index = eval(str(access.index), {}, dict)
        print(f"{elements[index]}")
        return
    
    if access.ending.startswith("$"):
        dict["chips"] -= 5
        check_chips(dict["chips"])
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
                    print("\033[33mSuccessful Spin!.\033[0m")
                    print(f"{elements[index]}")
                else:
                    print("\033[31mSpin unsuccessful.\033[0m")
        else:
            print("Array does not exist")
    else:
        print("Ending is incorrect.")

#Interpretting Wheels
def interpret_nonparam(nonparam, dict):
    name = nonparam.name
    if name == "Test":
        print("Hello!")
    elif name == "Blackjack":
        black_jack(nonparam, dict)
    elif name == "check":
        check_balance(dict)


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


def check_balance(dict):
    chips = dict["chips"]
    user_balance = dict["balance"] + chips
    print(f"Your chip count is: {chips}. Your total balance is {user_balance}.")

# Poker Implementation
def interpret_Poker(param, dict):
    print("\033[32mPoker!\033[0m")
    if param.ending.startswith("$"):
        dict["chips"] -= 50 * param.ending.count("$")
        check_chips(dict["chips"])
        poker_payout = 100
        earnings = poker_payout * param.ending.count("$")
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
def black_jack(nonparam, dict):
    print("\033[32mBlackJack!\033[0m")
    if nonparam.ending.startswith("$"):
        dict["chips"] -= 75 * nonparam.ending.count("$")
        check_chips(dict["chips"])
        black_jack_payout = 150
        earnings = black_jack_payout * nonparam.ending.count("$")
        player_value = random.randint(2, 21)
        dealer_value = random.randint(2, 21)

        print(f"{player_value} and {dealer_value}")

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


    
