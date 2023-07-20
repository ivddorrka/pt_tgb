from logic import *
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from config_loader import telegram_bot_token, admin_ids

URL_TAG_SEARCH = 'http://127.0.0.1:5000/search_posts_by_tags'
URL_DESCRIPTION_SEARCH = 'http://127.0.0.1:5000/search_posts_by_descs'
URL_ALL_POSTS = 'http://127.0.0.1:5000/search_all'
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

# description_changes = False
# description_appends = False
# description_user = False
# tags_user = False
# photo_appends = False
# tags_append=False
# user_id = None
# {
#     'chatd_id':
#         {
#             user
#         }
# }



def start(update, context):
    # global user_id
    global user_info_dct
    
    user_id = int(update.message.from_user.id)
    chat_id = update.effective_chat.id
    
    if chat_id not in user_info_dct:
        user_info_dct[chat_id] = {'user_id': user_id, 
                                  'photos':[], 'tags':[], 'current_post' : [],'descriptions': [], 
                                  'user_flags': { 'description_changes': False, 'description_appends': False,
                                  'description_user': False, 'tags_user': False, 'photo_appends': False, 'tags_append': False}}
        
    #     descriptions = user_info_dct[chat_id]['descriptions']
    # descriptions = user_info_dct[chat_id]['photos']
    # descriptions = user_info_dct[chat_id]['tags']
    # descriptions = user_info_dct[chat_id]['current_post']
    delete_whole_post(update, context)
    if int(update.message.from_user.id) in admin_ids:
        context.bot.send_message(chat_id=chat_id, text="Hi admin, here's help for you:")
        help(update, context)
        
    else:
        context.bot.send_message(chat_id=chat_id, text="Hello! This is 'Company name' TG bot, Use /help to see available features!")
        help(update, context)


def help(update, context):
    # global user_id
    global user_info_dct
    
    chat_id = update.effective_chat.id
    try:
        user_id = user_info_dct[chat_id]['user_id']
    except KeyError:
        user_id = None
    
    if not user_id:
        context.bot.send_message(chat_id=chat_id, text="Bot was restarted, press /start to authenticate") 
    else:
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Search By Tags", callback_data=f"search_tags")],
            [InlineKeyboardButton("Search By Description", callback_data=f"search_description")]
            ])
        
        context.bot.send_message(chat_id=chat_id, text="Help message: " \
                                                        "\n\nThere're searches available - each of them will provide you with some descriptions. Choose the one you're looking for,"\
                                                        " request for more or choose the one you want to get the full content of that particular post"\
                                                        "\n\n* Use 'search by tag' with at least one topic-tag to search for the related topics"\
                                                        "\n* Use 'search by description' with some part of the description to get the context you're looking for", reply_markup=reply_markup)

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
            

def search_by_tag(update, context, str_return):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm here!!!")
    global user_info_dct    
    chat_id = update.effective_chat.id
    try:
        user_id = user_info_dct[chat_id]['user_id']
    except KeyError:
        user_id = None
        
    if not user_id:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Bot was restarted, press /start to authenticate") 
    else:
        chat_id = update.effective_chat.id
        # args = context.args
        # str_return = " ".join(str(i) for i in args)
        context.bot.send_message(chat_id=chat_id, text=f'Accepted: {str_return}')
        params = {'query': str_return}
        response = requests.get(URL_TAG_SEARCH, params=params)
        if response.status_code == 200:
            context.bot.send_message(chat_id=chat_id, text=f'Preparing posts...')
        else:
            text = f"Request failed with status code: {response.status_code}"
            context.bot.send_message(chat_id=chat_id, text=text)
        for i in range(len(response.json())):
            send_post(update, context, response.json()[i][0])
        help(update, context)
        

    
def search_by_description(update, context, str_return):
    global user_info_dct    
    chat_id = update.effective_chat.id
    try:
        user_id = user_info_dct[chat_id]['user_id']
    except KeyError:
        user_id = None
        
        
    if not user_id:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Bot was restarted, press /start to authenticate") 
    else:
        chat_id = update.effective_chat.id
        # args = context.args
        # str_return = " ".join(str(i) for i in args)
        context.bot.send_message(chat_id=chat_id, text=f'Accepted: {str_return}')
        params = {'query': str_return}
        response = requests.get(URL_DESCRIPTION_SEARCH, params=params)
        if response.status_code == 200:
            context.bot.send_message(chat_id=chat_id, text=f'Preparing posts...')
        else:
            text = f"Request failed with status code: {response.status_code}"
            context.bot.send_message(chat_id=chat_id, text=text)
        for i in range(len(response.json())):
            send_post(update, context, response.json()[i][0])
        help(update, context)


