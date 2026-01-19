console.log("PantryVision frontend loaded");

// Get overlay
const overlay = document.getElementById("overlay");

// Set initial state
overlay.style.opacity = 0;
overlay.style.backdropFilter = "blur(0px)";

// Add animation: Fade in and blur the background
requestAnimationFrame(() => {
    overlay.style.transition = "opacity 0.5s ease, backdrop-filter 0.5s ease";
    overlay.style.opacity = 0.5;
    overlay.style.backdropFilter = "blur(10px)";
});

// // Add click event listener to overlay
// overlay.addEventListener("click", () => {
//     overlay.style.transition = "opacity 0.3s ease, backdrop-filter 0.3s ease";
//     overlay.style.opacity = 0;
//     overlay.style.backdropFilter = "blur(0px)";
// });