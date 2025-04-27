import datetime
import json
import difflib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from collections import defaultdict
import seaborn as sns
import pandas as pd
import calendar
import numpy as np
import csv


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


# Reading the categories of expenses
def load_category_budgets():
    try:
        with open("category_budgets.json", mode="r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {
            "Transportation": 10000,
            "Groceries": 30000,
            "Entertainment": 5000
        }


# Saving category budgets
def save_category_budgets():
    with open("category_budgets.json", mode="w") as file:
        json.dump(monthly_budget, file, indent=4)


# Add expenses
def add_expense(amount, category):
    category = validate_or_suggest_category(category)
    if not category:
        print("Expense not added.")
        return

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


# Edit expenses
def edit_expense():
    if not expenses:
        print('No expenses to edit.')
        return

    choice = ""

    while True:
        print('\n✏️ Your expenses:')
        for i, expense in enumerate(expenses):
            print(
                f'{i+1}.{expense["category"]}: ¥{expense["amount"]} on {expense["date"]}')

        try:
            choice = input("Enter the number of expense to edit: ").strip()
            if not choice:
                print("Edit cancelled.")
                return

            idx = int(choice) - 1
            if idx < 0 or idx >= len(expenses):
                print("Invalid number. Try again.")
                continue

            expense = expenses[idx]

            print('\nWhat would you like to edit?')
            print('1. Amount')
            print('2. Category')
            print('3. Date')
            print('0. Cancel')

            field_choice = input("Choose an option: ").strip()

            if field_choice == "1":
                while True:
                    try:
                        new_amount = float(input("Enter new amount: ").strip())
                        if new_amount < 0:
                            print("Amount cannot be negative.")
                            continue
                        expense["amount"] = new_amount
                        break
                    except ValueError:
                        print("Please enter a valid number.")

            elif field_choice == "2":
                new_category = input("Enter new category: ").strip()
                validated_category = validate_or_suggest_category(new_category)
                if validated_category:
                    expense["category"] = validated_category
                else:
                    print("Category change cancelled.")
                    return

            elif field_choice == "3":
                while True:
                    new_date_str = input(
                        "Enter new date (YYYY-MM-DD HH:MM:SS): ").strip()
                    try:
                        new_date = datetime.datetime.strptime(
                            new_date_str, "%Y-%m-%d %H:%M:%S")
                        expense["date"] = new_date.strftime(
                            "%Y-%m-%d %H:%M:%S")
                        break
                    except ValueError:
                        print("Invalid format. Please use YYYY-MM-DD HH:MM:SS")

            elif field_choice == "0":
                print("Edit cancelled.")
                return
            else:
                print("Invalid choice. Try again.")
                continue

            save_expenses()
            print("✅ Expense updated successfully.")
            return

        except ValueError:
            print("Invalid input. Please enter a valid number.")


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


# Display monthly summary
def show_monthly_summary():
    print("\n📊 Monthly Budget Summary: ")
    print("*"*50)
    now = datetime.datetime.now()
    categories = set([expense["category"]
                     for expense in expenses] + list(monthly_budget.keys()))

    for category in sorted(categories):
        spent = get_monthly_total(category)
        budget = monthly_budget.get(category, 0)
        remaining = budget - spent

        if budget == 0:
            status = "❓ No budget set"
        elif spent > budget:
            status = "‼️ Over budget"
        elif spent > 0.9 * budget:
            status = "⚠️ Near limit"
        else:
            status = "✅ Under budget"

        print(f"Category  :  {category}")
        print(f"Budget    :  ¥{budget}")
        print(f"Spent     :  ¥{spent}")
        print(f"Remaining :  ¥{remaining}")
        print(f"Status    :  {status}")
        print("*"*50)


