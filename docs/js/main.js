console.log("PantryVision frontend loaded");

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', () => {
    // Get overlay and box elements
    const overlay = document.getElementById("overlay");
    const box = document.getElementById("box");
    
    if (!overlay || !box) {
        console.error("Overlay or box element not found!");
        return;
    }
    
    // Set initial state (as strings)
    overlay.style.opacity = '0';
    overlay.style.backdropFilter = 'blur(0px)';
    
    // Add animation: Fade in and blur the background
    requestAnimationFrame(() => {
        box.style.transition = 'background-color 1s ease-out';
        box.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
        overlay.style.opacity = '1'
        overlay.style.transition = 'backdrop-filter 1s ease-out';
        overlay.style.opacity = '0.5';
        overlay.style.backdropFilter = 'blur(50px)';
    });
});
// // Add click event listener to overlay
// overlay.addEventListener("click", () => {
//     overlay.style.transition = "opacity 0.3s ease, backdrop-filter 0.3s ease";
//     overlay.style.opacity = 0;
//     overlay.style.backdropFilter = "blur(0px)";
// });
