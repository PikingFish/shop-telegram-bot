from configparser import ConfigParser
import sqlite3
from configparser import ConfigParser
from datetime import datetime
import item as itm

conn = sqlite3.connect('data.db')
c = conn.cursor()


class User:
    def __init__(self, user_id):
        self.user_id = user_id

        if not does_user_exist(self.get_id()):
            print(self.get_id())
            conf = ConfigParser()
            conf.read('config.ini', encoding='utf8')
            c.execute(f"INSERT INTO users VALUES(?, ?, ?, ?, ?, ?)", [self.get_id(), 0, 1 if str(self.get_id()) == conf["main_settings"]["mainadminid"] else 0, 0, 0, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            conn.commit()

    def get_id(self):
        return self.user_id

    def __clist(self):
        c.execute(f"SELECT * FROM users WHERE user_id={self.get_id()}")
        return list(c)[0]

    def is_admin(self):
        return self.__clist()[1] == 1

    def set_admin(self, value):
        c.execute(f"UPDATE users SET is_admin={value} WHERE user_id={self.get_id()}")
        conn.commit()

    # def is_support(self):
    #     return self.__clist()[2] == 1

    # def set_support(self, value):
    #     c.execute(f"UPDATE users SET is_support={value} WHERE user_id={self.get_id()}")
    #     conn.commit()

    def get_register_date(self):
        return self.__clist()[4]

    def notif_on(self):
        return self.__clist()[3] == 1

    def set_notif_enable(self, value):
        c.execute(f"UPDATE users SET notification=? WHERE user_id=?", [value, self.get_id()])
        conn.commit()

    def get_orders(self):
        c.execute(f"SELECT * FROM orders WHERE user_id=\"{self.get_id()}\"")
        return list(map(itm.Order, [order[0] for order in list(c)]))
    
    def get_cart_comma(self):
        return self.__clist()[5]
    
    def get_cart(self):
        cart = self.get_cart_comma()
        if cart == "None":
            return []
        return list(map(itm.Item, cart.split(",")))
    
    def get_cart_amount(self):
        cart = [item.get_id() for item in self.get_cart()]
        return [[itm.Item(item_id), cart.count(item_id)] for item_id in set(cart)]
    
    def get_cart_price(self):
        return sum([item_and_price[0].get_price() * item_and_price[1] for item_and_price in self.get_cart_amount()])
    
    def clear_cart(self):
        c.execute(f"UPDATE users SET cart=\"None\" WHERE user_id=?", [self.get_id()])
        conn.commit()
        
    def add_to_cart(self, item_id):
        cart = self.get_cart()
        c.execute(f"UPDATE users SET cart=? WHERE user_id=?", [",".join([str(item.get_id()) for item in cart + [itm.Item(item_id)]]) if cart else item_id, self.get_id()])
        conn.commit()
        
    def remove_from_cart(self, item_id):
        cart = [item.get_id() for item in self.get_cart()]
        cart.remove(item_id)
        cart_text = ",".join(cart)
        c.execute(f"UPDATE users SET cart=\"{cart_text}\" WHERE user_id=?", [self.get_id()])
        conn.commit()
        

def does_user_exist(user_id):
    c.execute(f"SELECT * FROM users WHERE user_id=\"{user_id}\"")
    return len(list(c)) != 0


def get_notif_list():
    c.execute(f"SELECT * FROM users WHERE notification=1")
    return map(User, [user[0] for user in list(c)])


def get_user_login(message):
    return message.from_user.username


def get_user_list():
    c.execute("SELECT * FROM users")
    return map(User, [user[0] for user in list(c)])


if __name__ == "__main__":
    user = User(772316661)
    user.add_to_cart(2)