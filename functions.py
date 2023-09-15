from collections.abc import Iterator
from error_handl_decorator import error_handling_decorator
from error_handl_decorator import CustomError
from collections import UserDict
import re
import datetime
import pickle

# classes
class Field:
    def __init__(self, value):
        self._value = None
        self.value = value
    
    def __str__(self):
        return self.value

    @property
    def value(self) -> str:
        return self._value


class Name(Field):
    @Field.value.setter
    def value(self, new_value: str):
        if new_value.isalpha():
            self._value = new_value
        else:
            raise CustomError("please provide valid name")


class Phone(Field):
    def __init__(self, value):
        super().__init__(str(value))
    
    @Field.value.setter
    def value(self, new_value: str):
        if new_value.isdigit() or new_value==None:
            self._value = new_value
        else:
            raise CustomError("phone number should contain digits only")


class Birthday(Field):
    def __init__(self, value): 
        super().__init__(value)
    
    @Field.value.setter
    def value(self, new_value: str):
        # check of birthday format
        if not re.match(r'\d{4}-\d{2}-\d{2}', new_value):
            raise CustomError("please enter a valid birthdate in the format YYYY-MM-DD")

        # convert to datetime format
        try:
            date_value = datetime.datetime.strptime(new_value, "%Y-%m-%d")
        except:
            raise CustomError("please enter a valid birthdate in the format YYYY-MM-DD")
        
        # check the date correctness
        if not (1900 <= date_value.year <= datetime.date.today().year and
                    1 <= date_value.month <= 12 and
                    1 <= date_value.day <= 31):
                raise CustomError("please enter a valid birthdate in the format YYYY-MM-DD")
        dob = date_value.date()
        self._value = dob
    

class Record:
    def __init__(self, name, phone=None, birthday=None): 
        self.name = Name(value=name)
        self.phones = []
        if phone:
            self.add_new_phone(phone)
        if birthday:
            self.birthday = Birthday(value=birthday)

    def days_to_birthday(self):
        current_date = datetime.date.today()
        next_birthday = datetime.date(current_date.year, self.birthday.value.month, self.birthday.value.day)
        
        if current_date > next_birthday:
            next_birthday = datetime.date(current_date.year + 1, self.birthday.value.month, self.birthday.value.day)
            
        days_until_birthday = (next_birthday - current_date).days

        return days_until_birthday

    def add_new_phone(self, phone): 
        self.phones.append(Phone(value=phone))

    def amend_phone(self, name, new_phone, old_phone): 
        phone_found = False
        for stored_phone in self.phones.copy():
            if str(stored_phone) == old_phone:
                self.phones.remove(stored_phone)
                self.add_new_phone(new_phone)
                phone_found = True

        if not phone_found:
            raise CustomError("phone number was not found")

    def remove_phone(self, phone):
        phone_found = False
        for stored_phone in self.phones.copy():
            if str(stored_phone) == phone:
                self.phones.remove(stored_phone)
                phone_found = True

        if not phone_found:
            raise CustomError("phone number was not found")


phone_book_file = r'/home/mike/Desktop/py_scripts/Home works/hw7_contacts_bot_ inFile/phone_book'


class AddressBook(UserDict):
    def __init__(self):
        super().__init__()
        try:
            with open(phone_book_file, "rb") as fh:
                deserialized_book = pickle.load(fh)
            self.data = deserialized_book
        except:
            pass

    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def iterator(self, n): # n-number of records per page. is defined in show_page function
        contacts_per_page = n
        contacts = list(self.data.keys())
        index = 0

        while index < len(contacts):
            yield contacts[index:index + contacts_per_page]
            index += contacts_per_page

phone_book = AddressBook()

# parser
@error_handling_decorator
def parse_input(user_input):
    for request in commands:  # commands: hello, search, show all, contact, add, remove, change
        if user_input.startswith(request):
            func = commands[request] 
            modif_input = user_input.replace(request, '', 1).strip()
            name = modif_input.split(' ')[0]            
            x = re.findall(r'\d+', modif_input)
            phone_numbers = [match for match in x if len(match) > 5]
            birthday_list = re.findall(r'\b\d{4}-\d{2}-\d{2}\b', modif_input) # birthday format YYYY-MM-DD
            page_list = [match for match in x if len(match) <= 2]

            if len(phone_numbers) == 2: # serves for change function
                return func(name, phone_numbers[0], phone_numbers[1])
            
            try:
                phone_numb = phone_numbers[0]
            except IndexError:
                phone_numb = None
            try:
                birth_date = birthday_list[0]
            except IndexError:
                birth_date = None
            try:
                page = page_list[0]
            except IndexError:
                page = None

            return func(name, phone_numb, birth_date, page)
        
    raise CustomError("please provide a valid command")


