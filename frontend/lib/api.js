const BASE_URL = process.env.NEXT_PUBLIC_API_URL;

export const apiRequest = async (endpoint, options = {}) => {
  try {
    // Ensure credentials are included in the options
    const updatedOptions = {
      ...options,
      credentials: "include", // Ensure cookies are sent with the request
    };

    console.log("API Request initiated:", endpoint, updatedOptions);

    // Make the API call
    const response = await fetch(`${BASE_URL}/${endpoint}`, updatedOptions);

    // Check if the response is OK
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || "API request failed");
    }

    // Parse and return the JSON response
    return await response.json();
  } catch (error) {
    // console.error("Error during API request:", error.message);
    throw error;
  }
};
