import datetime
import json

expenses = []

# Read existing expenses from JSON file


def load_expenses():
    try:
        with open("expenses.json", mode="r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Save expenses to JSON file


def save_expenses():
    with open("expenses.json", mode="w") as file:
        json.dump(expenses, file, indent=4)

# Add expenses


def add_expense(amount, category):
    current_time = datetime.datetime.now()
    expense = {
        "amount": amount,
        "category": category,
        "date": current_time.strftime("%Y-%m-%d %H:%M:%S")
    }
    expenses.append(expense)
    save_expenses()
    print(
        f"Added expense: {amount} in category: {category} on {expense['date']}")


def show_expenses():
    if expenses:
        print("\nYour Expenses:")
        for expense in expenses:
            print(
                f'{expense["category"]}: {expense["amount"]} on {expense['date']}')
    else:
        print("No expenses to show.")


def main():
    global expenses
    expenses = load_expenses()
    while True:
        print("\n1. Add Expense")
        print("2. Show Expenses")
        print("3. Exit")
        choice = int(input("Choose an option: "))

        if choice == 1:
            amount = float(input("Enter the amount: "))
            category = input("Enter the category: ")
            add_expense(amount, category)
        elif choice == 2:
            show_expenses()
        elif choice == 3:
            break
        else:
            print("Invalid choice, please try again.")


if __name__ == "__main__":
    main()