# Filter while viewing
def filter_expenses_by_date():
    while True:
        print("\n📅 Filter Expenses by Date")
        print("1. This Week")
        print("2. This month")
        print("3. Custom Date Range")
        print('0. Cancel')

        choice = input("Choose an option: ").strip()

        now = datetime.datetime.now()
        filtered = []
        lable = ""

        if choice == "1":
            # Start of week: last Sunday at 00:00:00
            start_of_week = datetime.datetime.combine(
                (now - datetime.timedelta(days=now.weekday() + 1)).date(),
                datetime.time.min
            )

            # End of week: next Saturday at 23:59:59
            days_to_saturday = 5 - now.weekday() if now.weekday() <= 5 else 6
            end_of_week = datetime.datetime.combine(
                (now + datetime.timedelta(days=days_to_saturday)).date(),
                datetime.time.max
            )

            filtered = [
                e for e in expenses
                if start_of_week <= datetime.datetime.strptime(e["date"], "%Y-%m-%d %H:%M:%S") <= end_of_week
            ]
            label = f"This Week ({start_of_week.date()} to {end_of_week.date()})"
            break

        elif choice == "2":
            start_of_month = now.replace(day=1)
            filtered = [e for e in expenses if datetime.datetime.strptime(
                e["date"], "%Y-%m-%d %H:%M:%S") >= start_of_month]
            label = "This Month"
            break

        elif choice == "3":
            while True:
                try:
                    start_str = input(
                        "Enter start date (YYYY-MM-DD): ").strip()
                    end_str = input("Enter end date (YYYY-MM-DD): ").strip()

                    start_date = datetime.datetime.strptime(
                        start_str, "%Y-%m-%d")
                    end_date = datetime.datetime.strptime(
                        end_str, "%Y-%m-%d") + datetime.timedelta(days=1)
                    # end date also included

                    if end_date < start_date:
                        print(
                            "❗️End date cannot be earlier than start date. Please try again.")
                        continue

                    filtered = [
                        e for e in expenses
                        if start_date <= datetime.datetime.strptime(e["date"], "%Y-%m-%d %H:%M:%S") < end_date
                    ]
                    label = f"From {start_date.date()} to {(end_date - datetime.timedelta(days=1)).date()}"
                    break
                except ValueError:
                    print('Invalid date format. Please use YYYY-MM-DD format.')
                    continue
            break

        elif choice == "0":
            return
        else:
            print('Invalid choice. Please enter again.')
            continue

    print(f"\n📂 Expenses - {label}")
    if not filtered:
        print('No expenses found in this range.')
    else:
        for e in filtered:
            print(f'{e["category"]}: ¥{e["amount"]} on {e["date"]}')


