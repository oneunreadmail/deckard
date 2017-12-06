**0. Users**  
A user is a human being (hopefully) registered in the system, authenticated by their login and password.
An administrator is a user with special privileges.

**1. Blogs**  
The platform consists of blogs, which are logical groups of posts. Only an administrator can create or delete blogs.

**2. Contributors**  
A blog can have many authors among users, which are called blog contributors. Any contributor can update a blog (e.g., change its name). 
A contributor to a blog can do reposts from other blogs to this blog. If blog S contains post 1, any contributor of blog D can make a repost of post 1 to blog D. After that post 1 appears in both blogs S and D. Source blog (blog S) is indicated as the source when post 1 is seen in blog D feed.

**3. Posts and reposts**  
A user can create a post in a blog if he is this blog's contributor. Users with contributing rights to this blog are considered as this post contributors. As a post contibutor, he/she can modify the post's title, text, upload or delete images, or hide the whole post. Hidden posts do not appear in the blog.

**4. Comments**  
Any user can leave a comment to a post. Comments cannot be modified or deleted by users. When a post is hidden, all its comments become hidden as well. Comments can not contain images. Any user can leave a comment to another comment.

**5. Likes**  
Any user can 'like' a post or a comment. Likes can be removed.
Like functionality may be replaced with +1/-1 one.
