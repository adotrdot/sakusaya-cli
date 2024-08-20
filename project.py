from consolemenu import ConsoleMenu, SelectionMenu
from consolemenu.items import FunctionItem
from consolemenu.prompt_utils import PromptUtils
from consolemenu.screen import Screen
from consolemenu.validators.regex import RegexValidator
import csv
import json
import sys


def main():
    # Try to open account.json, create a new one if it doesn't exist
    global account
    try:
        with open("account.json") as file:
            account = json.load(file)
    except FileNotFoundError:
        with open("account.json", "w") as file:
            account = {"total": 0, "income": 0, "expenses": 0, "saving": 0}
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

    # Deposit to saving
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
    menu = ConsoleMenu(
        title="=== SAKUSAYA ===",
        subtitle=get_history,
        exit_option_text="Back to main menu",
    )
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
        function=prompt.enter_to_continue,
        should_exit=True,
    )
    menu.append_item(item_reset)
    menu.show()

    # Refresh parent
    menu.previous_active_menu.draw()


def get_data():
    """
    Get the data of income.csv, expense.csv, and saving.csv
    and return it in a pretty table
    """
    return "Main Menu\n...\nContents of income, expense, saving.csv\n..."


def get_history():
    """
    Get the content of history.csv
    and return it in a pretty table
    """
    return "History\n...\nContents of history.csv\n..."


def input_data(parent: ConsoleMenu, type: str):
    """
    Input new data to either income.csv, expense.csv, or saving.csv

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
    Save new data to the corresponding csv file and make changes to account.json

    Arguments:
    money -- the amount of money
    type -- type of data, either income, expense, deposit, or withdraw
    category -- category of income/expense, None if type is either deposit or withdraw

    Raise:
    ValueError -- if type argument is not accepted
    """
    if not type in ["income", "expense", "deposit", "withdraw"]:
        raise ValueError
    
    # Filename will be saving.csv if type is either deposit or withdraw, but if type is income/expense then filename is income/expense.csv
    filename = "saving.csv" if category is None else f"{type}.csv"

    # Declare new data
    new_data = {"amount": money}
    if category is None:
        new_data["type"] = type.capitalize()
    else:
        new_data["category"] = category

    # Append new data
    with open(filename, "a", newline="") as file:
        fieldnames = ["amount", "type"] if category is None else ["amount", "category"]
        writer = csv.DictWriter(f=file, fieldnames=fieldnames)
        reader = csv.DictReader(file)

        # Add row
        if reader.line_num == 0:
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
            account["saving"] += money
            account["total"] -= money
        case "withdraw":
            account["saving"] -= money
            account["total"] += money

    with open("account.json", "w") as file:
        json.dump(account, file)


def input_money():
    """
    Ask user to input an amount of money, validate whether it's numeric, and return it
    """
    while True:
        money, valid = prompt.input(
            prompt="Amount: ", validators=RegexValidator(pattern=r"^[0-9]+$")
        )
        if valid:
            break
        else:
            prompt.println("You have to input a number!")

    return money


if __name__ == "__main__":
    main()
