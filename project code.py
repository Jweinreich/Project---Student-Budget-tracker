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

def login():
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()

    data = load_user(username)

    if data is None:
        print("User not found. Creating new account.")
        pw2 = input("Re-enter password to confirm: ").strip()
        if pw2 != password:
            print("Passwords do not match. Restart program.")
            exit()

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
        exit()

    return data

def choose_pay_rate(data):
    freq = ["daily", "weekly", "biweekly", "monthly", "yearly"]
    while True:
        x = input("How often do you get paid? ").lower().strip()
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
        except:
            print("Enter a number.")

def setup_categories(data):
    print("\nEnter your categories. Type 'done' when finished.")
    cats = []
    while True:
        c = input("Category name: ").strip()
        if c.lower() == "done":
            break
        if c:
            cats.append({"name": c, "weeks": [0]*53})
    data["categories"] = cats

def enter_expenses_for_week(data, week):
    for cat in data["categories"]:
        while True:
            try:
                amt = float(input(f"How much did you spend on {cat['name']}? "))
                cat["weeks"][week] = amt
                break
            except:
                print("Enter a number.")

def convert_weekly_income(data):
    inc = data["income"]
    r = data["payRate"]
    if r == 0:  return inc * 7
    if r == 1:  return inc
    if r == 2:  return inc / 2
    if r == 3:  return inc / 4
    if r == 4:  return inc / 52
    return inc

def check_overspending(data):
    w = data["current_week"]
    total = sum(cat["weeks"][w] for cat in data["categories"])
    weekly_income = convert_weekly_income(data)
    remaining = weekly_income - total
    data["savings"] += remaining

    print(f"\nTotal spent: {total}")
    print(f"Weekly income: {weekly_income}")
    print(f"Remaining: {remaining}")
    print(f"Savings: {data['savings']}")

    if remaining > 0 and remaining >= weekly_income * 0.30:
        print(f"You should consider investing {remaining/2:.2f}.")

def display_block(data):
    w = data["current_week"]
    block_start = ((w-1)//4)*4 + 1
    weeks = [((block_start+i-1)%52)+1 for i in range(4)]

    print("\n+-----------+-----------+-----------+-----------+-----------+")
    print("| Category  |", end="")
    for wk in weeks:
        print(f" Week {wk:<3} |", end="")
    print("\n+-----------+-----------+-----------+-----------+-----------+")

    for cat in data["categories"]:
        print(f"| {cat['name']:<9}|", end="")
        for wk in weeks:
            val = cat["weeks"][wk]
            print(f" {val:<9}|", end="")
        print("\n+-----------+-----------+-----------+-----------+-----------+")

def monthly_report(data):
    weeks_entered = [w for w in range(1,53) if any(cat["weeks"][w] != 0 for cat in data["categories"])]
    if not weeks_entered:
        print("No data yet.")
        return

    avg_weekly_exp = sum(sum(cat["weeks"][w] for cat in data["categories"]) for w in weeks_entered) / len(weeks_entered)
    weekly_income = convert_weekly_income(data)
    monthly_income = weekly_income * 4.33
    monthly_exp = avg_weekly_exp * 4.33

    print("\n=== Monthly Report ===")
    print(f"Weekly income: {weekly_income}")
    print(f"Weekly avg expenses: {avg_weekly_exp}")
    print(f"Monthly income: {monthly_income}")
    print(f"Monthly expenses: {monthly_exp}")
    print(f"Monthly balance: {monthly_income - monthly_exp}")

def main():
    data = login()

    choose_pay_rate(data)
    ask_income(data)
    setup_categories(data)

    print("\nEnter spending for Week 1:")
    enter_expenses_for_week(data, 1)
    check_overspending(data)

    while True:
        print("\nSave progress? (y/n)")
        s = input("> ").lower().strip()
        if s == "y":
            save_user(data)
            print("Progress saved.")

        data["current_week"] += 1
        if data["current_week"] > 52:
            data["current_week"] = 1

        print(f"\nEntering Week {data['current_week']}")
        enter_expenses_for_week(data, data["current_week"])
        check_overspending(data)
        display_block(data)
        monthly_report(data)

main()