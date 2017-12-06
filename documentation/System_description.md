0. A user is a human being (hopefully) registered in the system, authenticated by their login and password.

1. The platform consists of blogs, which are logical groups of posts. A blog can have many authors among users, which are called blog contributors.  
>Q:  
a - Can any user create a blog?  
b - Can any user (or any contributor) update a blog (e.g., change its name)?  
c - Can any user (or any contributor) delete a blog?  

2. A user can create a post in a blog if he is this blog's contributor. As an author, he can modify the post's title, text, upload or delete images, or delete the whole post. Posts can contain images.

3. Any user can leave a comment to a post. As an author, he can modify or delete his comment. When a post is deleted, all its comments are deleted. Comments can not contain images.

4. Any user can leave a comment to another comment. When a parent comment is deleted, it's marked as deleted and it's content is not displayed, but all child comments are visible.

5. Any user can 'like' a post or a comment. Likes can be removed.

6. A contributor to a blog can do reposts from other blogs to this blog. If blog A contains post 1, any contributor of post B can make a repost of post 1 to blog 2. Post 2 is created, which is a copy of post 1. The additional information about repost author id is stored in post 2.  
>Q:  
  a - Are likes and comments copied?  
  b - Who can edit post 2?  
  c - What happens with post 1 if someone comments or likes post 2?  
