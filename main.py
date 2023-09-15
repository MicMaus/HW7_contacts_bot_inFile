from functions import parse_input, phone_book_file, phone_book
import pickle

# tuple of commands to close the bot
close_app = ('exit', 'good bye', 'close') 


def main():
    while True:
        user_input = input("your input: ").lower()

        if user_input.startswith(close_app):
            print("Good bye!")

            with open(phone_book_file, "wb") as fh:
                pickle.dump(phone_book, fh)

            break

        result = parse_input(user_input) 
        if result is not None: 
            print(result) 


if __name__ == "__main__":
    main()
