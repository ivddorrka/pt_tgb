import requests

url = 'http://127.0.0.1:5000/admin/create_post/'

# The data to be sent in the request
data = {
    'description': 'YourXXX post description',
    'tags': 'tag1,tag2,tag3',
}

# Files to be uploaded (photos and video)

# files = {
#     'photos': 
#         ('photo1.jpg', open('media/0057.jpg', 'rb'), 'image/jpeg'),
#         # ('photo1.jpg', open('media/0139.jpg', 'rb'), 'image/jpeg'),
#         # Add more photos here as needed
#     # ,
#     'video': ('video.mp4', open('/home/mrs/Pictures/cool_video1.mp4', 'rb'), 'video/mp4'),
# }


# files = {
#     'photos': [
#         ('photo1.jpg', open('media/0057.jpg', 'rb'), 'image/jpeg'),
#         ('photo2.jpg', open('media/0139.jpg', 'rb'), 'image/jpeg'),
#         # Add more photos here as needed
#     ],
#     # 'video': ('video.mp4', open('path_to_video.mp4', 'rb'), 'video/mp4'),
# }


multiple_files = [('photos', ('media/0057.jpg', open('media/0057.jpg', 'rb'), 'image/jpeg')),
                      ('photos', ('media/0139.jpg', open('media/0139.jpg', 'rb'), 'image/jpeg')),
                      
                      ('video', ('cool_video1.mp4', open('/home/mrs/Pictures/cool_video1.mp4', 'rb'), 'video/mp4'))]
# r = requests.post(url, files=multiple_files)

# Send the POST request with files and data
response = requests.post(url, data=data, files=multiple_files)

# Check the response status
if response.status_code == 200:
    print('Post created successfully!')
else:
    print('Failed to create the post.')
