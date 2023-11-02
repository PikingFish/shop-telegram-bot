from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import message

# Item management
class addCat(StatesGroup):
    state_message = State()
    name = State()

class changeCatName(StatesGroup):
    state_message = State()
    cat_id = State()
    name = State()

class addItem(StatesGroup):
    name = State()
    price = State()
    cat_id = State()
    desc = State()
    confirmation = State()

class changeItemPrice(StatesGroup):
    state_message = State()
    item_id = State()
    price = State()

class changeItemDesc(StatesGroup):
    state_message = State()
    item_id = State()
    desc = State()
    
# User management
class notifyEveryone(StatesGroup):
    state_message = State()
    message = State()
    confirmation = State()









