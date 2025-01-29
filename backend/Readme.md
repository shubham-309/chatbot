# API Documentation

## Authentication Routes

### 1. **POST /auth/register**
**Description**: Register a new user.  
**Request Body**:
{
  "email": "user@example.com",
  "password": "password123",
  "username": "username"
}  
**Response**:
{
  "message": "User registered successfully."
}

### 2. **POST /auth/login**
**Description**: Log in an existing user.  
**Request Body**:
{
  "email": "user@example.com",
  "password": "password123"
}  
**Response**:
{
  "access_token": "<JWT-Token>"
}

### 3. **GET /auth/current**
**Description**: Get the current logged-in user's details.  
**Headers**:
{
  "Authorization": "Bearer <JWT-Token>"
}  
**Response**:
{
  "email": "user@example.com",
  "username": "username"
}

### 4. **GET /auth/google_login**
**Description**: Redirect to Google OAuth login page.  
**Response**: Redirects to Google login page.

### 5. **GET /auth/google_login/authorized**
**Description**: Handle OAuth response and create/login user using Google credentials.  
**Response**:
{
  "message": "User created via OAuth", 
  "email": "user@example.com", 
  "username": "username"
}

## Chatbot Routes

### 1. **POST /chatbot/ask**
**Description**: Ask a query to the chatbot.  
**Request Body**:
{
  "chat_id": "12345",
  "message": "Hello, how are you?"
}  
**Headers**:
{
  "Authorization": "Bearer <JWT-Token>"
}  
**Response**:
{
  "response": "This is a hardcoded response to your input: Hello, how are you?"
}

### 2. **GET /chatbot/latest-chats**
**Description**: Get the latest chats for a user.  
**Query Parameters**:  
x (optional, default 5) - Number of latest chats to return.  
**Headers**:
{
  "Authorization": "Bearer <JWT-Token>"
}  
**Response**:
{
  "latest_chats": [
    {
      "chat_id": "12345", 
      "name": "New Chat"
    },
    {
      "chat_id": "67890", 
      "name": "Another Chat"
    }
  ]
}

### 3. **GET /chatbot/chat-history**
**Description**: Get the entire chat history for a specific chat id.  
**Query Parameters**:
chat_id (required) - The ID of the chat to fetch the history for.  
**Headers**:
{
  "Authorization": "Bearer <JWT-Token>"
}  
**Response**:
{
  "chat_history": [
    {
      "sender": "user", 
      "content": "Hello, how are you?", 
      "timestamp": "2024-12-11T10:00:00"
    },
    {
      "sender": "bot", 
      "content": "This is a hardcoded response to your input: Hello, how are you?", 
      "timestamp": "2024-12-11T10:01:00"
    }
  ]
}
