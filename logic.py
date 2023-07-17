import telegram
from telegram import Update,InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
import os
# from app import done

photos = []
tags = []
descriptions = []
ready_db = []
draft_db = []
current_post = []

# ready_posts = []
# draft_posts = []

def add_photos(update, context):
    # photos.clear()

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Submit Photo 1", callback_data="submit_1")]
    ])
    # update.message.reply_text("Please submit up to 3 photos.", reply_markup=reply_markup)
    # reply_markup=inline_keyboard
    context.bot.send_message(chat_id=update.effective_chat.id, text="Please submit up to 5 photos", reply_markup=reply_markup)



def done(update, context, which_db):
    if which_db=="ready":
        ready_db.append(current_post[0])
    elif which_db=="draft":
        draft_db.append(current_post[0])
    
    current_post.clear()
    
    photos.clear()
    tags.clear()
    descriptions.clear()
    
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Added post to {which_db} database")
    # start_new_post(update, context)
    
def done_ph(update, context):
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
    context.bot.send_message(chat_id=chat_id, text="Submited photos saved successfully!", reply_markup=reply_markup)

def done_post(update, context):
    dct_for_post = {"photos": [], "videos":[], "description":[], "tags":[]}
    dct_for_post["photos"] = photos
    dct_for_post["description"] = descriptions
    dct_for_post["tags"] = tags
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Add to Ready", callback_data="add_cp_to_readyDB"),
         InlineKeyboardButton("Add to Draft", callback_data="add_cp_to_draftDB")]
    ])
    
    current_post.append(dct_for_post)
    
    context.bot.send_message(chat_id=update.effective_chat.id, text="Finished Post", reply_markup=reply_markup)
    
    
        
def handle_description(update, context):
    description = update.message.text

    # Add the description to the list
    descriptions.append(description)

    # Reply with a confirmation message
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Save", callback_data="save_desc_to_cp"),
         InlineKeyboardButton("Append more", callback_data="append_desc"),
         InlineKeyboardButton("Write a new one", callback_data="new_desc"),
         InlineKeyboardButton("Delete", callback_data="delete_desc")]
    ])
    
    update.message.reply_text(f"Description added: {description}")

def photo_handler(update, context):
    if len(photos) >= 5:
        update.message.reply_text("You have already submitted the maximum number of photos.")
        return

    photo = update.message.photo[-1]

    filename = f"{photo.file_id}.jpg"

    save_path = os.path.join("photo_files", filename)

    photo.get_file().download(save_path)

    photos.append(save_path)    
    num_pht = len(photos)+1
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Submit Photo {num_pht}", callback_data=f"submit_{num_pht}"),
         InlineKeyboardButton("Finish", callback_data="done_ph")]
    ])
    update.message.reply_text("Photo submitted successfully.", reply_markup=reply_markup)
