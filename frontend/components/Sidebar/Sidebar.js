import React, { useEffect, useState, useRef } from "react";
import styles from "./Sidebar.module.css";
import { apiRequest } from "../../lib/api";
import { useRouter } from "next/navigation";
import { FaComments } from "react-icons/fa";

const Sidebar = ({ user, chatId, onChatIdChange, userName, logout, toggleSidebar }) => {
  const [recentChats, setRecentChats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false); // For user dropdown
  const avatarRef = useRef(null);
  const dropdownRef = useRef(null);
  const router = useRouter();

  useEffect(() => {
    const fetchLatestChats = async () => {
      try {
        if (!user) router.push(`/auth`);

        const data = await apiRequest("chatbot/latest-chats?x=5", {
          method: "GET",
        });
        setRecentChats(data.latest_chats || []);
      } catch (error) {
        console.log("Failed to fetch latest chats:", error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchLatestChats();
  }, [user]);

  const loadMoreChats = async () => {
    try {
      if (!user) router.push(`/auth`);

      const data = await apiRequest(`chatbot/latest-chats?x=${recentChats.length + 5}`, {
        method: "GET",
      });

      setRecentChats((prevChats) => [...prevChats, ...data.latest_chats]);
    } catch (error) {
      console.log("Failed to fetch latest chats:", error.message);
    }
  };

  const handleSelectChat = (selectedChatId) => {
    toggleSidebar()
    onChatIdChange(selectedChatId);
    router.push(`/chat?id=${selectedChatId}`);
    
  };

  const handleNewChat = () => {
    onChatIdChange(null);
    toggleSidebar()
    router.push(`/chat`);
  };

  // Handle user dropdown
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        avatarRef.current &&
        !avatarRef.current.contains(event.target) &&
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target)
      ) {
        setIsDropdownOpen(false); // Close dropdown if click is outside
      }
    };

    document.addEventListener("mousedown", handleClickOutside);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const toggleDropdown = () => {
    setIsDropdownOpen((prev) => !prev);
  };

  const getInitials = (name) => {
    const nameParts = (name || "").split(" ");
    return nameParts.map((part) => part[0]).join("").toUpperCase();
  };

  const handleLogout = () => {
    logout();
    router.push("/");
  };

  return (
    <div className={`${styles.sidebarContainer}`}>
      {/* Logo Section */}
      <div className="text-left mb-4">
        <h1 className="text-2xl font-semibold leading-relaxed tracking-wide">
          CHAT A.I +
        </h1>
      </div>

      {/* New Chat Button */}
      <div className="flex justify-between items-center">

        <button
          className="w-9/12 bg-blue-600 text-white rounded-full px-4 py-2 flex gap-2 items-center"
          onClick={handleNewChat}
        >
          <h1 className="text-3xl">+</h1> New Chat
        </button>
        <svg onClick={handleNewChat} className="cursor-pointer" width="50" height="50" viewBox="0 0 50 50" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect width="50" height="50" rx="25" fill="black" />
          <path d="M24.25 31C27.9779 31 31 27.9779 31 24.25C31 20.5221 27.9779 17.5 24.25 17.5C20.5221 17.5 17.5 20.5221 17.5 24.25C17.5 27.9779 20.5221 31 24.25 31Z" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          <path d="M31.375 32.5C31.9963 32.5 32.5 31.9963 32.5 31.375C32.5 30.7537 31.9963 30.25 31.375 30.25C30.7537 30.25 30.25 30.7537 30.25 31.375C30.25 31.9963 30.7537 32.5 31.375 32.5Z" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>

      </div>

      <div className="flex justify-between items-center mb-4 mt-6 border-b -mx-6 border-gray-200 "></div>

      {/* Recent Chats Section */}
      <div className="flex justify-between items-center">
        <span className="text-gray-500">Your conversations</span>
      </div>

      <div className="flex justify-between items-center mb-2 mt-3 border-b -mx-6 border-gray-200 "></div>

      <div className={`${styles.chatsContainer}`}>
        <ul className={styles.chatList}>
          {loading ? (
            <p>Loading...</p>
          ) : recentChats.length > 0 ? (
            recentChats.map((chat) => (
              <li
                key={chat.chat_id}
                className={`${styles.chatItem} ${chat.chat_id === chatId ? styles.activeChatItem : ""}`}
                onClick={() => handleSelectChat(chat.chat_id)}
              >
                <FaComments className={styles.chatIcon} />
                <span className={`${styles.chatName} capitalize`}>{chat.name}</span>
              </li>
            ))
          ) : (
            <p className={`${styles.noChats}`}>No recent chats.</p>
          )}
          {recentChats.length > 0 && (
            <li className={styles.loadmorechats} onClick={loadMoreChats}>
              Load more chats
            </li>
          )}
        </ul>
      </div>

      <div className="flex justify-between items-center mb-4 mt-3 border-b -mx-6 border-gray-200 "></div>

      {/* User Profile Section */}
      <div className="space-y-2 mt-auto">
        <div className="flex gap-2 items-center border rounded-full p-2 cursor-pointer" ref={avatarRef} onClick={toggleDropdown}>
          {/* <img
            alt="User profile picture"
            className="rounded-full mr-2"
            height="24"
            src="https://storage.googleapis.com/a1aa/image/uGzqTZg7TNKTBhvIwWvqfV5k0DgoBepyodTtvN9YFDNjRufnA.jpg"
            width="24"
          /> */}
          <div className={styles.avatar}>
            {getInitials(userName)}
          </div>
          <span>{userName}</span>
        </div>

        {isDropdownOpen && (
          <div className={styles.dropdown} ref={dropdownRef}>
            <div className={styles.logoutButton} onClick={handleLogout}>
              <div className={styles.iconContainer}>
                <svg
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                  className={styles.logoutIcon}
                >
                  <path
                    fillRule="evenodd"
                    clipRule="evenodd"
                    d="M6 4C5.44772 4 5 4.44772 5 5V19C5 19.5523 5.44772 20 6 20H10C10.5523 20 11 20.4477 11 21C11 21.5523 10.5523 22 10 22H6C4.34315 22 3 20.6569 3 19V5C3 3.34315 4.34315 2 6 2H10C10.5523 2 11 2.44772 11 3C11 3.55228 10.5523 4 10 4H6ZM15.2929 7.29289C15.6834 6.90237 16.3166 6.90237 16.7071 7.29289L20.7071 11.2929C21.0976 11.6834 21.0976 12.3166 20.7071 12.7071L16.7071 16.7071C16.3166 17.0976 15.6834 17.0976 15.2929 16.7071C14.9024 16.3166 14.9024 15.6834 15.2929 15.2929L17.5858 13H11C10.4477 13 10 12.5523 10 12C10 11.4477 10.4477 11 11 11H17.5858L15.2929 8.70711C14.9024 8.31658 14.9024 7.68342 15.2929 7.29289Z"
                    fill="currentColor"
                  ></path>
                </svg>
              </div>
              Log out
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Sidebar;