def admin_only_helth_check(update: Update, context):
    global user_info_dct    
    chat_id = update.effective_chat.id
    try:
        user_id = user_info_dct[chat_id]['user_id']
    except KeyError:
        user_id = None
        
    if not user_id:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Bot was restarted, press /start to authenticate") 
    else:
    
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
    global user_info_dct    
    chat_id = update.effective_chat.id
    try:
        user_id = user_info_dct[chat_id]['user_id']
    except KeyError:
        user_id = None
        
    if not user_id:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Bot was restarted, press /start to authenticate") 
    else:
        if user_id in admin_ids:
            chat_id = update.effective_chat.id
            args = context.args
            description_change = "Add description"
            if len(user_info_dct[chat_id]['descriptions'])>0:
                description_change = "Change description"
                reply_markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton("Add photos", callback_data=f"add_photos")],
                    [InlineKeyboardButton("Add tags", callback_data=f"add_tags")],
                    [InlineKeyboardButton(description_change, callback_data=f"new_desc")],
                    [InlineKeyboardButton("Finish", callback_data="done_post")]]
                )
            else:
                reply_markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton("Add photos", callback_data=f"add_photos")],
                    [InlineKeyboardButton("Add tags", callback_data=f"add_tags")],
                    [InlineKeyboardButton(description_change, callback_data=f"add_description")],
                    [InlineKeyboardButton("Finish", callback_data="done_post")]]
                )
            context.bot.send_message(chat_id=chat_id, text="Editing Post", reply_markup=reply_markup)
    

def button_callback(update, context):
    global user_info_dct    
    chat_id = update.effective_chat.id
    try:
        user_id = user_info_dct[chat_id]['user_id']
    except KeyError:
        user_id = None
        
    # global description_user, tags_user
    if user_id==None:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Bot was restarted, press /start to authenicate")
    else:   
        
       
        description_user = user_info_dct[chat_id]['user_flags']['description_user']
        tags_user = user_info_dct[chat_id]['user_flags']['tags_user']
        
        query = update.callback_query

        callback_data = query.data
        if user_id in admin_ids:
             
                                
            description_appends= user_info_dct[chat_id]['user_flags']['description_appends']
            description_changes=user_info_dct[chat_id]['user_flags']['description_changes']
            photo_appends=user_info_dct[chat_id]['user_flags']['photo_appends']
            tags_append=user_info_dct[chat_id]['user_flags']['tags_append']
            descriptions=user_info_dct[chat_id]['descriptions']
            photos= user_info_dct[chat_id]['photos']
            tags= user_info_dct[chat_id]['tags']
            
            if callback_data.startswith("submit_"):
                user_info_dct[chat_id]['user_flags']['photo_appends'] = True
                photo_index = int(callback_data.split("_")[1])
                query.message.reply_text(f"Please submit photo {photo_index}.")
                
            elif callback_data.startswith("done") and not callback_data.startswith("done_ph"):       
                send_photos_and_text(update, context)
                done_post(update, context)
            
            elif callback_data.startswith("add_photos"):
                user_info_dct[chat_id]['user_flags']['photo_appends'] = True
                add_photos(update, context)
                
            elif callback_data.startswith("add_description"):
                user_info_dct[chat_id]['user_flags']['description_appends'] = True
                query.message.reply_text("Please enter the description.")
                
            elif callback_data.startswith("new_desc"):
                user_info_dct[chat_id]['user_flags']['description_changes'] = True
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
                user_info_dct[chat_id]['user_flags']['tags_append']=True
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
                done(update, context, user_id)
            
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
                url = f'http://127.0.0.1:5000/admin/delete_post/{post_id}?tg_id={user_id}'
            
                response = requests.delete(url)
                query.message.reply_text(f"Deleted Post {post_id}, response_code: {response.status_code}")
                help(update, context)
            
            if callback_data.startswith("search_description"):
                query.message.reply_text(f"Submit a part of description you want to search by")
                user_info_dct[chat_id]['user_flags']['description_user']=True

            elif callback_data.startswith("search_tags"):
                query.message.reply_text(f"Write all tags you want post to include separated by spaces")
                user_info_dct[chat_id]['user_flags']['tags_user']=True
        else:      
            
            if callback_data.startswith("search_description"):
                query.message.reply_text(f"Submit a part of description you want to search by")
                user_info_dct[chat_id]['user_flags']['description_user']=True

            elif callback_data.startswith("search_tags"):
                query.message.reply_text(f"Write all tags you want post to include separated by spaces")
                user_info_dct[chat_id]['user_flags']['tags_user']=True
                      
        
            


