from telegram import Update,InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, ParseMode, InputMediaVideo
import copy, requests

# URL_CREATE_POST = f'http://127.0.0.1:5000/admin/create_post?{user_id}'
user_info_dct = {}
# photos = []
# tags = []
# descriptions = []
# current_post = []

def add_photos(update, context):
    # part of s callback for photo-submission
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Submit Photo 1", callback_data="submit_1")]
    ])
    context.bot.send_message(chat_id=update.effective_chat.id, text="Please submit photos following the instructions", reply_markup=reply_markup)


def delete_whole_post(update, context):
    global user_info_dct    
    chat_id = update.effective_chat.id
    try:
        user_id = user_info_dct[chat_id]['user_id']
    except KeyError:
        user_id = None
        
    if not user_id:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Bot was restarted, press /start to authenticate") 
    else:

        # part of a callback to make a delete-request to db to delete a post (admin accessed)
        user_info_dct[chat_id]['current_post'].clear()
        user_info_dct[chat_id]['photos'].clear()
        user_info_dct[chat_id]['tags'].clear()
        user_info_dct[chat_id]['descriptions'].clear()
        return 'ok'

def done(update, context, user_id):
    global user_info_dct    
    chat_id = update.effective_chat.id
    try:
        user_id = user_info_dct[chat_id]['user_id']
    except KeyError:
        user_id = None
        
    if not user_id:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Bot was restarted, press /start to authenticate") 
    else:
        # description_user = user_info_dct[chat_id]['user_flags']['description_user']
        # tags_user = user_info_dct[chat_id]['user_flags']['tags_user']
        # description_appends= user_info_dct[chat_id]['user_flags']['description_appends']
        # description_changes=user_info_dct[chat_id]['user_flags']['description_changes']
        # # photo_appends=user_info_dct[chat_id]['user_flags']['photo_appends']
        # tags_append=user_info_dct[chat_id]['user_flags']['tags_append']
        descriptions=user_info_dct[chat_id]['descriptions']
        photos= user_info_dct[chat_id]['photos']
        tags= user_info_dct[chat_id]['tags']
        current_post= user_info_dct[chat_id]['current_post']
        # part of a callback to make a submit-request to db to submit a post (admin accessed)
        if len(descriptions)!=0 or len(tags)!=0 or len(photos)!=0:
            # context.bot.send_message(chat_id=update.effective_chat.id, text=f"{current_post}")
            data = {
            'description': " ".join(descriptions),
            'tags': " ".join(tags),
            }   
            

            pht_paths = []
            num_ph = 0
            for i in photos:
                num_ph+=1
                if i.split('.')[-1]=="png":
                    tuple_ph = ('photos', (f'{i}.png', open(i, 'rb'), 'image/png'))
                elif i.split('.')[-1]=="jpg" or i.split('.')[-1]=="jpeg":
                    tuple_ph = ('photos', (f'{i}.jpg', open(i, 'rb'), 'image/jpeg'))
                else:
                    tuple_ph = ('video', (f'{i}.mp4', open(i, 'rb'), 'image/mp4'))
                
                pht_paths.append(tuple_ph)
                
            URL_CREATE_POST = f'http://127.0.0.1:5000/admin/create_post?tg_id={user_id}'
            response = requests.post(URL_CREATE_POST, data=data, files=pht_paths)

            current_post.clear()
            
            photos.clear()
            tags.clear()
            descriptions.clear()
            
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Help", callback_data=f"help_post")],
                [InlineKeyboardButton("Start New Post", callback_data=f"st_new_post")],
                [InlineKeyboardButton("Review Public DB", callback_data=f"review_public")
                ]
            ])
            
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"Saved new post to DB", reply_markup=reply_markup)
        

            
def done_ph(update, context):
    global user_info_dct    
    chat_id = update.effective_chat.id
    try:
        user_id = user_info_dct[chat_id]['user_id']
    except KeyError:
        user_id = None
        
    if not user_id:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Bot was restarted, press /start to authenticate") 
    else:
        
        descriptions=user_info_dct[chat_id]['descriptions']
        
        # part of a callback to make a submit-request to db to submit a post (admin accessed)
        args = context.args
        
        description_change = "Add description"
        if len(descriptions)>0:
            description_change = "Change description"
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Add photos", callback_data=f"add_photos")],
            [InlineKeyboardButton("Add tags", callback_data=f"add_tags")],
            [InlineKeyboardButton(description_change, callback_data=f"add_description")],
            [InlineKeyboardButton("Finish", callback_data="done_post")]
        ])
        context.bot.send_message(chat_id=chat_id, text="Submited photos saved successfully!", reply_markup=reply_markup)
    
def done_post(update, context):
    global user_info_dct    
    chat_id = update.effective_chat.id
    try:
        user_id = user_info_dct[chat_id]['user_id']
    except KeyError:
        user_id = None
        
    if not user_id:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Bot was restarted, press /start to authenticate") 
    else:
        # description_user = user_info_dct[chat_id]['user_flags']['description_user']
        # tags_user = user_info_dct[chat_id]['user_flags']['tags_user']
        # description_appends= user_info_dct[chat_id]['user_flags']['description_appends']
        # description_changes=user_info_dct[chat_id]['user_flags']['description_changes']
        # # photo_appends=user_info_dct[chat_id]['user_flags']['photo_appends']
        # tags_append=user_info_dct[chat_id]['user_flags']['tags_append']
        descriptions=user_info_dct[chat_id]['descriptions']
        photos= user_info_dct[chat_id]['photos']
        tags= user_info_dct[chat_id]['tags']
        current_post= user_info_dct[chat_id]['current_post']
        
        dct_for_post = {"photos": [], "description":[], "tags":[]}
        dct_for_post["photos"] = copy.deepcopy(photos)
        dct_for_post["description"] = copy.deepcopy(descriptions)
        dct_for_post["tags"] = copy.deepcopy(tags)
        
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Add to PublicDB", callback_data="add_cp_to_PublicDB")],
            [InlineKeyboardButton("Delete Whole Post", callback_data="delete_whole_p")]
        ])
        
        current_post.append(dct_for_post)
        
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Saved post changes", reply_markup=reply_markup)
    