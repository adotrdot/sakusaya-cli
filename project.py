from consolemenu import ConsoleMenu, SelectionMenu
from consolemenu.items import FunctionItem, SubmenuItem, CommandItem
from consolemenu.screen import Screen


def main():
    # Create Main Menu
    main_menu = build_menu()

    main_menu.show()


def build_menu():
    # Main Menu
    menu = ConsoleMenu(title="=== SAKUSAYA ===", subtitle=get_data)

    # Insert New Data Menu
    submenu_insert = FunctionItem(
        text="Insert new data", function=build_submenu_insert, kwargs={"parent": menu}
    )

    # Deposit to saving
    item_deposit = FunctionItem(
        text="Deposit", function=input_deposit, kwargs={"parent": menu}
    )
    item_withdraw = FunctionItem(
        text="Withdraw", function=input_withdraw, kwargs={"parent": menu}
    )

    # View history
    submenu_history = FunctionItem(text="View history", function=build_submenu_history)

    # Reset data
    submenu_reset = FunctionItem(
        text="Reset data", function=build_submenu_reset, kwargs={"parent": menu}
    )

    menu.append_item(submenu_insert)
    menu.append_item(item_deposit)
    menu.append_item(item_withdraw)
    menu.append_item(submenu_history)
    menu.append_item(submenu_reset)

    return menu


def build_submenu_insert(parent):
    menu = ConsoleMenu(
        title="=== SAKUSAYA ===",
        subtitle="Do you want to add a new income or expense data?",
        exit_option_text="Cancel",
    )
    item_income = FunctionItem(
        text="Income", function=input, args=["Amount: "], should_exit=True
    )
    item_expense = FunctionItem(
        text="Expense", function=input, args=["Amount: "], should_exit=True
    )
    menu.append_item(item_income)
    menu.append_item(item_expense)
    menu.show()

    # Refresh parent
    parent.draw()


def build_submenu_history():
    menu = ConsoleMenu(
        title="=== SAKUSAYA ===",
        subtitle=get_history,
        exit_option_text="Back to main menu",
    )
    menu.show()


def build_submenu_reset(parent):
    menu = ConsoleMenu(
        title="=== SAKUSAYA ===",
        subtitle="Do you really want to RESET ALL DATA?",
        exit_option_text="No",
    )
    item_reset = FunctionItem(
        text="Yes",
        function=input,
        args=["Press Enter to continue..."],
        should_exit=True,
    )
    menu.append_item(item_reset)
    menu.show()

    # Refresh parent
    parent.draw()


def get_data():
    return "Main Menu\n...\nContents of income, expense, saving.csv\n..."


def get_history():
    return "History\n...\nContents of history.csv\n..."


def input_deposit(parent):
    _ = input_money()

    # Refresh parent
    parent.draw()


def input_withdraw(parent):
    _ = input_money()

    # Refresh parent
    parent.draw()


def input_money():
    return input("Amount: ")


if __name__ == "__main__":
    main()