# adding new contact/phone number
def add_contact (name, phone=None, birthday=None, notused=None): 
    if not name:  
        raise CustomError("please provide name")
    elif name not in phone_book:
        record = Record(name, phone, birthday)
        phone_book.add_record(record)
        return "new contact successfully added"
    else:
        record = phone_book[name]

        if phone:
            record.add_new_phone(phone)
        if birthday:
            record.birthday = Birthday(value=birthday)

        return "new information successfully added to existing contact"


# change the phone number
def change_phone (name, new_phone, old_phone):
    if name not in phone_book:
        raise CustomError('name not found')
    if not new_phone or not old_phone:
        raise CustomError("please provide name, new number and old number divided by space")
    
    record = phone_book[name]
    record.amend_phone(name, new_phone, old_phone)
    return "contact successfully changed"


# remove the phone number or birthdays
def delete_info(name, phone=None, birthday=None, notused=None):
    if name not in phone_book:
        raise CustomError('name not found')
    if not phone and not birthday:
        raise CustomError("please provide valid phone number or birthday")
    record = phone_book[name]
    if phone:
        record.remove_phone(phone)
        return("phone number successfully removed")
    elif birthday:
        if hasattr(record, 'birthday'):
            record.birthday = None
            return("birthday successfully removed")
        else:
            raise CustomError("no birthday exist for this contact")


# show the phone of user
def show_contact (name, notused=None, notused2=None, notused3=None): 
    if name not in phone_book:
        raise CustomError("please provide a valid name")
    
    record = phone_book[name]
    phone_numbers = []
        
    for item in record.phones:
        phone_numbers.append(item.value)

    if len(phone_numbers) > 0:
        phone_str = f"{', '.join(phone_numbers)}"
    else:
        phone_str = 'no phone numbers'

    if hasattr(record, 'birthday'):
        birthday_str = record.birthday.value.strftime('%Y-%m-%d')
    else:
        birthday_str = 'no birthday recorded'

    return f"{name}: {phone_str}, {birthday_str}"


# show all contacts info
def show_all(notused=None, notused1=None, notused2=None, notused3=None):
    contacts = []
    for record in phone_book:
        one_contact = show_contact(record)
        contacts.append(one_contact)
    if contacts:
        return ';\n'.join(contacts)
    else:
        raise CustomError("phone book is empty")


def show_page(notused=None, notused1=None, notused2=None, page=None):
    try:
        page_number = int(page)
        contacts_per_page = 2

        if page_number < 1:
            raise CustomError("pages start from 1")

        contact_batches = list(phone_book.iterator(contacts_per_page))

        if page_number <= len(contact_batches):
            contacts = contact_batches[page_number - 1]
            return ';\n'.join([show_contact(contact) for contact in contacts])
        else:
            raise CustomError("page not found")

    except ValueError:
        raise CustomError("invalid page number")


def hello(notused1=None, notused2=None, notused3=None, notused4=None):
    return("How can I help you?")


def search (search_word, notused1=None, notused2=None, notused3=None):
    result= []
    for name, record in phone_book.items():
        if len(record.phones) > 0:
            phone_numbers = ', '.join(phone.value for phone in record.phones)
            print(phone_numbers)
        else:
            phone_numbers = 'no phone numbers'
        try:
            birthday_str = record.birthday.value.strftime('%Y-%m-%d')
        except AttributeError:
            birthday_str = "no birthday recorded"
        
        if (search_word in name) or (search_word in phone_numbers) or (search_word == birthday_str):
            result.append(f"{name}: {phone_numbers}, {birthday_str}")

    if result:
        return ';\n'.join(result)
    else:
        raise CustomError("nothing found")


def dtb(name,notused=None, notused2=None, notused3=None):
    if name not in phone_book:
        raise CustomError("please provide a valid name")
    
    record = phone_book[name]
    if not hasattr(record, 'birthday'):
            raise CustomError ("no birthday recorded")
    return record.days_to_birthday()


commands = {
    "add": add_contact,
    "contact": show_contact,
    "change": change_phone,
    "show all": show_all,
    "page": show_page,
    "remove": delete_info,
    "hello": hello,
    "search": search,
    "dtb": dtb,
}

