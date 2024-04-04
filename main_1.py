import streamlit as st
import mysql.connector

# Function to authenticate user credentials from the database
def authenticate_user(username, password):
    try:
        # Connect to the MySQL database
        connection = mysql.connector.connect(
            host="sql6.freemysqlhosting.net",
            database="sql6695317",
            user="sql6695317",
            password="xWY2aLxsMw"
        )

        # Create a cursor object to execute SQL queries
        cursor = connection.cursor()

        # Query to check if the username and password match
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()  # Fetch the first row

        # If user exists, return True (authentication successful)
        if user:
            return True
        else:
            return False

    except mysql.connector.Error as error:
        st.error(f"Error: {error}")
        return False

    finally:
        # Close the cursor and database connection
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

# Define your login function
def login():
    st.header("Login Page")
    # Add your login code here
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        # Authenticate user with provided credentials
        if authenticate_user(username, password):
            st.session_state.logged_in = True
            st.query_params["page"] = "Dashboard"  # Redirect to dashboard
            st.success("Login successful!")
        else:
            st.error("Invalid username or password")

# Define your registration function
def register():
    st.header("Registration Page")
    # Add your registration code here
    # For now, let's assume registration is not implemented
    st.warning("Registration functionality is not implemented yet.")

# Define function to show dashboard content
def show_dashboard():
    st.header("Dashboard")
    # Add your content here
    st.write("Welcome to the dashboard!")

    # You can add more content or functionality here

    # Add your website code here using an iframe
    st.write("Embedded Website:")
    st.markdown('<iframe src="https://example.com" width="1000" height="600"></iframe>', unsafe_allow_html=True)


# Main Streamlit app
def main():
    ##Give title to the app
    st.title("Fashion Recommender System")

    import os
    from PIL import Image
    import numpy as np
    import pickle
    import tensorflow
    from tensorflow.keras.preprocessing import image
    from tensorflow.keras.layers import GlobalMaxPooling2D
    from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
    from sklearn.neighbors import NearestNeighbors
    from numpy.linalg import norm

    # Import Chatbot class
    from chatbot import Chatbot

    # Initialize the chatbot
    chatbot = Chatbot()

    feature_list = np.array(pickle.load(open('embeddings.pkl', 'rb')))
    filenames = pickle.load(open('filenames.pkl', 'rb'))

    # Load ResNet model for image feature extraction
    model = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    model.trainable = False
    model = tensorflow.keras.Sequential([
        model,
        GlobalMaxPooling2D()
    ])

    # Function to save uploaded file
    def save_uploaded_file(uploaded_file):
        try:
            with open(os.path.join('uploads', uploaded_file.name), 'wb') as f:
                f.write(uploaded_file.getbuffer())
            return True
        except:
            return False

    # Function for feature extraction
    def feature_extraction(img_path, model):
        img = image.load_img(img_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        expanded_img_array = np.expand_dims(img_array, axis=0)
        preprocessed_img = preprocess_input(expanded_img_array)
        result = model.predict(preprocessed_img).flatten()
        normalized_result = result / norm(result)
        return normalized_result

    # Function for recommendation
    def recommend(features, feature_list):
        neighbors = NearestNeighbors(n_neighbors=6, algorithm='brute', metric='euclidean')
        neighbors.fit(feature_list)
        distances, indices = neighbors.kneighbors([features])
        return indices

    # File upload section
    uploaded_file = st.file_uploader("Choose an image")
    if uploaded_file is not None:
        if save_uploaded_file(uploaded_file):
            # Display the uploaded image
            display_image = Image.open(uploaded_file)
            st.image(display_image)

            # Feature extraction
            features = feature_extraction(os.path.join("uploads", uploaded_file.name), model)

            # Recommendation
            indices = recommend(features, feature_list)

            # Display recommended products
            col1, col2, col3, col4, col5 = st.beta_columns(5)
            with col1:
                st.image(filenames[indices[0][0]])
            with col2:
                st.image(filenames[indices[0][1]])
            with col3:
                st.image(filenames[indices[0][2]])
            with col4:
                st.image(filenames[indices[0][3]])
            with col5:
                st.image(filenames[indices[0][4]])

        else:
            st.header("Some error occurred in file upload")

    # Chatbot section
    user_question = st.text_input("Ask a question:")
    if user_question:
        bot_response, recommended_products = chatbot.generate_response(user_question)
        st.write("Chatbot:", bot_response)

        # Display recommended products
        for result in recommended_products:
            pid = result['corpus_id']
            product_info = chatbot.product_data[pid]
            st.write("Product Name:", product_info['productDisplayName'])
            st.write("Category:", product_info['masterCategory'])
            st.write("Article Type:", product_info['articleType'])
            st.write("Usage:", product_info['usage'])
            st.write("Season:", product_info['season'])
            st.write("Gender:", product_info['gender'])
            st.image(chatbot.images[pid])

    # Sidebar navigation
    page = st.sidebar.radio("Navigation", ["Login", "Register", "Dashboard"])

    # Check if user is logged in
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # Show login page if user is not logged in
    if not st.session_state.logged_in:
        if page == "Login":
            login()

    # Show registration page if selected in the sidebar
    if page == "Register":
        register()

    # Show dashboard if selected in the sidebar and user is logged in
    if page == "Dashboard" and st.session_state.logged_in:
        show_dashboard()

# Run the main app
if _name_ == "_main_":
    main()