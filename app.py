from flask import Flask, request, jsonify, render_template
from supabase import create_client, Client
import tensorflow as tf
from tensorflow.keras.applications.efficientnet import EfficientNetB0, preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
import numpy as np
import os,logging
from io import BytesIO
from PIL import Image
import uuid
from dotenv import load_dotenv
import logging, traceback
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import math

load_dotenv()
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

# Load MobileNetV2 for image classification 
model = EfficientNetB0(weights="imagenet")

# Food to Cuisine Mapping
cusineMapping = {
    'pizza': ['Italian', 'American'],
    'hamburger': ['American', 'Fast Food'],
    'ice cream': ['Desserts', 'Ice Cream'],
    'pasta': ['Italian', 'Continental'],
    'sushi': ['Japanese', 'Asian'],
    'curry': ['Indian', 'Thai', 'Asian'],
    'noodles': ['Chinese', 'Asian', 'Thai'],
    'sandwich': ['American', 'Fast Food'],
    'cake': ['Desserts', 'Bakery'],
    'salad': ['Healthy Food', 'Continental']
}
# Country Code to Country Name mapping
country_mapping = {
    1: "India",
    14: "Australia",
    30: "Brazil",
    37: "Canada",
    94: "Indonesia",
    148: "New Zealand",
    162: "Phillipines",
    166: "Qatar",
    184: "Singapore",
    189: "South Africa",
    191: "Sri Lanka",
    208: "Turkey",
    214: "UAE",
    215: "United Kingdom",
    216: "United States"
}

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image(image_path):
    try:
        img = tf.keras.preprocessing.image.load_img(image_path, target_size=(224, 224))

        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = tf.expand_dims(img_array, 0)
        img_array = preprocess_input(img_array)
        predictions = model.predict(img_array)
        decoded_predictions = decode_predictions(predictions)
        food_items = []
        for pred in decoded_predictions[0]:
            class_name = pred[1].lower().replace('_', ' ')
            confidence = float(pred[2])
            for food_key in cusineMapping.keys():
                if food_key in class_name:
                    food_items.append({
                        'name': food_key,
                        'confidence': confidence,
                        'cuisines': cusineMapping[food_key]
                    })
                    break
        return food_items
    except Exception as e:
        print("Error in process_image:")
        traceback.print_exc()
        return []
# HTML templates
@app.route("/")
def home():
    return render_template("index.html")
@app.route("/nearby_search")
def nearby_search():
    return render_template("nearby_search.html")
@app.route("/image_search")
def image_search():
    return render_template("image_search.html")
@app.route("/restaurant_list")
def restaurant_list():
    return render_template("restaurant_list.html")
@app.route("/restaurant/<int:restaurant_id>")
def restaurant_detail(restaurant_id):
    return render_template("restaurant_detail.html", restaurant_id=restaurant_id)
