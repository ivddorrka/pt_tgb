from flsk_stp import Post, app
import requests

def get_post_by_id(post_id):
    post = Post.query.get(post_id)
    return post





def get_all_post_ids():
    with app.app_context():
        post_ids = []
        posts = Post.query.all()
        for post in posts:
            post_ids.append(post.id)
        return post_ids

if __name__ == '__main__':
    all_ids = get_all_post_ids()
    print(all_ids)
    
    
with app.app_context():
    post_id = 12
    post = get_post_by_id(post_id)

    if post:
        # The post with the given ID was found
        print(f"Post ID: {post.id}")
        print(f"Description: {post.description}")
        print(f"Tags: {post.tags}")
        print(f"Photos: {post.photos}")
        print(f"Video: {post.video}")
    else:
        # No post found with the given ID
        print(f"No post found with ID: {post_id}")
        

def delete_post_by_id(post_id):
    url = f'http://127.0.0.1:5000/admin/delete_post/{post_id}'
    
    # Send the DELETE request
    response = requests.delete(url)

    # Check the response status
    if response.status_code == 200:
        print(f'Post with ID {post_id} deleted successfully!')
    else:
        print(f'Failed to delete post with ID {post_id}.')

if __name__ == '__main__':
    # Example usage: Delete the post with ID = 1
    post_id = 12
    delete_post_by_id(post_id)