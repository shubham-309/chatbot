# app/auth/routes.py
from flask import Blueprint, request, jsonify, redirect, url_for, current_app, make_response
from app import db
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
import os

auth_bp = Blueprint('auth', __name__)
frontend_url = os.getenv("FRONTEND_URL")
# Register a new user
@auth_bp.route('/register', methods=['POST'])
def register_user():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        username = data.get('username')

        if not email or not password or not username:
            return jsonify({"message": "Email, password, and username are required."}), 400

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"message": "User already exists."}), 400

        hashed_password = generate_password_hash(password)
        new_user = User(email=email, password_hash=hashed_password, username=username)

        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User registered successfully."}), 201
    except Exception as e:
        current_app.logger.error(f"Error occurred: {str(e)}")
        return jsonify({"message": "Internal server error."}), 500


# User login
@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"msg": "Email and password are required"}), 400

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({"msg": "Invalid credentials"}), 401

        user_info = {
            "email": user.email,
            "username": user.username
        }

        # Generate access token
        access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(hours=1))

        # Set HTTP-only cookie for the token
        response = make_response(jsonify({"user": user_info}))
        response.set_cookie(
            "access_token",  # Cookie name
            access_token,    # JWT token value
            httponly=True,   # JavaScript cannot access this cookie
            secure=True,    # Use True in production with HTTPS
            samesite="None",  # Restrict cross-site sending
            max_age=3600     # Cookie expiration time in seconds
        )
        return response
    except Exception as e:
        current_app.logger.error(f"Error during login: {str(e)}")
        return jsonify({"msg": "Internal server error."}), 500


# Get current logged-in user
@auth_bp.route('/current', methods=['GET'])
@jwt_required()
def current_user():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404

        user_info = {
            "email": user.email,
            "username": user.username
        }
        return jsonify({"user": user_info}), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching current user: {str(e)}")
        return jsonify({"message": "Internal server error."}), 500


# User logout
@auth_bp.route('/logout', methods=['POST'])
def logout():
    try:
        response = make_response(jsonify({"message": "Logged out successfully."}))
        response.delete_cookie("access_token")
        return response
    except Exception as e:
        current_app.logger.error(f"Error during logout: {str(e)}")
        return jsonify({"message": "Internal server error."}), 500


# Google OAuth login
@auth_bp.route('/google_login')
def google_login():
    redirect_uri = url_for('auth.google_authorized', _external=True)
    return current_app.extensions['oauth'].google.authorize_redirect(redirect_uri)


@auth_bp.route('/google_login/authorized')
def google_authorized():
    try:
        oauth = current_app.extensions['oauth']
        token = oauth.google.authorize_access_token()
        if not token:
            return jsonify({"message": "Authorization failed"}), 400

        # Fetch user info from Google
        user_info = oauth.google.get('userinfo').json()
        email = user_info.get('email')
        username = user_info.get('name') or email

        if not email:
            return jsonify({"message": "Failed to retrieve email from Google"}), 400

        # Check if user exists in your database
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email, username=username, password_hash="oauth_login")
            db.session.add(user)
            db.session.commit()

        user_info = {
            "email": user.email,
            "username": user.username
        }

        # Generate access token
        access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(hours=1))

        response = redirect(f"{frontend_url}/chat")  # Redirect to frontend
        response.set_cookie(
            "access_token",  # Cookie name
            access_token,    # JWT token value
            httponly=True,   # JavaScript cannot access this cookie
            secure=True,    # Use True in production with HTTPS
            samesite="None",  # Restrict cross-site sending
            max_age=3600     # Cookie expiration time in seconds
        )

        return response

    except Exception as e:
        current_app.logger.error(f"Error during OAuth process: {str(e)}")
        return jsonify({"message": "Internal server error during OAuth"}), 500