# API Endpoints
@app.route("/api/restaurant/<int:restaurant_id>", methods=["GET"])
def get_restaurant_by_id(restaurant_id):
    try:
        response = supabase.table("zomato_full_data").select("*").eq("id", restaurant_id).execute()
        if response.data:
            restaurant = response.data[0]
            restaurant["has_table_booking"] = "✅ Available" if restaurant.get("has_table_booking") else "❌ Not Available"
            restaurant["has_online_delivery"] = "✅ Yes" if restaurant.get("has_online_delivery") else "❌ No"
            restaurant["is_delivering_now"] = "✅ Yes" if restaurant.get("is_delivering_now") else "❌ No"
            restaurant["switch_to_order_menu"] = "✅ Available" if restaurant.get("switch_to_order_menu") else "❌ Not Available"

            return jsonify(restaurant), 200
        else:
            return jsonify({"error": "Restaurant not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/restaurants", methods=['GET'])
def get_restaurants():
    try:
        # Pagination Parameters
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit",9))
        offset = (page - 1) * limit

        # Filtering Parameters
        country_code = request.args.get("country_code", type=int)
        search_query = request.args.get("search", "").strip()
        avg_cost_raw = request.args.get("avg_cost")
        cuisine_filter = request.args.get("cuisine", "").strip().lower()
        avg_cost = None
        if avg_cost_raw:
            try:
                avg_cost = int(float(avg_cost_raw))
            except ValueError:
                return jsonify({"error": "Invalid average cost value"}), 400
        query = supabase.table("zomato_full_data").select("*")
        count_query = supabase.table("zomato_full_data").select("id", count="exact")  # Get exact count

        # Apply Filters
        if country_code:
            query = query.contains("location", {"country_id": country_code})  
            count_query = count_query.contains("location", {"country_id": country_code})

        if search_query:
            query = query.ilike("name", f"%{search_query}%")
            count_query = count_query.ilike("name", f"%{search_query}%")

        if avg_cost is not None:
            query = query.lte("average_cost_for_two", avg_cost)
            count_query = count_query.lte("average_cost_for_two", avg_cost)

        if cuisine_filter:
            query = query.ilike("cuisines", f"%{cuisine_filter}%")
            count_query = count_query.ilike("cuisines", f"%{cuisine_filter}%")

        count_response = count_query.execute()
        total_count = count_response.count or 0
        total_pages = max(1, math.ceil(total_count / limit))


        query = query.range(offset, offset + limit)
        response = query.execute()



        return jsonify({
            "restaurants": response.data or [],
            "page": page,
            "total_pages": total_pages,
            "total_count": total_count
        }), 200

    except Exception as e:
        print("[ERROR] API Failure:", traceback.format_exc()) #callback function
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/api/cuisines", methods=["GET"])
def get_cuisines():
    try:
        response = supabase.table("zomato_full_data").select("cuisines").execute()
        all_cuisines = set()
        for restaurant in response.data:
            cuisines = restaurant.get("cuisines", "")
            if cuisines:
                for cuisine in cuisines.split(","):
                    all_cuisines.add(cuisine.strip())

        return jsonify({"cuisines": sorted(all_cuisines)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/restaurants/nearby", methods=['GET'])
def get_nearby_restaurants():
    try:
        location = request.args.get("location")
        lat = request.args.get("lat")
        lon = request.args.get("lon")
        radius = float(request.args.get("radius", 3))  
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit",9))
        offset = (page - 1) * limit

        # Log the received parameters
        app.logger.info(f"Received location: {location}, lat: {lat}, lon: {lon}, radius: {radius}")

        if location:
            geocoder = Nominatim(user_agent="restaurant_finder_app")
            location_data = geocoder.geocode(location)
            if not location_data:
                return jsonify({"error": "Location not found"}), 404
            lat = location_data.latitude
            lon = location_data.longitude

        try:
            lat = float(lat)
            lon = float(lon)
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid coordinates"}), 400

        # Log the coordinates being used
        app.logger.info(f"Using coordinates - lat: {lat}, lon: {lon}")

        lat_margin = 0.5  
        lon_margin = 0.5  

        query = supabase.table("zomato_full_data")\
    .select("*, location->>latitude AS latitude, location->>longitude AS longitude")\
    .gte("location->>latitude", str(lat - lat_margin))\
    .lte("location->>latitude", str(lat + lat_margin))\
    .gte("location->>longitude", str(lon - lon_margin))\
    .lte("location->>longitude", str(lon + lon_margin))

        response = query.execute()
        if not response.data:
            return jsonify({"error": "No restaurants found in this area"}), 404

        nearby_restaurants = []
        for restaurant in response.data:
            try:
                rest_lat = float(restaurant["location"]["latitude"])
                rest_lon = float(restaurant["location"]["longitude"])
                distance = geodesic((lat, lon), (rest_lat, rest_lon)).kilometers
                if distance <= radius:
                    restaurant["distance"] = round(distance, 2)
                    nearby_restaurants.append(restaurant)
            except (ValueError, TypeError) as e:
                continue

        nearby_restaurants.sort(key=lambda x: x["distance"]) 

        total_count = len(nearby_restaurants)
        total_pages = max(1, math.ceil(total_count / limit))
        paginated_restaurants = nearby_restaurants[offset:offset + limit]

        return jsonify({
            "restaurants": paginated_restaurants,
            "page": page,
            "total_pages": total_pages,
            "total_restaurants": total_count,
            "search_location": {
                "latitude": lat,
                "longitude": lon,
                "radius_km": radius
            }
        })
    except Exception as e:
        app.logger.error(f"Error in get_nearby_restaurants: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/api/restaurants/search-by-image", methods=['POST'])
def search_restaurants_by_image():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        file = request.files['image']
        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type"}), 400

        img_path = "temp_image.jpg"
        file.save(img_path)

        food_items = process_image(img_path)
        
        if not food_items:
            return jsonify({"status": "success", "message": "No matching cuisine found.", "restaurants": []}), 200

        detected_cuisines = set()
        for item in food_items:
            for cuisine in item.get('cuisines', []):
                detected_cuisines.add(cuisine.lower().strip())

        response = supabase.table("zomato_full_data").select("*").execute()
        if not response.data:
            return jsonify({"status": "success", "message": "No restaurants available in database.", "restaurants": []}), 200

        matching_restaurants = []
        for restaurant in response.data:
            cuisines_str = restaurant.get("cuisines") or ""
            restaurant_cuisines = [c.strip().lower() for c in cuisines_str.split(",") if c.strip()]
            if any(c in restaurant_cuisines for c in detected_cuisines):
                matching_restaurants.append(restaurant)

        page = int(request.args.get("page", 1) or 1)
        limit = int(request.args.get("limit", 9) or 9)

        offset = (page - 1) * limit
        total_matches = len(matching_restaurants)
        total_pages = max(1, -(-total_matches // limit)) 

        paginated_restaurants = matching_restaurants[offset:offset + limit]
        if not response or not response.data:
            return jsonify({"status": "success", "message": "No restaurants available in database.", "restaurants": []}), 200

        return jsonify({
            "status": "success",
            "detected_cuisines": list(detected_cuisines),
            "restaurants": paginated_restaurants,
            "page": page,
            "total_pages": total_pages
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)


