// scroll_top.js
// javascript functions for feed interactivity

// JavaScript to show/hide the button based on scroll position
window.onscroll = function() {scrollFunction()};

function scrollFunction() {
    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
        document.getElementById("scrollToTopBtn").style.display = "block"; // Show the button
    } else {
        document.getElementById("scrollToTopBtn").style.display = "none"; // Hide the button
    }
}

// Function to scroll to the top of the page
function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}