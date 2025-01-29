"use client";

import { useState } from "react";
import styles from "./page.module.css";
import Login from "../components/Login/Login"; // Adjust the path as per your project structure
import Signup from "../components/Signup/Signup"; // Adjust the path as per your project structure

export default function LandingPage() {
  const [isLoginMode, setIsLoginMode] = useState(true);

  const toggleMode = (e) => {
    // e.preventDefault();
    setIsLoginMode((prevMode) => !prevMode);
  };

  return (
    <div className={styles.container}>
      {/* Left Half: Image */}
      <div className={`${styles.left}  text-white px-8`}>
        {/* Header Section */}
        <h1 className="text-4xl my-8 text-left w-full">
          CHAT AI +
        </h1>
        <h1 className="text-4xl mb-10 text-left w-full">
          Learn, Discover & <br /> &nbsp;&nbsp;&nbsp;&nbsp; Automate in One Place.
        </h1>

        {/* Content Section */}
        <div className="text-left max-w-lg ">
          <h2 className="text-lg mb-2">
            Create a chatbot GPT using Python language. What will be the steps for that?
          </h2>
          <div className="mt-8 opacity-75 rounded-md px-4">
            <p className="font-bold mb-2 -mx-4">CHAT A.I+</p>
            <p>
              Sure, I can help you get started with creating a chatbot using GPT in Python.
              Here are the basic steps you'll need to follow:
            </p>
            <ol className="list-decimal list-inside mt-4">
              <li>
                <span className="font-semibold">Install the required libraries:</span> You'll need
                to install the transformers library from Hugging Face to use GPT. You can install it
                using pip.
              </li>
              <li className="mt-2">
                <span className="font-semibold">Load the pre-trained model:</span> GPT comes in
                several sizes and versions, so you'll need to choose the one that fits your needs.
                You can load a pre-trained GPT model.
              </li>
            </ol>
            <p className="mt-4">
              These are just the basic steps to get started with a GPT chatbot in Python. Depending
              on your requirements, you may need to add more features or complexity to the chatbot.
              Good luck!
            </p>
          </div>
        </div>
      </div>

      {/* Right Half: Login/Signup */}
      <div className={styles.right}>
        <div className={styles.content}>
          {isLoginMode ? <Login toggleMode={toggleMode} /> : <Signup toggleMode={toggleMode} />}
        </div>
      </div>
    </div>
  );
}