def handle_description(update, context):
    global user_info_dct    
    chat_id = update.effective_chat.id
    try:
        user_id = user_info_dct[chat_id]['user_id']
    except KeyError:
        user_id = None
        
    if user_id==None:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Bot was restarted, press /start to authenicate")
    else:
        
        description_user = user_info_dct[chat_id]['user_flags']['description_user']
        tags_user = user_info_dct[chat_id]['user_flags']['tags_user']
        description_appends= user_info_dct[chat_id]['user_flags']['description_appends']
        description_changes=user_info_dct[chat_id]['user_flags']['description_changes']
        tags_append=user_info_dct[chat_id]['user_flags']['tags_append']
            
        if description_user:
            description = update.message.text
            search_by_description(update, context, description)
            user_info_dct[chat_id]['user_flags']['description_user'] = False
        if tags_user:
            tags = update.message.text
            search_by_tag(update, context, tags)
            user_info_dct[chat_id]['user_flags']['tags_user'] = False
            
        if description_appends:
            description = update.message.text
            user_info_dct[chat_id]['descriptions'].append(description)
            
        elif description_changes:
            description = update.message.text
            user_info_dct[chat_id]['descriptions'].clear()
        
            user_info_dct[chat_id]['descriptions'].append(description)    
        if description_appends or description_changes:
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Save", callback_data="save_desc_to_cp")],
                [InlineKeyboardButton("Append more", callback_data="add_description")],
                [InlineKeyboardButton("Write a new one", callback_data="new_desc")],
                [InlineKeyboardButton("Delete", callback_data="delete_desc")]
            ])
            
            update.message.reply_text(f"Description now: {' '.join(user_info_dct[chat_id]['descriptions'])}", reply_markup=reply_markup)
            
            user_info_dct[chat_id]['user_flags']['description_changes'] = False
            user_info_dct[chat_id]['user_flags']['description_appends'] = False
    
    
        elif tags_append:
            tags_reply = update.message.text
            user_info_dct[chat_id]['tags'] += tags_reply.split()
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Save", callback_data="save_tags_to_cp")],
                [InlineKeyboardButton("Append more", callback_data="add_tags")],
                [InlineKeyboardButton("Delete all", callback_data="delete_tags")]
            ])
            
            update.message.reply_text(f"Tags for the current post: {' '.join(user_info_dct[chat_id]['tags'])}", reply_markup=reply_markup)
            user_info_dct[chat_id]['user_flags']['tags_append'] = False
     

def handle_video(update, context):
    global user_info_dct    
    chat_id = update.effective_chat.id
    try:
        user_id = user_info_dct[chat_id]['user_id']
    except KeyError:
        user_id = None
        
    if user_id==None:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Bot was restarted, press /start to authenicate")
    else:
        
        if user_info_dct[chat_id]['user_flags']['photo_appends']:
            if len(user_info_dct[chat_id]['photos']) >= 10:
                update.message.reply_text("You have already submitted the maximum number of media.")
                return
            video = update.message.video

            if video.file_size > MAX_FILE_SIZE_BYTES:
                update.message.reply_text("Sorry, the video size is too large. Please send a svideo of up to 10MB size")
                return

            video_file = video.get_file()

            file_path = f"{video_file.file_id}.mp4"

            num_pht = len(user_info_dct[chat_id]['photos'])+1
            video_file.download(file_path)
            user_info_dct[chat_id]['photos'].append(file_path)   
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton(f"Submit Photo {num_pht}", callback_data=f"submit_{num_pht}"),
                InlineKeyboardButton("Finish", callback_data="done_ph")]
            ])
            
            user_info_dct[chat_id]['user_flags']['photo_appends']=False
            update.message.reply_text("Video received and saved!", reply_markup=reply_markup)
    
        

