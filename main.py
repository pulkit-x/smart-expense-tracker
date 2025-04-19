expenses = []

def add_expense(amount, category):
    expense = {"amount": amount, "category": category}
    expenses.append(expense)
    print(f'Added expense: {amount} in category: {category}')

def show_expenses():
    for expense in expenses:
        print(f'{expense["category"]}: {expense["amount"]}')

def main():
    add_expense(2000, "Groceries")
    add_expense(220, "Transportation")

    print('\nAll Expenses:')
    show_expenses()

if __name__ == "__main__":
    main()
