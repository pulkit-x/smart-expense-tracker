expenses = []


def add_expense(amount, category):
    expense = {"amount": amount, "category": category}
    expenses.append(expense)
    print(f'Added expense: {amount} in category: {category}')


def show_expenses():
    print('\nYour Expenses:')
    for expense in expenses:
        print(f'{expense["category"]}: {expense["amount"]}')


def main():
    while True:
        print("1. Add Expense")
        print("2. Show Expenses")
        print("3. Exit")
        choice = int(input("Enter the category: "))

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
