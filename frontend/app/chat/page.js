"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "../../context/AuthContext";
import UserAvatar from "../../components/UserAvatar/UserAvatar";
import Sidebar from "../../components/Sidebar/Sidebar";
import ChatWindow from "../../components/ChatWindow/ChatWindow";
import styles from "./page.module.css";

const ChatPage = () => {
  const { user, logout } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();

  const [chatId, setChatId] = useState(null);
  const [isSidebarVisible, setIsSidebarVisible] = useState(false);

  // Function to update chatId
  const handleChatIdChange = (newChatId) => {
    setChatId(newChatId);
  };

  // Read `chatId` from URL if present
  useEffect(() => {
    const urlChatId = searchParams.get("id");
    if (urlChatId) {
      setChatId(urlChatId);
    }
  }, [searchParams]);

  // Redirect to auth page if user is not logged in
  useEffect(() => {
    if (!user) {
      router.push("/");
    }
  }, [user]);

  // Function to toggle sidebar visibility
  const toggleSidebar = () => {
    setIsSidebarVisible((prev) => !prev);
  };

  return (
    <div className={styles.container}>
      {/* Hamburger Icon */}
      <div className={styles.hamburger} onClick={toggleSidebar}>
        <span></span>
        <span></span>
        <span></span>
      </div>

      {/* Sidebar Component */}
      <div className={`${styles.sidebar} ${isSidebarVisible ? styles.visible : ""}`}>
        <Sidebar user={user} chatId={chatId} onChatIdChange={handleChatIdChange} userName={user?.username} logout={logout} toggleSidebar={toggleSidebar}/>
      </div>

      {/* Main Chat Section */}
      <div className={styles.mainContent}>

        {/* Chat Window Component */}
        <ChatWindow user={user} chatId={chatId} onChatIdChange={handleChatIdChange} />
      </div>
    </div>
  );
};

export default ChatPage;