# Category wise breakdown (viewing)
def show_category_breakdown():
    if not expenses:
        print("No expenses to analyze.")
        return

    totals = defaultdict(float)
    for exp in expenses:
        totals[exp["category"]] += exp["amount"]

    categories = list(totals.keys())
    amounts = list(totals.values())

    plt.figure(figsize=(10, 6))
    plt.bar(categories, amounts, color='skyblue')
    plt.title("💸 Total Spent per Category")
    plt.xlabel("Category")
    plt.ylabel("Amount (¥)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()


# Time based trend (viewing)
def show_time_based_trend():
    if not expenses:
        print("No expenses to analyze.")
        return

    print("\n📆 Choose an option:")
    print("1. Daily")
    print("2. Weekly")
    print("3. Monthly")
    granularity = input("Enter your choice: ").strip()

    totals = defaultdict(float)

    for exp in expenses:
        date = datetime.datetime.strptime(exp["date"], "%Y-%m-%d %H:%M:%S")

        if granularity == "1":
            key = date.strftime("%Y-%m-%d")
        elif granularity == "2":
            # Year-Week
            key = f"{date.isocalendar()[0]}-W{date.isocalendar()[1]}"
        elif granularity == "3":
            key = date.strftime("%Y-%m")
        else:
            print("Invalid choice.")
            return

        totals[key] += exp["amount"]

    if not totals:
        print("No data to display.")
        return

    # Sort by date
    sorted_items = sorted(totals.items())
    keys = [item[0] for item in sorted_items]
    values = [item[1] for item in sorted_items]

    plt.figure(figsize=(10, 6))
    plt.plot(keys, values, marker='o', linestyle='-', color='purple')
    plt.title("📈 Spending Trend Over Time")
    plt.xlabel("Time")
    plt.ylabel("Total Spent (¥)")
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()


# Draw calender
def draw_calendar(ax, year, month, fig, colorbar_container):
    ax.clear()
    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdayscalendar(year, month)

    daily_spending = defaultdict(float)
    daily_details = defaultdict(list)

    for exp in expenses:
        date = datetime.datetime.strptime(exp["date"], "%Y-%m-%d %H:%M:%S")
        if date.year == year and date.month == month:
            daily_spending[date.day] += exp["amount"]
            daily_details[date.day].append((exp["category"], exp["amount"]))

    max_spending = max(daily_spending.values(), default=1)
    cmap = plt.cm.YlOrRd
    norm = plt.Normalize(vmin=0, vmax=max_spending)

    ax.set_xlim(0, 7)
    ax.set_ylim(0, len(month_days))
    ax.set_xticks(range(7))
    ax.set_xticklabels(['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'])
    ax.set_yticks([])
    ax.set_title(
        f"Calendar View - {calendar.month_name[month]} {year}", fontsize=16)

    rect_info = {}

    for week_idx, week in enumerate(month_days):
        for day_idx, day in enumerate(week):
            if day == 0:
                continue
            spending = daily_spending.get(day, 0)
            color = cmap(norm(spending)) if spending > 0 else "white"

            x, y = day_idx, len(month_days) - 1 - week_idx
            rect = patches.Rectangle(
                (x, y), 1, 1, facecolor=color, edgecolor='gray')
            ax.add_patch(rect)
            ax.text(x + 0.5, y + 0.7, str(day), ha='center',
                    va='center', fontsize=10, weight='bold')

            if spending > 0:
                ax.text(x + 0.5, y + 0.3, f"¥{spending:.2f}",
                        ha='center', va='center', fontsize=8, color='black')

            rect_info[(x, y)] = (day, daily_details.get(day, []))

    # Remove previous colorbar if it exists
    if colorbar_container["cbar"]:
        colorbar_container["cbar"].remove()
        colorbar_container["cbar"] = None

    # Add new colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    colorbar_container["cbar"] = fig.colorbar(
        sm, ax=ax, orientation='vertical', fraction=0.03, pad=0.04)
    colorbar_container["cbar"].set_label('Spending (¥)', fontsize=10)

    # Tooltip
    annot = ax.annotate("", xy=(0, 0), xytext=(10, 10), textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w"),
                        arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)

    def on_hover(event):
        if event.inaxes == ax:
            for (x, y), (day, details) in rect_info.items():
                if x <= event.xdata < x + 1 and y <= event.ydata < y + 1:
                    if details:
                        text = f"{calendar.month_name[month]} {day}:\n"
                        for cat, amt in details:
                            text += f"  {cat}: ¥{amt:.2f}\n"
                        annot.xy = (event.xdata, event.ydata)
                        annot.set_text(text.strip())
                        annot.set_visible(True)
                        fig.canvas.draw_idle()
                        return
        annot.set_visible(False)
        fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", on_hover)


# Calender view of expenses
def show_calendar_view():
    now = datetime.datetime.now()
    current_year = now.year
    current_month = now.month

    fig, ax = plt.subplots(figsize=(10, 6))
    # Track the colorbar so we can remove it
    colorbar_container = {"cbar": None}

    draw_calendar(ax, current_year, current_month, fig, colorbar_container)

    def on_key(event):
        nonlocal current_year, current_month
        if event.key == "right":
            if current_month == 12:
                current_month = 1
                current_year += 1
            else:
                current_month += 1
        elif event.key == "left":
            if current_month == 1:
                current_month = 12
                current_year -= 1
            else:
                current_month -= 1
        draw_calendar(ax, current_year, current_month, fig, colorbar_container)

    fig.canvas.mpl_connect("key_press_event", on_key)
    plt.show()


# Analytics menu
def analytics_menu():
    while True:
        print("\n📊 Analytics Menu")
        print("1. 📈 Category-wise Expense Breakdown")
        print("2. 🕒 Time-Based Spending Trend")
        print("3. 📅 Calendar View of Daily Spending")
        print("0. 🔙 Back to Main Menu")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            show_category_breakdown()
        elif choice == "2":
            show_time_based_trend()
        elif choice == "3":
            show_calendar_view()
        elif choice == "0":
            return
        else:
            print("Invalid option. Please try again.")


