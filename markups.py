from telebot import types

mk_1 = types.InlineKeyboardMarkup()
mk_1.row(
    types.InlineKeyboardButton(text="Add password", callback_data="add_password"),
    types.InlineKeyboardButton(text="Remove password", callback_data="remove_password"),
)
mk_1.add(types.InlineKeyboardButton(text="See my passwords", callback_data="see_passwords"))
mk_1.add(types.InlineKeyboardButton(text="Contact developer", callback_data="contacts"),)


mk_2 = types.InlineKeyboardMarkup()
mk_2.row(
    types.InlineKeyboardButton(text="Add password", callback_data="add_password"),
    types.InlineKeyboardButton(text="Remove password", callback_data="remove_password"),
)
mk_2.add(types.InlineKeyboardButton(text="See my passwords", callback_data="see_passwords"))

mk_3 = types.InlineKeyboardMarkup()
mk_3.add(types.InlineKeyboardButton(text="See my password for a given service", callback_data="see_1_password"))
mk_3.add(types.InlineKeyboardButton(text="See all my passwords", callback_data="see_all_passwords"))
