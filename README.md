# SAKUSAYA-CLI
#### Video Demo: https://youtu.be/kpdnR3ScgeI
#### Description:
***sakusaya-cli*** is a software with a simple CLI interface to manage your income, expenses, and savings.

This software was built using Python. The libraries used to help build some functionalities of the program are listed below:
- **console-menu** : was used to help build the interface and the menus.
- **tabulate** : was used to help create a neat-looking table from a dictionary data.
- **csv** : was used to read and write csv files.
- **json** : was used to read and write json files.
- **re** : was used to validate a string using Regex pattern.
- **datetime** : was used to get the current date and time.
- **sys** : was used to exit the program in case of errors.

This software was built as a submission for the CS50 Python's final project.

This software has one main file, that is `project.py`. All the functionalities of the software are written in this file. `categories.json` is a mandatory file that stores the type of income and expenses. If this file is deleted, the software will not behave as intended. `requirements.txt` lists all the dependencies needed to run this software. `test_history.csv` and `test_project.py` are files to test the three custom functions, which was required by the CS50P's final project specification.

This software has one main menu interface consisting of 6 main actions. Below is how the software will look like when first launched.
![Screenshot 1](/img/screenshot1.png)
The current total amount of money, savings, income, and expenses are displayed, and one can insert new data, deposit and withdraw, view history, and reset data. Exit is pretty self-explanatory, but the 5 other actions are what makes up this software.

By choosing **Insert new data** from the main menu, the user can insert a new income/expense data. When inserting, they will be asked to choose which type of income/expense that they are inserting. The available types for income are `Job`, `Projects`, and `Others`, and for expense are `Food & Drink`, `Transportation`, `Rent`, `Entertainment`, and `Others`. A new income data will be added to the total amount of money, and a new expense data will subtract the total amount of money.

Other than keeping track of the user's income and expenses, this software can also keep track of their savings. The user can choose **Deposit** to take some amount of money from their total money and add it to their savings, and **Withdraw** to take back some amount of money from their savings to the total amount of money.

A **View history** feature is also available, to see the user's income/expenses/savings record. Below is an example of how this will look like.
![Screenshot 2](/img/screenshot2.png)
User can also set filters to see what types of data they wanted to see.

And lastly, if the user chooses **Reset data**, all the data stored will be erased completely and permanently, resetting the software to the state of when it was first launched.

When developing this software, I set a time limit to myself so that the software won't become 'too big'. Because of said time limit, there were three features that I had planned, but eventually scrapped, that is:
- Add Custom Income/Expense Category
- Sort History by Amount, Ascending/Descending
- Add other currencies and let the user choose what currency they will be using.

And also, I was contemplating whether to use GUI or CLI interface, but opted to use CLI to cut on development time. I also contemplated whether to use `re.match` or `PromptUtils.validate_input` when writing the `validate_money` function, but opted to use `re.match` because to use `validate_input`, one had to create a PromptUtils object, and when I had to test the function in `test_project.py`, it's simply just shorter to write the test function when using `re.match`.

#### Usage:
To use this software, first you have to have Python installed on your machine. Learn more on how to install Python [here](https://www.python.org/downloads/). Then, you also have to have all the dependencies listed in **requirements.txt** installed. You can use `pip install -r requirements.txt` on your machine's terminal or other methods to do it. Finally, you can launch the program by running `python project.py` on the terminal.