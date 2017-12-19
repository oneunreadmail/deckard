**0. Users**  
A user is a human being (hopefully) registered in the system, authenticated by their login and password.
An administrator is a user with special privileges.

**1. Blogs**  
The platform consists of blogs, which are logical groups of posts. Only an administrator can create, update or delete blogs.

**2. Contributors**  
A blog can have many authors among users, which are called blog contributors. Any contributor can update a blog (e.g., change its name). 

**3. Posts**  
A user can create a post in a blog if he is this blog's contributor.

Users with contributing rights to the blog are considered as this post contributors. As a post contibutor, the user can modify the post's title, text, upload or delete images, or hide the whole post.

A post can be pinned, in this case it appears at the top of the blog feed.

A post can be created in a blog unpublished. Unblished posts are called drafts.

**4. Reposts**  
A contributor to a blog can do reposts from other blogs to this blog. If blog S contains post 1, any contributor of blog D can make a repost of post 1 to blog D. After that post 1 appears in both blogs S and D. Source blog (blog S) is indicated as the source when post 1 is seen in blog D feed. Post pinning works independently in blogs S and D.

**5. Comments**  
Any user can leave a comment to a post. Comments cannot be modified or deleted by users. Comments can not contain images. Any user can leave a comment to another comment.

**6. Ratings**  
Any user can rate a post or a comment by giving it +1 or -1 points. Ratings can be changed.

**7. Visibility**  
Anyone can see any published and not hidden posts in a feed with all their comments. Draft posts are seen only by their contributors (marked as draft). Hidden posts cannot be seen by anyone.