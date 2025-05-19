# TastyTrack - Food Discovery Web App

## Overview
TastyTrack is a web application that helps users find nearby restaurants, search for food using images, and explore restaurant collections. It integrates restaurant data and provides an intuitive way to discover new places to eat.

## Features
- **Find Nearby Restaurants** – Users can search for restaurants near their location.
- **Image-Based Search** – Users can upload images of food to find similar dishes.
- **Restaurant Listings** – Displays a list of restaurants with details like name, location, and cuisine.
- **Restaurant Details** – View restaurant-specific information, including ratings and menu.
- **Dataset Integration** – Uses real restaurant data from Zomato for enhanced recommendations.

## Project Structure
```
webapp-jhansi/
│── app.py                    # Main Flask application
│── addjson.py                # Processes JSON data
│── data.py                   # Handles data operations
│── requirements.txt          # Lists project dependencies
│── .env                      # Stores environment variables
│── static/
│   └── food.png              # Static assets like images
│── templates/
│   ├── index.html            # Homepage
│   ├── image_search.html     # Search by image page
│   ├── nearby_search.html    # Find nearby restaurants
│   ├── restaurant_list.html  # Display list of restaurants
│   ├── restaurant_detail.html# Detailed restaurant view
│── zomato/
│   ├── zomato.csv            # Raw restaurant dataset
│   ├── merged.json           # Pre-processed dataset
│   ├── Country-Code.xlsx     # Reference for country codes
│   ├── Genre Classification Dataset/  # Additional dataset files
```

## Installation
### Prerequisites
- Python 3.x installed
- Flask and required dependencies

### Steps to Set Up
1. **Clone the Repository:**
   ```sh
   git clone https://github.com/your-repo/tastytrack.git
   cd tastytrack
   ```
2. **Install Dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Set Up Environment Variables:**
   - Create a `.env` file and configure API keys if required.
4. **Run the Application Locally:**
   ```sh
   python app.py
   ```
5. **Access the Web App:** Open `http://127.0.0.1:5000` in your browser.

## Deployment on Render
### Steps to Deploy
1. **Create a Render Account:**
   - Sign up at [Render](https://render.com/).
2. **Create a New Web Service:**
   - Select `+ New` → `Web Service`.
3. **Connect GitHub Repository:**
   - Link your GitHub repository containing the TastyTrack project.
4. **Set Up Environment Variables:**
   - Add necessary environment variables as per `.env`.
5. **Specify Build Command:**
   ```sh
   pip install -r requirements.txt
   ```
6. **Specify Start Command:**
   ```sh
   python app.py
   ```
7. **Deploy and Monitor:**
   - Click `Deploy` and wait for Render to set up the application.
   - Access the live URL provided by Render.

## Technologies Used
- **Backend:** Flask (Python)
- **Frontend:** HTML, CSS, JavaScript
- **Datasets:** Zomato restaurants datasets (CSV, JSON)
- ****Database** supabase



