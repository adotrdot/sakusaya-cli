from consolemenu import ConsoleMenu, SelectionMenu, MultiSelectMenu
from consolemenu.items import FunctionItem, SubmenuItem
from consolemenu.prompt_utils import PromptUtils
from consolemenu.screen import Screen
from datetime import datetime
from tabulate import tabulate
import csv
import json
import re
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
        text="Deposit", function=input_data, kwargs={"parent": menu, "type": "deposit"}
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
        return get_history(filter=filter)

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
    menu_filter = MultiSelectMenu(
        title="=== SAKUSAYA ===",
        subtitle="Filter history by type\nEx.: 1,2,3 or 1-3 or 1-2,4",
        exit_option_text="Cancel",
    )
    filter_income = FunctionItem(
        text="Income", function=add_filter, args=["Income"], should_exit=True
    )
    filter_expenses = FunctionItem(
        text="Expense", function=add_filter, args=["Expense"], should_exit=True
    )
    filter_deposit = FunctionItem(
        text="Deposit", function=add_filter, args=["Deposit"], should_exit=True
    )
    filter_withdraw = FunctionItem(
        text="Withdraw", function=add_filter, args=["Withdraw"], should_exit=True
    )
    menu_filter.append_item(filter_income)
    menu_filter.append_item(filter_expenses)
    menu_filter.append_item(filter_deposit)
    menu_filter.append_item(filter_withdraw)
    menu_filter_item = SubmenuItem(
        text="Filter history by type", submenu=menu_filter, menu=menu_filter
    )
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

    Returns:
        table (str): A table consisting of total money, income, expense, and savings generated using tabulate
    """
    header = ["Total", format_money(account["total"])]
    data = [
        ["Savings", format_money(account["savings"])],
        ["Income", format_money(account["income"])],
        ["Expenses", format_money(account["expenses"])],
    ]

    table = tabulate(tabular_data=data, headers=header, tablefmt="fancy_outline")

    return table


def get_history(history_file: str = "history.csv", filter: set = {}):
    """
    Get the content of history.csv and return it in a pretty table.
    Returns 'No records.' if content is empty.

    Arguments:
        history_file (str): Filename of the history csv file
        filter (set): List of filters to apply. Options are 'Income', 'Expense', 'Deposit', and 'Withdraw'.

    Returns:
        table (str): A table containing the contents of history.csv generated using tabulate. However, if there are no contents, return 'No records'
    """
    try:
        with open(history_file, newline="") as file:
            reader = csv.DictReader(file)
            data = []
            nfilter = len(filter)
            for row in reader:
                # Skip if filter is not empty and data type is not in filter
                if nfilter > 0 and not row["Type"] in filter:
                    continue

                # Format money in USD currency
                row["Amount"] = format_money(float(row["Amount"]))

                # Append row to data
                data.append(row)

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
        parent (ConsoleMenu): this function will make changes to values displayed in parent's menu, hence parent needs to be given to redraw it
        type (str): type of data, either income, expense, deposit, or withdraw

    Raises:
        ValueError: if type argument is not accepted
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
        
        # If user selected exit (the last option), return
        if selected == len(data):
            return
        
        category = data[selected]
        prompt.println(f"You have selected '{category}'")

    # Ask user to input the amount of money
    subtitle = f"You have chosen {type.capitalize()}"
    if category != None:
        subtitle += f" with the category {category}"
    money, money_usd = input_money(subtitle=subtitle)
    if not prompt.confirm_answer(money_usd):
        return

    # Save data
    save_data(money, type, category)

    # Refresh parent
    parent.draw()


def save_data(money: float, type: str, category=None):
    """
    Save new data to the history.csv file and make changes to account.json

    Arguments:
        money (float): the amount of money
        type (str): type of data, either income, expense, deposit, or withdraw
        category (str, optional): category of income/expense, None if type is either deposit or withdraw

    Raises:
        ValueError: if type argument is not accepted
    """
    if not type in ["income", "expense", "deposit", "withdraw"]:
        raise ValueError

    # Declare new data
    new_data = {"Amount": money}
    new_data["Type"] = type.capitalize()
    new_data["Category"] = "-" if category is None else category
    new_data["Timestamp"] = datetime.now().strftime(
        "%y-%m-%d %H:%M"
    )  # Get and format current time

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


def input_money(subtitle: str = "", prompt_text: str = "Amount: $ "):
    """
    Ask user to input an amount of money, validate whether it's numeric, and return it

    Arguments:
        subtitle (str, optional): a help text to show above the prompt
        prompt (str): provide custom text for prompt, default is 'Amount: $ '

    Returns:
        money (str): the amount of money that has been validated
        (tuple): a tuple consisting of an float of the amount of money and a string of the money in USD format
    """
    while True:
        if subtitle:
            prompt.println(subtitle)
        prompt.println(
            "Example input are:\n- 123456\n- 123,456\n- 123,456.0\n- 123,456.00"
        )
        money = input(prompt_text)
        if validate_money(money):
            break
        else:
            prompt.println("You have to input a whole number!")

    # Convert money to float, removing all occurences of comma
    money_f = float(money.replace(",", ""))

    # Format money back to string, formatted in USD currency
    money_usd = format_money(money_f)

    return (money_f, money_usd)


def validate_money(money: str):
    """
    Validate if the given money is actually valid.

    Arguments:
        money (str): the amount of money that will be validated

    Returns:
        (bool): whether the money was valid or not
    """

    return True if re.match(pattern=r"^(0|[1-9][0-9]{0,2})(,*\d{3})*(\.\d{1,2})?$", string=money) else False


def format_money(money: float):
    """
    Format money from float to string in USD currency format

    Arguments:
        money (float): the amount of money

    Returns:
        money_usd (str): the amount of money, as a string, in USD currency format
    """

    return f"$ {money:,.2f}"


def new_account():
    """
    Return a new dictionary of an account that consists of total amount of money,
    income, expenses, and saving with values set to 0.

    Returns:
        (dict): A dictionary consisting of total money, income, expenses, and savings with the default value of 0
    """
    return {"total": 0, "income": 0, "expenses": 0, "savings": 0}


if __name__ == "__main__":
    main()
