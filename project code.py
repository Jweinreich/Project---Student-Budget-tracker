import json

def normalize_week_input(w):
    w = w.lower().replace("week", "").replace("wk", "").replace("w", "").strip()
    if w.isdigit():
        n = int(w)
        if 1 <= n <= 52:
            return n
    return None

def load_user(username):
    filename = f"{username}_budget.json"
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def save_user(data):
    filename = f"{data['name']}_budget.json"
    with open(filename, "w") as f:
        json.dump(data, f)
    print(f"--- Progress saved to {filename} ---")

def login():
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()

    data = load_user(username)

    if data is None:
        print("User not found. Creating new account.")
        pw2 = input("Re-enter password to confirm: ").strip()
        if pw2 != password:
            print("Passwords do not match. Restart program.")
            return None 

        return {
            "name": username,
            "password": password,
            "categories": [],
            "income": 0,
            "payRate": 1,
            "interval": "weekly",
            "savings": 0,
            "current_week": 1
        }

    if password != data["password"]:
        print("Incorrect password.")
        return None 

    return data

def choose_pay_rate(data):
    freq = ["daily", "weekly", "biweekly", "monthly", "yearly"]
    while True:
        x = input("How often do you get paid? (daily, weekly, biweekly, monthly, yearly): ").lower().strip()
        if x in freq:
            data["interval"] = x
            data["payRate"] = freq.index(x)
            return
        print("Invalid option.")

def ask_income(data):
    while True:
        try:
            amt = float(input(f"How much {data['interval']} income do you receive? "))
            data["income"] = amt
            return
        except ValueError:
            print("Enter a number.")

def setup_categories(data):
    if data["categories"]:
        return
    
    print("\nEnter your categories. Type 'done' when finished.")
    cats = []
    while True:
        c = input("Category name: ").strip()
        if c.lower() == "done":
            break
        if c:
# Fixed the box-shifting bug by forcing a character limit on category names
            clean_name = c[:9]
# Changed this to 53 so we don't get 'index out of range' errors when hitting week 52
            cats.append({"name": clean_name, "weeks": [0]*53})
    data["categories"] = cats

def enter_expenses_for_week(data, week):
    print(f"\n--- Entering Spending for Week {week} ---")
    for cat in data["categories"]:
        while True:
            try:
                current_val = cat["weeks"][week]
# Changed the prompt to show current value so you know what's already saved
                amt = input(f"How much did you spend on {cat['name']}? (Current: {current_val}): ")
                if amt == "": 
                    break
                cat["weeks"][week] = float(amt)
                break
            except ValueError:
                print("Enter a number.")

def convert_weekly_income(data):
    inc = data["income"]
    r = data["payRate"]
    if r == 0:  return inc * 7
    if r == 1:  return inc
    if r == 2:  return inc / 2
    if r == 3:  return inc / 4.33
    if r == 4:  return inc / 52
    return inc

def calculate_all_savings(data):
# Fixed the double-counting bug by calculating total savings from scratch across all weeks
    weekly_income = convert_weekly_income(data)
    total_spent = 0
    weeks_active = 0
    
    for w in range(1, 53):
        week_total = sum(cat["weeks"][w] for cat in data["categories"])
        if week_total > 0:
            total_spent += week_total
            weeks_active += 1
            
    return (weekly_income * weeks_active) - total_spent

def check_overspending(data):
    w = data["current_week"]
    total = sum(cat["weeks"][w] for cat in data["categories"])
    weekly_income = convert_weekly_income(data)
    remaining = weekly_income - total
    
    current_savings = calculate_all_savings(data)

    print(f"\n--- Week {w} Summary ---")
    print(f"Total spent this week: {total:.2f}")
    print(f"Weekly income: {weekly_income:.2f}")
    print(f"Remaining this week: {remaining:.2f}")
    print(f"Total Portfolio Savings: {current_savings:.2f}")

    if remaining > 0 and remaining >= weekly_income * 0.30:
        print(f"** Tip: You should consider investing {remaining/2:.2f}. **")

def display_block(data):
    w = data["current_week"]
    block_start = ((w-1)//4)*4 + 1
    weeks = [((block_start+i-1)%52)+1 for i in range(4)]
# Fixed the formatting here so the borders stay straight even with different category lengths
    print("\n+-----------+-----------+-----------+-----------+-----------+")
    print("| Category  |", end="")
    for wk in weeks:
        indicator = "*" if wk == w else " "
        print(f" Week {wk}{indicator:<2} |", end="")
    print("\n+-----------+-----------+-----------+-----------+-----------+")

    for cat in data["categories"]:
# Fixed the formatting here so the borders stay straight even with different category lengths
        print(f"| {cat['name']:<9} |", end="")
        for wk in weeks:
            val = cat["weeks"][wk]
            print(f" {val:<9.2f} |", end="")
        print("\n+-----------+-----------+-----------+-----------+-----------+")

def monthly_report(data):
    weeks_entered = [w for w in range(1, 53) if any(cat["weeks"][w] != 0 for cat in data["categories"])]
    if not weeks_entered:
        return

    total_spent_ever = sum(sum(cat["weeks"][w] for cat in data["categories"]) for w in weeks_entered)
    avg_weekly_exp = total_spent_ever / len(weeks_entered)
    
    weekly_income = convert_weekly_income(data)
    monthly_income = weekly_income * 4.33
    monthly_exp = avg_weekly_exp * 4.33

    print("\n=== Monthly Report (Projected) ===")
    print(f"Weekly Avg Expenses: {avg_weekly_exp:.2f}")
    print(f"Est. Monthly Income:   {monthly_income:.2f}")
    print(f"Est. Monthly Expenses: {monthly_exp:.2f}")
    print(f"Est. Monthly Balance:  {monthly_income - monthly_exp:.2f}")

def main():
    data = login()
    
    if data is None:
        return

    if data["income"] == 0:
        choose_pay_rate(data)
        ask_income(data)
    
    setup_categories(data)

# completely changed the main loop into a menu so it doesn't just run away from you
# I added the Income and payrate adjustment/ so it can better utilized
    while True:
        display_block(data)
        print(f"\n--- MENU (Week {data['current_week']}) ---")
        print("E: Enter Expenses | I: Edit income or payrate | N: Next Week | P: Prev Week | S: Save | X: Exit")
        choice = input("Select an option: ").lower().strip()

        if choice == 'e':
            enter_expenses_for_week(data, data["current_week"])
            check_overspending(data)
            monthly_report(data)
        elif choice == 'n':
# Changed how weeks cycle so you don't get stuck in 'week 5, 6, 7' forever
            data["current_week"] = (data["current_week"] % 52) + 1
        elif choice == 'p':
# Added a previous week option so you can go back and check your work
            data["current_week"] = (data["current_week"] - 2) % 52 + 1
        elif choice == 's':
            save_user(data)
# Ficed another bug that didnt allow for the user to change pay/rate
        elif choice == 'i':
            print(f"""\n--- Update Income
(Current: {data['income']}
{data['interval']})---""")
            choose_pay_rate(data)
            ask_income(data)
        elif choice == 'x':
            print("income profile updated!")
# Fixed the loop bug—added a proper break so the program actually closes when you want
            save_user(data)
            print("Budget closed. See you later.")
            break
        else:
# Fixed the 'random input' bug—it now ignores junk and asks you to try again
            print("!!! Invalid input. Please use E, I, N, P, S, or X. !!!")

if __name__ == "__main__":
    main()