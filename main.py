import datetime
import json

expenses = []

monthly_budget = {
    "Transportation": 10000,
    "Groceries": 30000,
    "Entertainment": 5000
}

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


# Saving deleted expenses in a file

def log_deleted_expenses(deleted_items):
    try:
        with open("deleted_expenses.json", mode="r") as file:
            deleted_log = json.load(file)
    except FileNotFoundError:
        deleted_log = []

    deleted_log.extend(deleted_items)

    with open("deleted_expenses.json", mode="w") as file:
        json.dump(deleted_log, file, indent=4)

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

    # Check against monthly budget
    budget = monthly_budget.get(category)
    if budget:
        spent = get_monthly_total(category)
        if spent > budget:
            print(
                f"⚠️ Warning: You have exceeded your monthyl budget for {category}!")
        elif spent > 0.9 * budget:
            print(
                f"🔔 Heads up! You're close to reaching your monthly budget for {category}")


# Delete Expenses

def delete_expense():
    if not expenses:
        print("No expenses to delete.")
        return

    while True:
        print("\nYour expenses:")
        for i, expense in enumerate(expenses):
            print(
                f"{i+1}. {expense['category']}: {expense['amount']} on {expense['date']}.")
        input_str = input(
            "Enter the numbers of the expenses to delete (comma-separated), or press Enter to cancel: ")
        if not input_str:
            print("No expenses deleted.")
            break

        try:
            indexes = [int(i.strip()) - 1 for i in input_str.split(",")]

            # Checking if indexes are valid
            if any(idx < 0 or idx >= len(expenses) for idx in indexes):
                print(
                    "One or more invalid numbers entered. No expenses were deleted. Please try again.")
                continue

            # Remove in reverse order to prevent index shift
            indexes = sorted(set(indexes), reverse=True)
            deleted_items = []

            for idx in indexes:
                deleted_items.append(expenses.pop(idx))

            log_deleted_expenses(deleted_items)

            save_expenses()

            print(f"Deleted the following expenses:")
            for item in deleted_items:
                print(
                    f"{item["category"]} - {item["amount"]} on {item["date"]}")
            break

        except ValueError:
            print('Input invalid. Please enter numbers separated by commas.')


# Helper function to calculate total spent this month in a category


def get_monthly_total(category):
    now = datetime.datetime.now()
    total = 0
    for expense in expenses:
        exp_date = datetime.datetime.strptime(
            expense["date"], "%Y-%m-%d %H:%M:%S")
        if (expense["category"].lower() == category.lower() and exp_date.year == now.year and exp_date.month == now.month):
            total += expense["amount"]
    return total


# Display expenses


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
        print("\n1. Add an Expense")
        print("2. Show Expenses")
        print("3. Delete an Expense")
        print("4. Exit")
        choice = int(input("Choose an option: "))

        if choice == 1:
            amount = float(input("Enter the amount: "))
            category = input("Enter the category: ")
            add_expense(amount, category)
        elif choice == 2:
            show_expenses()
        elif choice == 3:
            delete_expense()
        elif choice == 4:
            break
        else:
            print("Invalid choice, please try again.")


if __name__ == "__main__":
    main()
