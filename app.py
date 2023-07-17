from logic import *

# current_post = []

telegram_bot_token = "6346062239:AAF6xZa93p6J_-DrT9c1k0pWqczbHDfopRg"

updater = Updater(token=telegram_bot_token, use_context=True)
dispatcher = updater.dispatcher
admin_ids = [542430395]  
# ready_db = []
# draft_db = []


def start(update, context):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text="Hello! This is 'Company name' TG bot, Use /help to see available features!")


def help(update, context):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text="Help message: " \
                                                    "\n* Use /available-tags to see which tags to topics have been added already, " \
                                                    "you can search specific topics using these tags" \
                                                    "\n\nThere're searches available - each of them will provide you with some descriptions. Choose the one you're looking for,"\
                                                    " request for more or choose the one you want to get the full content of that particular post"\
                                                    "\n\n* Use /search_by_tag with at least one topic-tag to search for the related topics"\
                                                    "\n* Use /search_by_description with some part of the description to get the context you're looking for")


def search_by_tag(update, context):
    chat_id = update.effective_chat.id
    args = context.args
    str_return = ", ".join(str(i) for i in args)
    context.bot.send_message(chat_id=chat_id, text=f'Accepted: {str_return}')
    
def search_by_description(update, context):
    chat_id = update.effective_chat.id
    args = context.args
    str_return = ", ".join(str(i) for i in args)
    context.bot.send_message(chat_id=chat_id, text=f'Accepted: {str_return}')


def admin_only_helth_check(update: Update, context):
    user_id = update.effective_user.id
    if user_id in admin_ids:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Available features except the basic ones:"\
                                                                        "\n\n* /start_new_post - start new post and follow the "\
                                                                        "step-by-step instructions to complete it"\
                                                                        "\n* / something else bla-bla-bla")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, you don't have permission to use this feature.")
        
        
        
def start_new_post(update, context):
    
    chat_id = update.effective_chat.id
    args = context.args
    # str_return = ", ".join(str(i) for i in args)
    # context.bot.send_message(chat_id=chat_id, text=f'Accepted: {str_return}')
    description_change = "Add description"
    if len(descriptions)>0:
        description_change = "Change description"
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Add photos", callback_data=f"add_photos"),
         InlineKeyboardButton("Add tags", callback_data=f"add_tags"),
         InlineKeyboardButton(description_change, callback_data=f"add_description"),
         InlineKeyboardButton("Finish", callback_data="done_post")]
    ])
    context.bot.send_message(chat_id=chat_id, text="Photo submitted successfully.", reply_markup=reply_markup)

def button_callback(update, context):
    query = update.callback_query

    callback_data = query.data

    if callback_data.startswith("submit_"):
        photo_index = int(callback_data.split("_")[1])
        query.message.reply_text(f"Please submit photo {photo_index}.")
    elif callback_data.startswith("done") and not callback_data.startswith("done_ph"):
        done_post(update, context)
    elif callback_data.startswith("add_photos"):
        add_photos(update, context)
    elif callback_data.startswith("add_description"):
        query.message.reply_text("Please enter the description.")
        # add_description(update, context)
    elif callback_data.startswith("add_cp_to_readyDB"):
        done(update, context, "ready")
    elif callback_data.startswith("add_cp_to_draftDB"):
        done(update, context, "draft")
        # add_tags(update, context)
    elif callback_data.startswith("done_ph"):
        done_ph(update, context)
        

        
for admin_id in admin_ids:
    dispatcher.add_handler(CommandHandler("admin_only_helth_check", admin_only_helth_check, Filters.user(user_id=admin_id)))
    dispatcher.add_handler(CommandHandler("start_new_post", start_new_post, Filters.user(user_id=admin_id)))
    # dispatcher.add_handler(CommandHandler("add_photos", add_photos, Filters.user(user_id=admin_id)))
    # dispatcher.add_handler(CommandHandler("add_description", add_description))

    # Register the callback query handler
    dispatcher.add_handler(CallbackQueryHandler(button_callback))

# Register the handler for user input of the description
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_description))
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", help))
dispatcher.add_handler(CommandHandler("search_by_tag", search_by_tag))
dispatcher.add_handler(CommandHandler("search_by_description", search_by_description))


# dispatcher.add_handler(CommandHandler("add_photos", add_photos))

dispatcher.add_handler(CallbackQueryHandler(button_callback))

dispatcher.add_handler(MessageHandler(Filters.photo, photo_handler))

dispatcher.add_handler(CommandHandler("done", done))

updater.start_polling()