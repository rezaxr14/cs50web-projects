document.addEventListener('DOMContentLoaded', () => {
    // Add event listener for submitting a new post
    const newPostForm = document.querySelector("#sendNewPost");
    if (newPostForm) {
        newPostForm.addEventListener("click", () => {
            fetch("/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken()
                },
                body: JSON.stringify({
                    newPost: document.getElementById('poster').value
                })
            }).then(() => {
                document.getElementById('poster').value = '';
                // Reload the first page to show the new post
                fetchAllPosts(1);
            });
        });
    }


    fetchAllPosts(1);
});

function fetchAllPosts(pageNumber) {
    const postsContainer = document.getElementById("posts-js");
    const paginationContainer = document.getElementById("pagination-controls");
    const currentUser = document.body.dataset.username;
    fetch(`/posts?page=${pageNumber}`)
        .then(res => res.json())
        .then(data => {
            // Clear previous posts and buttons
            postsContainer.innerHTML = "";
            paginationContainer.innerHTML = "";

            // Display the posts for the current page
            data.posts.forEach(post => {
                const postElement = document.createElement("div");
                postElement.classList.add("post", "card", "mb-3");
                postElement.innerHTML = `
                   <div class="card-body" id="post-body-${post.id}">
                        <h5 class="card-title"><a href="/user/${post.author}">${post.author}</a></h5>
                        <p class="card-text">${post.content}</p>
                        <small class="text-muted">Posted on: ${post.date_posted}</small>
                        
                        <div class="mt-2">
                            <button class="btn btn-sm like-btn ${post.is_liked_by_user ? 'btn-primary' : 'btn-outline-primary'}" data-post-id="${post.id}">
                                ${post.is_liked_by_user ? 'Unlike' : 'Like'}
                            </button>
                            <span id="like-count-${post.id}">${post.likes}</span> Likes
                        </div>
                        
                        ${
                                    post.author === currentUser ? `<button class="btn btn-sm btn-info edit-btn mt-2" data-post-id="${post.id}">Edit</button>` : ''
                        }
                    </div>
                `;
                postsContainer.appendChild(postElement);
            });
            // Add event listeners for the new Like buttons
            document.querySelectorAll('.like-btn').forEach(button => {
                button.addEventListener('click', () => {
                    const postId = button.dataset.postId;
                    fetch(`/posts/${postId}/like`, {
                        method: 'POST',
                        headers: { 'X-CSRFToken': getCSRFToken() }
                    })
                    .then(response => response.json())
                    .then(result => {
                        // Update like count and button style
                        const likeCountSpan = document.getElementById(`like-count-${postId}`);
                        likeCountSpan.innerText = result.like_count;

                        if (result.is_liked) {
                            button.innerText = 'Unlike';
                            button.classList.remove('btn-outline-primary');
                            button.classList.add('btn-primary');
                        } else {
                            button.innerText = 'Like';
                            button.classList.remove('btn-primary');
                            button.classList.add('btn-outline-primary');
                        }
                    });
                });
            });
            // After the loop, add event listeners for the new Edit buttons
            document.querySelectorAll('.edit-btn').forEach(button => {
                button.addEventListener('click', () => {
                    const postId = button.dataset.postId;
                    editPost(postId);
                });
            });


            // Create pagination buttons
            const paginationList = document.createElement('ul');
            paginationList.classList.add('pagination');

            // "Previous" button
            const prevLi = document.createElement('li');
            prevLi.classList.add('page-item');
            if (data.has_previous) {
                const prevLink = document.createElement('a');
                prevLink.classList.add('page-link');
                prevLink.href = '#';
                prevLink.innerText = 'Previous';
                prevLink.addEventListener('click', (e) => {
                    e.preventDefault();
                    fetchAllPosts(data.previous_page_number);
                });
                prevLi.appendChild(prevLink);
            } else {
                prevLi.classList.add('disabled');
                prevLi.innerHTML = `<span class="page-link">Previous</span>`;
            }
            paginationList.appendChild(prevLi);

            // "Next" button
            const nextLi = document.createElement('li');
            nextLi.classList.add('page-item');
            if (data.has_next) {
                const nextLink = document.createElement('a');
                nextLink.classList.add('page-link');
                nextLink.href = '#';
                nextLink.innerText = 'Next';
                nextLink.addEventListener('click', (e) => {
                    e.preventDefault();
                    fetchAllPosts(data.next_page_number);
                });
                nextLi.appendChild(nextLink);
            } else {
                nextLi.classList.add('disabled');
                nextLi.innerHTML = `<span class="page-link">Next</span>`;
            }
            paginationList.appendChild(nextLi);

            paginationContainer.appendChild(paginationList);
        })
        .catch(error => {
            console.error("Error fetching posts:", error);
            postsContainer.innerHTML = "<p>Failed to load posts.</p>";
        });
}

function getCSRFToken() {
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + '=')) {
            return decodeURIComponent(cookie.substring(name.length + 1));
        }
    }
    return null;
}
function editPost(postId) {
    const postBody = document.getElementById(`post-body-${postId}`);
    const postContent = postBody.querySelector('.card-text');
    const originalContent = postContent.innerText;

    postBody.innerHTML = `
        <textarea class="form-control" id="textarea-${postId}">${originalContent}</textarea>
        <button class="btn btn-sm btn-success mt-2 save-btn" data-post-id="${postId}">Save</button>
        <button class="btn btn-sm btn-secondary mt-2 cancel-btn" data-post-id="${postId}">Cancel</button>
    `;

    // Add event listener for the Save button
    postBody.querySelector('.save-btn').addEventListener('click', () => {
        const newContent = document.getElementById(`textarea-${postId}`).value;
        fetch(`/posts/${postId}`, {
            method: 'PUT',
            headers: { 'X-CSRFToken': getCSRFToken(), 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: newContent })
        })
        .then(response => {
            if (response.ok) {
                fetchAllPosts(1);
            }
        });
    });

    // Add event listener for the Cancel button
    postBody.querySelector('.cancel-btn').addEventListener('click', () => {
        fetchAllPosts(1);
    });
}