from consolemenu import ConsoleMenu, SelectionMenu, MultiSelectMenu
from consolemenu.items import FunctionItem, SubmenuItem
from consolemenu.prompt_utils import PromptUtils
from consolemenu.screen import Screen
from consolemenu.validators.regex import RegexValidator
from datetime import datetime
from tabulate import tabulate
import csv
import json
import sys


def main():
    # Try to open account.json, create a new one if it doesn't exist
    global account
    try:
        with open("account.json") as file:
            account = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        with open("account.json", "w") as file:
            account = new_account()
            json.dump(account, file)

    # Create and show Main Menu
    main_menu = build_menu()

    main_menu.show()


def build_menu():
    """
    Build menu using components from console-menu.
    The menu has 5 items, which are:
    1. Insert new data
    2. Deposit
    3. Withdraw
    4. View history
    5. Reset data
    """
    # Main Menu
    global prompt
    prompt = PromptUtils(screen=Screen())
    menu = ConsoleMenu(title="=== SAKUSAYA ===", subtitle=get_data)

    # Insert New Data Menu
    submenu_insert = FunctionItem(text="Insert new data", function=build_submenu_insert)

    # Deposit to savings
    item_deposit = FunctionItem(
        text="Deposit",
        function=input_data,
        kwargs={"parent": menu, "type": "deposit"}
    )
    item_withdraw = FunctionItem(
        text="Withdraw",
        function=input_data,
        kwargs={"parent": menu, "type": "withdraw"},
    )

    # View history
    submenu_history = FunctionItem(text="View history", function=build_submenu_history)

    # Reset data
    submenu_reset = FunctionItem(text="Reset data", function=build_submenu_reset)

    menu.append_item(submenu_insert)
    menu.append_item(item_deposit)
    menu.append_item(item_withdraw)
    menu.append_item(submenu_history)
    menu.append_item(submenu_reset)

    return menu


def build_submenu_insert():
    """
    Build menu for the item 'Insert new data'
    """
    menu = ConsoleMenu(
        title="=== SAKUSAYA ===",
        subtitle="Do you want to add a new income or expense data?",
        exit_option_text="Cancel",
    )
    item_income = FunctionItem(
        text="Income",
        function=input_data,
        kwargs={"parent": menu.previous_active_menu, "type": "income"},
        should_exit=True,
    )
    item_expense = FunctionItem(
        text="Expense",
        function=input_data,
        kwargs={"parent": menu.previous_active_menu, "type": "expense"},
        should_exit=True,
    )
    menu.append_item(item_income)
    menu.append_item(item_expense)
    menu.show()


def build_submenu_history():
    """
    Build menu for the item 'View history'
    """
    filter = set()

    def get_history_with_filter():
        """Get filtered content of history.csv"""
        return get_history(filter)
    
    def add_filter(f):
        filter.add(f)
        menu.draw()

    def reset_filter():
        filter.clear()
        menu.draw()

    menu = ConsoleMenu(
        title="=== SAKUSAYA ===",
        subtitle=get_history_with_filter,
        exit_option_text="Back to main menu",
    )

    # Filter
    menu_filter = MultiSelectMenu(title="=== SAKUSAYA ===", subtitle="Filter history by type\nEx.: 1,2,3 or 1-3 or 1-2,4", exit_option_text="Cancel")
    filter_income = FunctionItem(text="Income", function=add_filter, args=["Income"], should_exit=True)
    filter_expenses = FunctionItem(text="Expense", function=add_filter, args=["Expense"], should_exit=True)
    filter_deposit = FunctionItem(text="Deposit", function=add_filter, args=["Deposit"], should_exit=True)
    filter_withdraw = FunctionItem(text="Withdraw", function=add_filter, args=["Withdraw"], should_exit=True)
    menu_filter.append_item(filter_income)
    menu_filter.append_item(filter_expenses)
    menu_filter.append_item(filter_deposit)
    menu_filter.append_item(filter_withdraw)
    menu_filter_item = SubmenuItem(text="Filter history by type", submenu=menu_filter, menu=menu_filter)
    item_reset_filter = FunctionItem(text="Reset filter", function=reset_filter)

    menu.append_item(menu_filter_item)
    menu.append_item(item_reset_filter)
    menu.show()


def build_submenu_reset():
    """
    Build menu for the item 'Reset data'
    """
    menu = ConsoleMenu(
        title="=== SAKUSAYA ===",
        subtitle="Do you really want to RESET ALL DATA?",
        exit_option_text="No",
    )
    item_reset = FunctionItem(
        text="Yes",
        function=reset_data,
        kwargs={"parent": menu.previous_active_menu},
        should_exit=True,
    )
    menu.append_item(item_reset)
    menu.show()


