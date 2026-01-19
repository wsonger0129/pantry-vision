console.log("PantryVision frontend loaded");

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', () => {
    // Get overlay
    const overlay = document.getElementById("overlay");
    
    if (!overlay) {
        console.error("Overlay element not found!");
        return;
    }
    
    // Set initial state (as strings)
    overlay.style.opacity = '0';
    overlay.style.backdropFilter = 'blur(0px)';
    
    // Add animation: Fade in and blur the background
    requestAnimationFrame(() => {
        overlay.style.transition = 'opacity 0.5s ease-out, backdrop-filter 0.5s ease-out';
        overlay.style.opacity = '0.5';
        overlay.style.backdropFilter = 'blur(10px)';
    });
});

// // Add click event listener to overlay
// overlay.addEventListener("click", () => {
//     overlay.style.transition = "opacity 0.3s ease, backdrop-filter 0.3s ease";
//     overlay.style.opacity = 0;
//     overlay.style.backdropFilter = "blur(0px)";
// });