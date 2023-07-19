from logic import *
from config_loader import telegram_bot_token, admin_ids
# current_post = []

# telegram_bot_token = os.environ.get('telegram_bot_token')
url_tag_search = 'http://127.0.0.1:5000/search_posts_by_tags'
url_desc_search = 'http://127.0.0.1:5000/search_posts_by_descs'
updater = Updater(token=telegram_bot_token, use_context=True)

dispatcher = updater.dispatcher

# admin_ids = os.environ.get('tg_bot_admin_ids').split()


description_changes = False
description_appends = False
photo_appends = False
tags_append=False
user_id = None
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB



def start(update, context):
    global user_id
    user_id = int(update.message.from_user.id)
    chat_id = update.effective_chat.id
    if int(update.message.from_user.id) in admin_ids:
        context.bot.send_message(chat_id=chat_id, text="Hi admin, here's help for you:")
        help(update, context)
        
    else:
        context.bot.send_message(chat_id=chat_id, text="Hello! This is 'Company name' TG bot, Use /help to see available features!")
        help(update, context)


def help(update, context):
    global user_id
    chat_id = update.effective_chat.id
    try:
        if user_id==None:
            user_id = int(update.message.from_user.id)
    except AttributeError:
        context.bot.send_message(chat_id=chat_id, text="Bot was restarted, press /start to authorize")
    
    context.bot.send_message(chat_id=chat_id, text="Help message: " \
                                                    "\n* Use /available-tags to see which tags to topics have been added already, " \
                                                    "you can search specific topics using these tags" \
                                                    "\n\nThere're searches available - each of them will provide you with some descriptions. Choose the one you're looking for,"\
                                                    " request for more or choose the one you want to get the full content of that particular post"\
                                                    "\n\n* Use /search_by_tag with at least one topic-tag to search for the related topics"\
                                                    "\n* Use /search_by_description with some part of the description to get the context you're looking for")

    if user_id in admin_ids:
        reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Help", callback_data=f"help_post")],
         [InlineKeyboardButton("Start New Post", callback_data=f"st_new_post")],
         [InlineKeyboardButton("Review Public DB", callback_data=f"review_public")]
         ])
        
        context.bot.send_message(chat_id=chat_id, text="\n\nAdmin features:"\
                                                        "\n* /start_new_post - to start creating a post, follow step-by-step help there"\
                                                        "\n* /review_public_db - review saved posts and continue editing / delete / mmove to ready_posts db for review",
                                                        reply_markup=reply_markup)
        

def search_by_tag(update, context):
    chat_id = update.effective_chat.id
    args = context.args
    str_return = " ".join(str(i) for i in args)
    context.bot.send_message(chat_id=chat_id, text=f'Accepted: {str_return}')
    params = {'query': str_return}
    response = requests.get(url_tag_search, params=params)
    if response.status_code == 200:
        context.bot.send_message(chat_id=chat_id, text=f'Preparing posts...')
    else:
        text = f"Request failed with status code: {response.status_code}"
        context.bot.send_message(chat_id=chat_id, text=text)
    for i in range(len(response.json())):
        send_post(update, context, response.json()[i][0])
    help(update, context)

    
def search_by_description(update, context):
    chat_id = update.effective_chat.id
    args = context.args
    str_return = " ".join(str(i) for i in args)
    context.bot.send_message(chat_id=chat_id, text=f'Accepted: {str_return}')
    params = {'query': str_return}
    response = requests.get(url_desc_search, params=params)
    if response.status_code == 200:
        context.bot.send_message(chat_id=chat_id, text=f'Preparing posts...')
    else:
        text = f"Request failed with status code: {response.status_code}"
        context.bot.send_message(chat_id=chat_id, text=text)
    for i in range(len(response.json())):
        send_post(update, context, response.json()[i][0])
    help(update, context)


def admin_only_helth_check(update: Update, context):
    global user_id
    if user_id in admin_ids:
        user_id = update.effective_user.id
        if user_id in admin_ids:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Available features except the basic ones:"\
                                                                            "\n\n* /start_new_post - start new post and follow the "\
                                                                            "step-by-step instructions to complete it"\
                                                                            "\n* / something else bla-bla-bla")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, you don't have permission to use this feature.")
        
        
        