def get_data():
    """
    Get the data of total money, income, expense, and savings from account
    and return it in a pretty table
    """
    header = ["Total", account['total']]
    data = [
        ["Savings", account['savings']],
        ["Income", account['income']],
        ["Expenses", account['expenses']]
    ]

    table = tabulate(tabular_data=data, headers=header, tablefmt="fancy_outline")

    return table


def get_history(filter: set = {}):
    """
    Get the content of history.csv and return it in a pretty table.
    Returns 'No records.' if content is empty.

    Arguments:
    filter -- List of filters to apply. Options are 'Income', 'Expense', 'Deposit', and 'Withdraw'.
    """
    try:
        with open("history.csv", newline="") as file:
            reader = csv.DictReader(file)
            if len(filter) > 0:
                data = [row for row in reader if row["Type"] in filter]
            else:
                data = [row for row in reader]

            if len(data) == 0:
                return "No records"
            
            # Reverse data so that the latest timestamp is on top
            data.reverse()

            return tabulate(tabular_data=data, headers="keys", tablefmt="fancy_outline")
    except FileNotFoundError:
        return "No records"


def input_data(parent: ConsoleMenu, type: str):
    """
    Input new data to either income.csv, expense.csv, or savings.csv

    Arguments:
    type -- type of data, either income, expense, deposit, or withdraw

    Raise:
    ValueError -- if type argument is not accepted
    """
    if not type in ["income", "expense", "deposit", "withdraw"]:
        raise ValueError

    # Get category if type is either income or expense
    category = None
    if type in ["income", "expense"]:
        data = []
        try:
            with open("categories.json") as file:
                data = json.load(file)[type]
        except FileNotFoundError:
            sys.exit("Could not open categories.json")

        # Get selection of categories
        selected = SelectionMenu.get_selection(
            strings=data, title="=== SAKUSAYA ===", subtitle="Choose income category:"
        )
        category = data[selected]
        print(f"You have selected '{category}'")

    # Ask user to input the amount of money
    money = input_money()
    if not prompt.confirm_answer(money):
        return

    # Save data
    save_data(int(money), type, category)

    # Refresh parent
    parent.draw()


def save_data(money: int, type: str, category=None):
    """
    Save new data to the history.csv file and make changes to account.json

    Arguments:
    money -- the amount of money
    type -- type of data, either income, expense, deposit, or withdraw
    category -- category of income/expense, None if type is either deposit or withdraw

    Raise:
    ValueError -- if type argument is not accepted
    """
    if not type in ["income", "expense", "deposit", "withdraw"]:
        raise ValueError

    # Declare new data
    new_data = {"Amount": money}
    new_data["Type"] = type.capitalize()
    new_data["Category"] = "-" if category is None else category
    new_data["Timestamp"] = datetime.now().strftime("%y-%m-%d %H:%M") # Get and format current time

    # Append new data history.csv
    with open("history.csv", "a", newline="") as file:
        fieldnames = ["Amount", "Type", "Category", "Timestamp"]
        writer = csv.DictWriter(f=file, fieldnames=fieldnames)
        reader = csv.DictReader(file)

        # Add row
        if file.tell() == 0:
            writer.writeheader()
        writer.writerow(new_data)

    # Make necessary changes to account.json
    match type:
        case "income":
            account["income"] += money
            account["total"] += money
        case "expense":
            account["expenses"] += money
            account["total"] -= money
        case "deposit":
            account["savings"] += money
            account["total"] -= money
        case "withdraw":
            account["savings"] -= money
            account["total"] += money

    with open("account.json", "w") as file:
        json.dump(account, file)


def reset_data(parent: ConsoleMenu):
    """
    Reset data, remove the contents of history.csv and reset account
    """
    # Remove contents of history.csv
    with open("history.csv", "w", newline="") as file:
        file.write("")

    # Reset account
    global account
    account = new_account()

    # Replace account.json with the new reset account
    with open("account.json", "w", newline="") as file:
        json.dump(account, file)

    # Refresh parent
    parent.draw()


def input_money():
    """
    Ask user to input an amount of money, validate whether it's numeric, and return it
    """
    while True:
        money = input("Amount: ")
        if validate_money(money):
            break
        else:
            prompt.println("You have to input a whole number!")

    return money


def validate_money(money):
    """
    Validate if the given is actually valid.

    Arguments:
    money -- the amount of money that will be validated
    """

    return prompt.validate_input(input_string=money, validators=RegexValidator(pattern=r"^[0-9]+$"))


def new_account():
    """
    Return a new dictionary of an account that consists of total amount of money,
    income, expenses, and saving with values set to 0.
    """
    return {"total": 0, "income": 0, "expenses": 0, "savings": 0}


if __name__ == "__main__":
    main()