def photo_handler(update, context):
    global user_info_dct    
    chat_id = update.effective_chat.id
    try:
        user_id = user_info_dct[chat_id]['user_id']
    except KeyError:
        user_id = None
        
    
    if user_id==None:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Bot was restarted, press /start to authenicate")
    else:
        
        
        if user_info_dct[chat_id]['user_flags']['photo_appends']:
            if len(user_info_dct[chat_id]['photos']) >= 10:
                update.message.reply_text("You have already submitted the maximum number of media.")
                return

            photo = update.message.photo[-1]

            filename = f"{photo.file_id}.jpg"

            save_path = filename

            photo.get_file().download(save_path)

            user_info_dct[chat_id]['photos'].append(save_path)    
            num_pht = len(user_info_dct[chat_id]['photos'])+1
            
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton(f"Submit Photo {num_pht}", callback_data=f"submit_{num_pht}"),
                InlineKeyboardButton("Finish", callback_data="done_ph")]
            ])
            update.message.reply_text("Photo submitted successfully.", reply_markup=reply_markup)
            
            user_info_dct[chat_id]['user_flags']['photo_appends']=False
       
       
def send_photos_and_text(update, context):
    global user_info_dct    
    chat_id = update.effective_chat.id
    try:
        user_id = user_info_dct[chat_id]['user_id']
    except KeyError:
        user_id = None
        
    if user_id==None:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Bot was restarted, press /start to authenicate")
    else:   
        chat_id = update.effective_chat.id
        
        
        media = [InputMediaPhoto(open(photo_path, 'rb')) for photo_path in user_info_dct[chat_id]['photos']]

        text = "\n".join(user_info_dct[chat_id]['descriptions'])+"\n"
        if len(user_info_dct[chat_id]['tags'])>0:
            text+=f"Tags: {user_info_dct[chat_id]['tags']}"

        if len(media) >0:
            context.bot.send_media_group(chat_id=update.effective_chat.id, media=media)

        if text=='\n':
            text = "No description or tags provided for current post yet"
        context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.MARKDOWN)


 
def review_db(update, context):
    global user_info_dct    
    chat_id = update.effective_chat.id
    try:
        user_id = user_info_dct[chat_id]['user_id']
    except KeyError:
        user_id = None
        
    if not user_id:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Bot was restarted, press /start to authenticate") 
    else:

        chat_id = update.effective_chat.id

        context.bot.send_message(chat_id=chat_id, text=f'PUBLIC DB, WHOLE:')
        response = requests.get(URL_ALL_POSTS)
        if response.status_code == 200:
            context.bot.send_message(chat_id=chat_id, text=f'Preparing posts...')
        else:
            text = f"Request failed with status code: {response.status_code}"
            context.bot.send_message(chat_id=chat_id, text=text)
            
        for i in range(len(response.json())):
            send_post(update, context, response.json()[i][0], public_db=True)
        help(update, context)
        
    
    return 'ok'
 
     
def send_post(update, context, dct, public_db=False):
    
    global user_info_dct    
    chat_id = update.effective_chat.id
    try:
        user_id = user_info_dct[chat_id]['user_id']
    except KeyError:
        user_id = None
        
    if not user_id:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Bot was restarted, press /start to authenticate") 
    else:

        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Post with ID {dct['id']} \/\/\/\/\/\/\/\/\/")
        media = []
        if dct["photos"]:
            media += [InputMediaPhoto(open('media/'+photo_path, 'rb')) for photo_path in dct["photos"].split(',')]
        if dct["video"]:
            media += [InputMediaVideo(open('media/'+photo_path, 'rb')) for photo_path in dct["video"].split(',')]
            
        text = dct["description"]+"\n"
        if dct["tags"]:
            text+=f"Tags: {dct['tags']}"

        if len(media) >0:
            context.bot.send_media_group(chat_id=update.effective_chat.id, media=media)

        if text=='\n' or len(text)==0:
            text = "No description or tags provided for current post yet"
        if not public_db:
            context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.MARKDOWN)
        else:
            reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Delete", callback_data=f"delete_public_{dct['id']}")]
            ])
            context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)


if __name__=="__main__":
    updater = Updater(token=telegram_bot_token, use_context=True)

    dispatcher = updater.dispatcher       
    
    for admin_id in admin_ids:
        
        
        dispatcher.add_handler(CommandHandler("admin_only_helth_check", admin_only_helth_check, Filters.user(user_id=admin_id)))
        dispatcher.add_handler(CommandHandler("start_new_post", start_new_post, Filters.user(user_id=admin_id)))
        
        dispatcher.add_handler(CallbackQueryHandler(button_callback))

        dispatcher.add_handler(CommandHandler("done", done))

    dispatcher.add_handler(CallbackQueryHandler(button_callback))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_description))
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("search_by_tag", search_by_tag))
    dispatcher.add_handler(CommandHandler("search_by_description", search_by_description))
    dispatcher.add_handler(MessageHandler(Filters.video, handle_video))
    dispatcher.add_handler(MessageHandler(Filters.photo, photo_handler))


    updater.start_polling()