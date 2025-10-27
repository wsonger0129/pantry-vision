# PantryVision

## 🧠 Overview
**PantryVision** is an intelligent kitchen assistant that helps users automatically track their groceries, suggest recipes based on available ingredients, and minimize food waste. It uses **computer vision** to recognize items in your fridge or pantry and integrates with a **database and AI agent** to provide personalized recipe and shopping suggestions.

## 🎯 Goal
The goal of PantryVision is to create a smart, hands-free inventory management system for the kitchen. It aims to:
- Detect and track grocery items using AI-powered video processing that observes what users place into or remove from the fridge, updating the inventory automatically.
- Store and manage user inventory data to create better recommendations.
- Suggest recipes based on preferences, fitness goals, allergies, and available ingredients.
- Notify users of upcoming expiration dates to reduce waste.

## ⚙️ Core Technologies
In the planning stage, I may use:
- **Python** — Primary programming language.
- **OpenCV / YOLO / TensorFlow** — For object detection and image recognition.
- **SQLite / Firebase** — For storing inventory and user data.
- **LangChain / OpenAI API** — For recipe generation and intelligent meal planning.
- **FastAPI or Flask** — Backend for handling API calls and database interaction.
- **React Native (optional)** — For a mobile interface or companion app.

## 🧩 Key Features (Prototype Goals)

### 🤖 AI Recipe Agent (Available Now!)
- **Personalized Recommendations:** Get recipes based on your preferences, fitness goals, and dietary restrictions
- **Interactive Terminal Interface:** Easy-to-use command-line interface with colored output
- **Smart Profile System:** Remembers your food preferences, allergies, and fitness goals
- **Flexible Requests:** Ask for recipes in natural language ("I want meat for dinner tonight")
- **Model Selection:** Choose your preferred OpenAI model (GPT-3.5-turbo, GPT-4, GPT-4o, etc.)
- **Local Data Storage:** Save your profile and recipe history locally for future sessions
- **Complete Recipe Details:** Includes ingredients, instructions, nutrition info, prep/cook times, and source URLs

### 🔮 Future Features
1. **Image Recognition:** Detect items inside the fridge using a connected camera.
2. **Inventory Tracking:** Log items into a structured database with timestamps.
3. **Recipe Generation:** Suggest recipes based on current ingredients.
4. **Expiration Monitoring:** Estimate or extract expiration dates using barcode or OCR.
5. **User Notifications:** Alert users when items are expiring or missing for a recipe.

## 🧰 Development Setup

### Quick Start with AI Recipe Agent

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up OpenAI API Key**
   - Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
   - Copy `env.example` to `.env` and add your API key:
     ```bash
     cp env.example .env
     # Edit .env and add: OPENAI_API_KEY=your_api_key_here
     ```

3. **Configure Model and Data Storage (Optional)**
   - Edit `.env` to customize your settings:
     ```bash
     # Choose your OpenAI model
     OPENAI_MODEL=gpt-3.5-turbo  # or gpt-4, gpt-4o, gpt-4o-mini
     OPENAI_MAX_TOKENS=2000
     OPENAI_TEMPERATURE=0.7
     
     # Enable local data storage
     SAVE_USER_DATA=true
     DATA_DIR=./data
     ```

3. **Run the AI Recipe Agent**
   ```bash
   python src/main.py
   ```

4. **First Time Setup**
   - The agent will prompt you for your preferences, fitness goals, and allergies
   - After setup, you can ask for recipe recommendations like:
     - "I want meat for dinner tonight"
     - "vegetarian lunch ideas"
     - "high protein breakfast"

### Development Environment
- Start in **Python IDE** (e.g., VS Code, PyCharm, or Jupyter) for prototyping.
- Use **Google Colab** for AI model training and testing.
- Later, deploy to a **cloud platform** (e.g., AWS, Google Cloud, or Azure) for scalability.

## 🔐 License
This project is licensed under the **MIT License**, allowing others to use, modify, and distribute it with attribution.

## 📈 Future Roadmap
- Integrate receipt or barcode scanning for easier item input.
- Develop an IoT-compatible fridge camera mount for continuous monitoring.
- Implement cross-device syncing (mobile app + web dashboard).
- Introduce sustainability analytics (food waste tracking, carbon footprint).

---

Created by Whitney Songer<br>
“Less thinking, more eating!”