def start_new_post(update, context):
    global user_id
    try:
        if user_id==None:
            user_id = int(update.message.from_user.id)
    except AttributeError:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Bot was restarted, press /start to authorize")
    
    if user_id in admin_ids:
        chat_id = update.effective_chat.id
        args = context.args
        description_change = "Add description"
        if len(descriptions)>0:
            description_change = "Change description"
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Add photos", callback_data=f"add_photos")],
            [InlineKeyboardButton("Add tags", callback_data=f"add_tags")],
            [InlineKeyboardButton(description_change, callback_data=f"add_description")],
            [InlineKeyboardButton("Finish", callback_data="done_post")]]
        )
        context.bot.send_message(chat_id=chat_id, text="Editing Post", reply_markup=reply_markup)
    

def button_callback(update, context):
    global user_id
    try:
        if user_id==None:
            user_id = int(update.message.from_user.id)
    except AttributeError:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Bot was restarted, press /start to authorize")
    
    
    if user_id in admin_ids:
        global description_appends, description_changes, photo_appends, tags_append
        global descriptions, photos, tags, current_id
        query = update.callback_query

        callback_data = query.data

        if callback_data.startswith("submit_"):
            photo_appends = True
            photo_index = int(callback_data.split("_")[1])
            query.message.reply_text(f"Please submit photo {photo_index}.")
            
        elif callback_data.startswith("done") and not callback_data.startswith("done_ph"):       
            send_photos_and_text(update, context)
            done_post(update, context)
        
        elif callback_data.startswith("add_photos"):
            photo_appends = True
            add_photos(update, context)
        elif callback_data.startswith("add_description"):
            description_appends = True
            query.message.reply_text("Please enter the description.")
        elif callback_data.startswith("new_desc"):
            description_changes = True
            query.message.reply_text("Please enter the description.")
        elif callback_data.startswith("delete_desc"):
            descriptions.clear()
            query.message.reply_text(f"Current Post Overview so far:")
            send_photos_and_text(update, context)
            
            start_new_post(update, context)
        elif callback_data.startswith("save_desc_to_cp"):
            query.message.reply_text(f"Current Post Overview so far:")
            send_photos_and_text(update, context)

            start_new_post(update, context)
            
        elif callback_data.startswith("add_tags"):
            tags_append=True
            query.message.reply_text(f"Please write each tag separated by space, aka: \nfood drinks hotels mermaids")
        elif callback_data.startswith("delete_tags"):
            tags.clear()
            query.message.reply_text(f"All tags attached to current post are deleted")
            query.message.reply_text(f"Current Post Overview so far:")
            send_photos_and_text(update, context)
            start_new_post(update, context)
        elif callback_data.startswith("save_tags_to_cp"):
            query.message.reply_text(f"All tags attached to current post are saved successfully!")
            query.message.reply_text(f"Current Post Overview so far:")
            send_photos_and_text(update, context)
            start_new_post(update, context)

        elif callback_data.startswith("add_cp_to_PublicDB"):
            done(update, context)
        
        elif callback_data.startswith("delete_whole_p"):
            delete_whole_post(update, context)
            query.message.reply_text(f"Current Post in edit was cleared.")
            help(update, context)
            
        elif callback_data.startswith("done_ph"):
            query.message.reply_text(f"Current Post Overview so far:")
            send_photos_and_text(update, context)
            done_ph(update, context)
            
        elif callback_data.startswith("st_new_post"):
            start_new_post(update, context)
            
        elif callback_data.startswith("help_post"):
            help(update, context)

        elif callback_data.startswith("review_public"):
            review_db(update, context)

            
        elif callback_data.startswith("delete_public_"):
            post_id = int(callback_data.split("_")[-1])
            url = f'http://127.0.0.1:5000/admin/delete_post/{post_id}'
        
            response = requests.delete(url)
            query.message.reply_text(f"Deleted Post {post_id}, response_code: {response.status_code}")
            help(update, context)



def handle_description(update, context):
    global description_appends, description_changes, tags_append, tags
    if description_appends:
        description = update.message.text

        descriptions.append(description)
    elif description_changes:
        description = update.message.text
        descriptions.clear()
    
        descriptions.append(description)    
    if description_appends or description_changes:
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Save", callback_data="save_desc_to_cp")],
            [InlineKeyboardButton("Append more", callback_data="add_description")],
            [InlineKeyboardButton("Write a new one", callback_data="new_desc")],
            [InlineKeyboardButton("Delete", callback_data="delete_desc")]
        ])
        
        update.message.reply_text(f'Description now: {"/n".join(descriptions)}', reply_markup=reply_markup)
        description_changes = False
        description_appends = False
    
    
    elif tags_append:
        tags_reply = update.message.text
        tags += tags_reply.split()
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Save", callback_data="save_tags_to_cp")],
            [InlineKeyboardButton("Append more", callback_data="add_tags")],
            [InlineKeyboardButton("Delete all", callback_data="delete_tags")]
        ])
        
        update.message.reply_text(f"Tags for the current post: {' '.join(tags)}", reply_markup=reply_markup)
        tags_append = False
    else:
        update.message.reply_text("Can not submit any messages yet")
        if int(update.message.from_user.id) in admin_ids:
            start_new_post(update, context)
        else:
            help(update, context)


