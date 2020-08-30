import random
from sys import exit
import sqlite3


def print_main_menu():
    print()
    print("1. Create an account")
    print("2. Log into account")
    print("0. Exit")


def print_log_in_menu():
    print()
    print("1. Balance")
    print("2. Add income")
    print("3. Do transfer")
    print("4. Close account")
    print("5. Log out")
    print("0. Exit")


def exxit():
    print("Bye!")
    exit()


def create_db():
    conn = sqlite3.connect("card.s3db")
    # conn.execute("drop table card;")
    conn.execute("create table if not exists card (id INTEGER, number TEXT, pin TEXT, balance INTEGER DEFAULT 0);")
    conn.commit()
    conn.close()


def gen_bin():
    return 400000


def gen_account():
    num = ""
    for i in range(1,10):
        num += str(random.randint(0, 9))
    return num


def get_card_no_sum(card_no_pre):
    
    digits_odd_by2 = []
    for i in range(0, len(card_no_pre)):
        if i % 2 == 0:
            digits_odd_by2.append(str(int(card_no_pre[i]) * 2))
        else:
            digits_odd_by2.append(card_no_pre[i])
    
    subs9_over9 = []
    for i in digits_odd_by2:
        if int(i) > 9:
            subs9_over9.append(str(int(i) - 9))
        else:
            subs9_over9.append(i)
    
    sum_no = 0
    for i in subs9_over9:
        sum_no += int(i)
    
    return sum_no


def get_closest10(num):
    closest10 = 0
    temp = 0
    for i in range(0, 10):
        temp = num + i
        if temp % 10 == 0:
            closest10 = temp
            break
            
    return closest10
    
    
def gen_checksum(card_no_pre):
    sum_no = get_card_no_sum(card_no_pre)
    closest10 = get_closest10(sum_no)
    checksum = (closest10 - sum_no)
    return checksum


def verify_checksum(card_no):
    checksum = gen_checksum(card_no[:-1])

    if int(card_no[-1:]) == checksum:
        return True
    
    return False

    
def gen_card_number():
    card_no_pre = str(gen_bin()) + "" + str(gen_account())
    card_no = str(card_no_pre) + "" + str(gen_checksum(card_no_pre))
    return card_no
    
    
def gen_pin():
    pin = ""
    for i in range(1, 5):
        pin += str(random.randint(0, 9))
        
    return pin


def read_cards():
    cards = {}
    try:
        with open("cards.txt", "r") as f1:
            for i in f1:
                cards[i.split("=")[0]] = [i.split("=")[1], i.split("=")[2].rstrip("\n")]
    except OSError:
        cards = {}
    
    return cards


def read_cards_from_db():
    cards = {}
    try:
        conn = sqlite3.connect("card.s3db")
        cur = conn.execute("select number, pin, balance from card;")
        for i in cur:
            cards[i[0]] = [i[1], i[2]]
        conn.close()
    except:
        conn.close()

    return cards


def save_card(card_no, pin, balance):
    
    cards = read_cards()
    if not card_no in cards:
        with open("cards.txt", "a") as f1:
            print("{}={}={}".format(str(card_no), str(pin), str(balance)), end="\n", file=f1, flush=True)
        return True
    else:
        return False


def save_card_to_db(card_no, pin, balance):

    cards = read_cards_from_db()
    if card_no not in cards:
        try:
            conn = sqlite3.connect("card.s3db")
            cur = conn.cursor()
            cur.execute("select coalesce(max(id), 0) + 1 from card;")
            new_id = cur.fetchone()[0]
            cur.execute("insert into card(id, number, pin, balance) values (?, ?, ?, ?);", (new_id, str(card_no), str(pin), balance))
            conn.commit()
            conn.close()
            return True
        except:
            conn.close()
            return False
    else:
        return False


def add_income(card_no, income):
    try:
        conn = sqlite3.connect("card.s3db")
        cur = conn.cursor()
        cur.execute("update card set balance = balance + ? where number = ?;", (income, card_no))
        conn.commit()
        conn.close()
        print()
        print("Income was added!")
        return True
    except:
        conn.close()
        return False


def do_transfer(src_card_no, target_card_no, amount):
    try:
        conn = sqlite3.connect("card.s3db")
        cur = conn.cursor()
        cur.execute("update card "
                    "set balance = balance + ? "
                    "where number = ?;", (amount, target_card_no))
        cur.execute("update card "
                    "set balance = balance - ? "
                    "where number = ?;", (amount, src_card_no))
        conn.commit()
        conn.close()
        print("Success!")
    except:
        conn.close()


def delete_account(card_no):
    try:
        print(card_no)
        conn = sqlite3.connect("card.s3db")
        cur = conn.cursor()
        cur.execute("delete from card where number = ?;", (str(card_no),))
        conn.commit()
        conn.close()
        print("The account has been closed!")
        return True
    except:
        conn.close()
        return False


# create db
create_db()


while 1 == 1:
    
    print_main_menu()
    option1 = input()

    cards = read_cards_from_db()

    # utworz konto
    if option1 == "1":

        while 1 == 1:
            card_number = gen_card_number()
            if card_number in cards:
                continue
            pin = gen_pin()
            break
        
        save_card_to_db(card_number, pin, 0)

        print()
        print("Your card has been created")
        print("Your card number:")
        print("{}".format(card_number))
        print("Your card PIN:")
        print("{}".format(pin))
        
    # logowanie
    elif option1 == "2":
        
        print("Enter your card number:")
        prov_card_no = input()
        print("Enter your PIN:")
        prov_pin = input()
        
        if not verify_checksum(prov_card_no):
            print("Wrong card number or PIN!")
            continue

        print()
        if prov_card_no in cards:
            if prov_pin == cards[prov_card_no][0]:
                print("You have successfully logged in!")
            
                print_log_in_menu()
                option2 = input()
                while 1 == 1:
                    cards = read_cards_from_db()
                    if option2 == "1":
                        print()
                        print("Balance: {}".format(str(cards[prov_card_no][1])))
                    elif option2 == "2":
                        print("Enter income:")
                        income = int(input())
                        add_income(prov_card_no, income)
                    elif option2 == "3":
                        print("Transfer")
                        target_card_no = input()
                        if verify_checksum(target_card_no):
                           if target_card_no in cards:
                               print("Enter how much money you want to transfer:")
                               amount = int(input())
                               if amount <= cards[prov_card_no][1]:
                                   do_transfer(prov_card_no, target_card_no, amount)
                               else:
                                   print()
                                   print("Not enough money!")
                           else:
                               print()
                               print("Such a card does not exist.")
                        else:
                            print()
                            print("Probably you made a mistake in the card number. Please try again!")
                    elif option2 == "4":
                        delete_account(prov_card_no)
                    elif option2 == "5":
                        print("You have successfully logged out!")
                        break
                    elif option2 == "0":
                        exxit()
                    
                    print_log_in_menu()
                    option2 = input()
            
            else:
                print("Wrong card number or PIN!")
            
        else:
            print("Wrong card number or PIN!")
          
    # wyjscie
    elif option1 == "0":
        exxit()