# Export to CSV
def export_expenses_to_csv(filename="expenses_export.csv"):
    if not expenses:
        print("No expenses to export.")
        return

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["date", "amount", "category"])  # Header row
        for expense in expenses:
            writer.writerow(
                [expense["date"], expense["amount"], expense["category"]])

    print(f"Expenses exported to {filename}")


# Import from CSV
def import_expenses_from_csv(filename):
    try:
        with open(filename, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            imported_expenses = []
            for row in reader:
                imported_expenses.append({
                    'date': row['date'],
                    'amount': float(row['amount']),
                    'category': row['category']
                })
            print(f"Expenses imported from {filename}")
            return imported_expenses
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        return []


# Category Suggestion
def validate_or_suggest_category(input_category):
    known_categories = list(monthly_budget.keys()) + \
        [e["category"] for e in expenses]
    known_categories = list(set(known_categories))

    close_matches = difflib.get_close_matches(
        input_category, known_categories, n=1, cutoff=0.7)

    if close_matches:
        suggested = close_matches[0]
        confirm = input(f'Did you mean "{suggested}"? (Y/N): ').strip().lower()
        if confirm == "y":
            return suggested
        else:
            confirm_new = input(
                f'"{input_category}" is not recognised. Do you want to add it as a new category? (Y/N): ').strip().lower()
            if confirm_new == 'y':
                budget = prompt_for_budget(input_category)
                monthly_budget[input_category] = budget
                return input_category
            else:
                print("Category not accepted.")
                return None
    else:
        confirm_new = input(
            f'"{input_category}" is not recognised. Do you want to add it as a new category? (Y/N): ').strip().lower()
        if confirm_new == 'y':
            budget = prompt_for_budget(input_category)
            monthly_budget[input_category] = budget
            return input_category
        else:
            print("Category not accepted.")
            return None


# Setting budget for new categories
def prompt_for_budget(category):
    while True:
        try:
            budget_amount = float(
                input(f'Set a monthly budget for "{category}": '))
            if budget_amount < 0:
                print("Budget cannot be negative. Try again.")
                continue
            return budget_amount
        except ValueError:
            print("Invalid budget amount. Try again.")


def main():
    global expenses
    expenses = load_expenses()
    while True:
        print("\n1. Add an Expense")
        print("2. Show Expenses")
        print("3. Filter Expenses by Date")
        print("4. Monthly Summary Report")
        print("5. Analytics and Visualisation")
        print("6. Export / Import (CSV)")
        print("7. Edit an Expense")
        print("8. Delete an Expense")
        print("0. Exit")
        try:
            choice = input("Choose an option: ")
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue

        if choice == "1":
            amount = float(input("Enter the amount: "))
            category = input("Enter the category: ")
            add_expense(amount, category)
        elif choice == "2":
            show_expenses()
        elif choice == "3":
            filter_expenses_by_date()
        elif choice == "4":
            show_monthly_summary()
        elif choice == "5":
            analytics_menu()

        elif choice == "6":
            print("1. Export")
            print("2. Import")
            try:
                choice = input("Choose an option: ")
            except ValueError:
                print("Invalid input. Please enter a number.")
                continue
            if choice == "1":
                filename = input(
                    "Enter filename to export (default: expenses_export.csv): ").strip()
                export_expenses_to_csv(filename or "expenses_export.csv")
            elif choice == "2":
                filename = input(
                    "Enter filename to import (default: expenses_import.csv): ").strip()
                expenses += import_expenses_from_csv(
                    filename or "expenses_export.csv")
                save_expenses()

        elif choice == "7":
            edit_expense()
        elif choice == "8":
            delete_expense()
        elif choice == "0":
            break
        else:
            print("Invalid choice, please try again.")


expenses = []
monthly_budget = load_category_budgets()


if __name__ == "__main__":
    main()