def handle_video(update, context):
    global photo_appends
    if photo_appends:
        if len(photos) >= 10:
            update.message.reply_text("You have already submitted the maximum number of media.")
            return
        video = update.message.video

        if video.file_size > MAX_FILE_SIZE_BYTES:
            update.message.reply_text("Sorry, the video size is too large. Please send a svideo of up to 10MB size")
            return

        video_file = video.get_file()

        file_path = f"{video_file.file_id}.mp4"

        num_pht = len(photos)+1
        video_file.download(file_path)
        photos.append(file_path)   
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"Submit Photo {num_pht}", callback_data=f"submit_{num_pht}"),
            InlineKeyboardButton("Finish", callback_data="done_ph")]
        ])
        
        photo_appends=False
        update.message.reply_text("Video received and saved!", reply_markup=reply_markup)
        
    else: 
        update.message.reply_text("Can not submit any videos")
        if int(update.message.from_user.id) in admin_ids:
            start_new_post(update, context)
        else:
            help(update, context)
    

def photo_handler(update, context):
    global photo_appends
    if photo_appends:
        if len(photos) >= 10:
            update.message.reply_text("You have already submitted the maximum number of media.")
            return

        photo = update.message.photo[-1]

        filename = f"{photo.file_id}.jpg"

        save_path = filename

        photo.get_file().download(save_path)

        photos.append(save_path)    
        num_pht = len(photos)+1
        
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"Submit Photo {num_pht}", callback_data=f"submit_{num_pht}"),
            InlineKeyboardButton("Finish", callback_data="done_ph")]
        ])
        update.message.reply_text("Photo submitted successfully.", reply_markup=reply_markup)
        
        photo_appends=False
    else: 
        update.message.reply_text("Can not submit any photos")
        if int(update.message.from_user.id) in admin_ids:
            start_new_post(update, context)
        else:
            help(update, context)
        
def send_photos_and_text(update, context):
    media = [InputMediaPhoto(open(photo_path, 'rb')) for photo_path in photos]

    text = "\n".join(descriptions)+"\n"
    if len(tags)>0:
        text+=f"Tags: {', '.join(tags[:-1])}"+f"{tags[-1]}"

    if len(media) >0:
        context.bot.send_media_group(chat_id=update.effective_chat.id, media=media)

    if text=='\n':
        text = "No description or tags provided for current post yet"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.MARKDOWN)
        
def send_post(update, context, dct):
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Post with ID {dct['id']} \/\/\/\/\/\/\/\/\/")
    media = [InputMediaPhoto(open('media/'+photo_path, 'rb')) for photo_path in dct["photos"].split(',') if len(dct["photos"])>0]

    text = dct["description"]+"\n"
    if len(tags)>0:
        text+=f"Tags: {' '.join(dct['tags'][:-1])}"+f"{tags[-1]}"

    if len(media) >0:
        context.bot.send_media_group(chat_id=update.effective_chat.id, media=media)

    if text=='\n':
        text = "No description or tags provided for current post yet"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.MARKDOWN)
        
            
for admin_id in admin_ids:
    dispatcher.add_handler(CommandHandler("admin_only_helth_check", admin_only_helth_check, Filters.user(user_id=admin_id)))
    dispatcher.add_handler(CommandHandler("start_new_post", start_new_post, Filters.user(user_id=admin_id)))
    dispatcher.add_handler(MessageHandler(Filters.photo, photo_handler))
    
    dispatcher.add_handler(CallbackQueryHandler(button_callback))

    dispatcher.add_handler(CommandHandler("done", done))

dispatcher.add_handler(CallbackQueryHandler(button_callback))

dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_description))
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", help))
dispatcher.add_handler(CommandHandler("search_by_tag", search_by_tag))
dispatcher.add_handler(CommandHandler("search_by_description", search_by_description))
dispatcher.add_handler(MessageHandler(Filters.video, handle_video))


updater.start_polling()