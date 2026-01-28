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
        box.style.opacity = '1';
        overlay.style.transition = 'background-color 0.5s ease-out, backdrop-filter 0.5s ease-out';
        overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.1)';
        overlay.style.opacity = '1';
        overlay.style.backdropFilter = 'blur(3px)';
    });
});

// After loaded
const input = document.getElementById("input"); // Input text box
const goalText = document.getElementById("goal-text"); // Goal text
var timesInputted = 0;

input.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        console.log("Input entered: " + input.value);
        input.value = "";
        timesInputted++;
    }
    switch (timesInputted) {
    case 1:
        goalText.textContent = "what do you like? (savory, chocolate, crunchy, etc.)";
        break;
    case 2:
        goalText.textContent = "what can you absolutely not stand? (pickles, tomatoes, mushrooms, etc.)";
        break;
    case 3:
        goalText.textContent = "alright! what are you feeling right now? (big hearty meal, light snack, must have chicken, etc.)";
        break;
    case 4:
        goalText.textContent = "generating recipe... (not finished yet)";
        input.disabled = true;
        break;
    }
});