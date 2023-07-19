from telegram import Update,InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
import os, copy, requests
from flsk_stp import Post, app, db

url = 'http://127.0.0.1:5000/admin/create_post/'
photos = []
videos = []
tags = []
descriptions = []
ready_db = []
draft_db = []
current_post = []

def add_photos(update, context):

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Submit Photo 1", callback_data="submit_1")]
    ])
    context.bot.send_message(chat_id=update.effective_chat.id, text="Please submit up to 5 photos", reply_markup=reply_markup)


def delete_whole_post(update, context):
    current_post.clear()
    
    photos.clear()
    videos.clear()
    tags.clear()
    descriptions.clear()
    return 'ok'

def done(update, context):
    if len(descriptions)!=0 or len(tags)!=0 or len(photos)!=0 or len(videos)!=0:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"{current_post}")
        data = {
        'description': " ".join(descriptions),
        'tags': " ".join(tags),
        }   
        

        pht_paths = []
        num_ph = 0
        for i in photos:
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"I = {i}")
            num_ph+=1
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"SPLITTED = {i.split('.')[-1]}")
            if i.split('.')[-1]=="png":
                tuple_ph = ('photos', (f'{i}.png', open(i, 'rb'), 'image/png'))
            elif i.split('.')[-1]=="jpg" or i.split('.')[-1]=="jpeg":
                tuple_ph = ('photos', (f'{i}.jpg', open(i, 'rb'), 'image/jpeg'))
            else:
                tuple_ph = ('video', (f'{i}.mp4', open(i, 'rb'), 'image/mp4'))
            
            pht_paths.append(tuple_ph)
            
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"pht_paths = {pht_paths}")
            
        response = requests.post(url, data=data, files=pht_paths)

        current_post.clear()
        
        photos.clear()
        videos.clear()
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
    chat_id = update.effective_chat.id
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
    dct_for_post = {"photos": [], "videos":[], "description":[], "tags":[]}
    dct_for_post["photos"] = copy.deepcopy(photos)
    dct_for_post["description"] = copy.deepcopy(descriptions)
    dct_for_post["tags"] = copy.deepcopy(tags)
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Add to PublicDB", callback_data="add_cp_to_PublicDB")],
         [InlineKeyboardButton("Delete Whole Post", callback_data="delete_whole_p")]
    ])
    
    current_post.append(dct_for_post)
    
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Finished Post{dct_for_post}", reply_markup=reply_markup)
    
    
def review_db(update, context):
    with app.app_context():
        posts = Post.query.all()
    
    for draft_p in posts:
        id = draft_p.id
        photos_p = draft_p.photos
        videos_p = draft_p.video
        description = draft_p.description
        tagss_p = draft_p.tags
        
        
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"\n\nPost {id}\n\n \/\/\/\/\/\/\/\/\/\/\/\/\/\/\/")
        photos_p = []
        if photos_p:
            photos_p = photos_p.split(',') 
        if videos_p:
            photos_p += videos_p.split(',')
        media = [InputMediaPhoto(open('media'+'/'+photo_path, 'rb')) for photo_path in photos_p]

        text = description
        if len(tagss_p)>0:
            text  += "\n\n"+f"Tags: {', '.join(tagss_p.split()[:-1])}"+f"{tagss_p.split()[-1]}"

        if len(media) >0:
            context.bot.send_media_group(chat_id=update.effective_chat.id, media=media)
        
        
        reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Delete", callback_data=f"delete_public_{id}")]
        ])
        
        if len(text)==0:
            text="No description or tags provided"
        context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
        
            
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Start New Post", callback_data="st_new_post")],
         [InlineKeyboardButton("Help", callback_data="help_post")]
    ])
    context.bot.send_message(chat_id=update.effective_chat.id, text="These're all available posts so far", reply_markup=reply_markup)    