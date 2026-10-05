
import { useState, useEffect, useRef } from "react";
import "./App.css";

function App() {
  // Load saved chats
  const [chats, setChats] = useState(() => {
    try {
      const savedChats = localStorage.getItem(
        "shopb_chats"
      );

      return savedChats
        ? JSON.parse(savedChats)
        : [];
    } catch (error) {
      console.error("Could not load chats:", error);
      return [];
    }
  });

  const [activeChatId, setActiveChatId] = useState(null);

  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(() => {
  return window.innerWidth > 768;
});
  const messagesEndRef = useRef(null);

  // Get current chat
  const activeChat = chats.find(
    (chat) => chat.id === activeChatId
  );

  const messages = activeChat?.messages || [];

  // Save chats
  useEffect(() => {
    localStorage.setItem(
      "shopb_chats",
      JSON.stringify(chats)
    );
  }, [chats]);

  // Save active chat
  useEffect(() => {
    if (activeChatId) {
      localStorage.setItem(
        "shopb_active_chat",
        activeChatId
      );
    } else {
      localStorage.removeItem(
        "shopb_active_chat"
      );
    }
  }, [activeChatId]);

  // Scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  // Create a new chat
  const createNewChat = () => {
    const newChat = {
      id: Date.now().toString(),
      title: "New Chat",
      messages: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    setChats((previousChats) => [
      newChat,
      ...previousChats,
    ]);

    setActiveChatId(newChat.id);
    setQuestion("");
  };

  // Delete chat
  const deleteChat = (chatId) => {
    const updatedChats = chats.filter(
      (chat) => chat.id !== chatId
    );

    setChats(updatedChats);

    if (chatId === activeChatId) {
      if (updatedChats.length > 0) {
        setActiveChatId(updatedChats[0].id);
      } else {
        setActiveChatId(null);
      }
    }
  };

  // Select a previous chat
  const selectChat = (chatId) => {
    setActiveChatId(chatId);
    setQuestion("");
  };

  // Send question
  const askAssistant = async () => {
    const userQuestion = question.trim();

    if (!userQuestion || loading) {
      return;
    }

    let chatId = activeChatId;

    // Automatically create chat if none exists
    if (!chatId) {
      chatId = Date.now().toString();

      const newChat = {
        id: chatId,
        title: userQuestion.substring(0, 35),
        messages: [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      setChats((previousChats) => [
        newChat,
        ...previousChats,
      ]);

      setActiveChatId(chatId);
    }

    // Add user message
    const userMessage = {
      role: "user",
      content: userQuestion,
      timestamp: new Date().toISOString(),
    };

    setChats((previousChats) =>
      previousChats.map((chat) => {
        if (chat.id !== chatId) {
          return chat;
        }

        return {
          ...chat,
          title:
            chat.title === "New Chat"
              ? userQuestion.substring(0, 35)
              : chat.title,
          messages: [
            ...chat.messages,
            userMessage,
          ],
          updatedAt: new Date().toISOString(),
        };
      })
    );

    setQuestion("");
    setLoading(true);

    try {
      const response = await fetch(`${import
        .meta.env.VITE_API_URL}/chat`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
  question: userQuestion,
  history: messages
    .slice(-6)
    .map((message) => ({
      role: message.role,
      content: message.content,
    })),
}),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Something went wrong."
        );
      }

      const assistantMessage = {
        role: "assistant",
        content: data.answer,
        sources: data.sources || [],
        timestamp: new Date().toISOString(),
      };

      setChats((previousChats) =>
        previousChats.map((chat) => {
          if (chat.id !== chatId) {
            return chat;
          }

          return {
            ...chat,
            messages: [
              ...chat.messages,
              assistantMessage,
            ],
            updatedAt: new Date().toISOString(),
          };
        })
      );
    } catch (error) {
      const errorMessage = {
        role: "assistant",
        content: `Sorry, something went wrong: ${error.message}`,
        sources: [],
        timestamp: new Date().toISOString(),
      };

      setChats((previousChats) =>
        previousChats.map((chat) => {
          if (chat.id !== chatId) {
            return chat;
          }

          return {
            ...chat,
            messages: [
              ...chat.messages,
              errorMessage,
            ],
            updatedAt: new Date().toISOString(),
          };
        })
      );
    } finally {
      setLoading(false);
    }
  };

  // Enter to send
  const handleKeyDown = (event) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();
      askAssistant();
    }
  };

  // Suggested question
  const askSuggestion = (text) => {
    setQuestion(text);
  };

  // Sort recent chats
  const recentChats = [...chats].sort(
    (a, b) =>
      new Date(b.updatedAt) -
      new Date(a.updatedAt)
  );

  return (
    <div className="app">

      {/* SIDEBAR */}

      <aside
        className={`sidebar ${
          sidebarOpen ? "sidebar-open" : "sidebar-closed"
        }`}
      >

        <div className="sidebar-header">

          <div className="brand">
            🛍️
            <span>ShopB.Africa</span>
          </div>

          <button
            className="close-sidebar"
            onClick={() => setSidebarOpen(false)}
          >
            ×
          </button>

        </div>


        <button
          className="new-chat"
          onClick={createNewChat}
        >
          + New Chat
        </button>


        <div className="recent-title">
          Recent Chats
        </div>


        <div className="chat-list">

          {recentChats.length === 0 ? (

            <p className="no-chats">
              No recent chats
            </p>

          ) : (

            recentChats.map((chat) => (

              <div
                key={chat.id}
                className={`chat-item ${
                  chat.id === activeChatId
                    ? "active-chat"
                    : ""
                }`}
                onClick={() =>
                  selectChat(chat.id)
                }
              >

                <span className="chat-icon">
                  💬
                </span>

                <span className="chat-title">
                  {chat.title}
                </span>

                <button
                  className="delete-chat"
                  onClick={(event) => {
                    event.stopPropagation();
                    deleteChat(chat.id);
                  }}
                >
                  ×
                </button>

              </div>

            ))

          )}

        </div>

      </aside>


      {/* MAIN CHAT */}

      <div className="chat-container">

        {/* HEADER */}

        <header className="chat-header">

          {!sidebarOpen && (
            <button
              className="menu-button"
              onClick={() =>
                setSidebarOpen(true)
              }
            >
              ☰
            </button>
          )}

          <div className="header-info">

            <div className="header-avatar">
              🤖
            </div>

            <div>
              <h1>
                ShopB.Africa AI Assistant
              </h1>

              <p>
                AI-powered customer support
              </p>
            </div>

          </div>

        </header>


        {/* CHAT BODY */}

        <main className="chat-body">

          {messages.length === 0 && (

            <div className="welcome-message">

              <div className="welcome-icon">
                🤖
              </div>

              <h2>
                How can I help you?
              </h2>

              <p>
                Ask me about ShopB.Africa orders,
                payments, delivery, returns and
                vendors.
              </p>

              <div className="suggestions">

                <button
                  onClick={() =>
                    askSuggestion(
                      "Explain your order process?"
                    )
                  }
                >
                  🚚 Order and Delivery
                </button>

                <button
                  onClick={() =>
                    askSuggestion(
                      "what shopb.africa offer"
                    )
                  }
                >
                  💳 Company Overview
                </button>

                <button
                  onClick={() =>
                    askSuggestion(
                      "How can I become a vendor?"
                    )
                  }
                >
                  🏪 Become a Vendor
                </button>

                <button
                  onClick={() =>
                    askSuggestion(
                      "Can I return a damaged product?"
                    )
                  }
                >
                  🔄 Returns
                </button>

              </div>

            </div>
          )}


          {/* MESSAGES */}

          {messages.map(
            (message, index) => (

              <div
                key={index}
                className={`message-row ${
                  message.role === "user"
                    ? "user-row"
                    : "assistant-row"
                }`}
              >

                {message.role === "assistant" && (

                  <div className="avatar assistant-avatar">
                    🤖
                  </div>

                )}

                <div>

                  <div
                    className={`message-bubble ${
                      message.role === "user"
                        ? "user-message"
                        : "assistant-message"
                    }`}
                  >
                    <p>
                      {message.content}
                    </p>
                  </div>


                  {message.role === "assistant" &&
                    message.sources &&
                    message.sources.length > 0 && (

                      <div className="sources">

                        <span className="sources-title">
                          📚 Sources
                        </span>

                        
{message.sources.map((source, sourceIndex) => (
  <div
    key={`${source.source}-${source.section}-${sourceIndex}`}
    className="source-item"
  >
    <strong>{source.section || "General Information"}</strong>
    <span className="source-filename">
      {source.source}
    </span>
  </div>
))}

                      </div>

                    )}

                </div>


                {message.role === "user" && (

                  <div className="avatar user-avatar">
                    👤
                  </div>

                )}

              </div>

            )
          )}


          {/* LOADING */}

          {loading && (

            <div className="message-row assistant-row">

              <div className="avatar assistant-avatar">
                🤖
              </div>

              <div className="message-bubble assistant-message typing">

                <span></span>
                <span></span>
                <span></span>

              </div>

            </div>

          )}

          <div ref={messagesEndRef}></div>

        </main>


        {/* INPUT */}

        <div className="chat-input-area">

          <div className="input-wrapper">

            <textarea
              value={question}
              onChange={(event) =>
                setQuestion(event.target.value)
              }
              onKeyDown={handleKeyDown}
              placeholder="Message ShopB.Africa AI Assistant..."
              rows="1"
              disabled={loading}
            />

            <button
              className="send-button"
              onClick={askAssistant}
              disabled={
                !question.trim() || loading
              }
            >
              ➤
            </button>

          </div>

          <p className="input-note">
            Develop by Abubakar Aliyu          </p>

        </div>

      </div>

    </div>
  );
}

export default App;
