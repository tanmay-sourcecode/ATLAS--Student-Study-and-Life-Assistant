document.addEventListener("DOMContentLoaded", () => {
    // --- DOM Elements ---
    const messagesContainer = document.getElementById("messages-container");
    const chatForm = document.getElementById("chat-form");
    const chatInput = document.getElementById("chat-input");
    const sendBtn = document.getElementById("send-btn");
    const fileUpload = document.getElementById("file-upload");
    const fileDropzone = document.getElementById("file-dropzone");
    const connectionDot = document.getElementById("connection-dot");
    const connectionStatus = document.getElementById("connection-status");
    const approvalModal = document.getElementById("approval-modal");
    const approvalDescription = document.getElementById("approval-description");
    const btnApprove = document.getElementById("btn-approve");
    const btnDeny = document.getElementById("btn-deny");
    const toast = document.getElementById("toast-notification");
    const toastMessage = document.getElementById("toast-message");
    
    // Sidebar list nodes
    const overdueList = document.getElementById("tasks-overdue");
    const urgentList = document.getElementById("tasks-urgent");
    const upcomingList = document.getElementById("tasks-upcoming");
    const calendarList = document.getElementById("calendar-events");
    
    // Quick action chips
    const chips = document.querySelectorAll(".chip");
    
    // Pomodoro Timer Elements
    const pomodoroTime = document.getElementById("pomodoro-time");
    const timerToggleBtn = document.getElementById("timer-toggle-btn");
    const timerResetBtn = document.getElementById("timer-reset-btn");
    const progressRingCircle = document.querySelector(".progress-ring__circle");

    // --- State Variables ---
    let socket = null;
    let streamingMessageElement = null;
    let streamingText = "";
    
    // Pomodoro State
    let timerInterval = null;
    let secondsLeft = 1500; // 25 mins
    let totalSeconds = 1500;
    let isTimerRunning = false;

    // --- Connect WebSocket ---
    function connectWebSocket() {
        const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
        const wsUrl = `${protocol}//${window.location.host}/ws/chat`;
        
        socket = new WebSocket(wsUrl);
        
        socket.onopen = () => {
            connectionDot.className = "dot green";
            connectionStatus.textContent = "Online";
            console.log("WebSocket connected.");
        };
        
        socket.onclose = () => {
            connectionDot.className = "dot red";
            connectionStatus.textContent = "Offline (Reconnecting...)";
            setTimeout(connectWebSocket, 3000);
        };
        
        socket.onerror = (err) => {
            console.error("WebSocket error:", err);
        };
        
        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.type === "token") {
                handleToken(data.text);
            } else if (data.type === "done") {
                finalizeStreamingMessage();
            } else if (data.type === "error") {
                handleError(data.text);
            } else if (data.type === "approval_request") {
                showApprovalModal(data.description);
            }
        };
    }

    // --- Message Handling ---
    function handleToken(text) {
        if (!streamingMessageElement) {
            // Create a new assistant message node
            streamingMessageElement = document.createElement("div");
            streamingMessageElement.className = "message assistant";
            
            const contentDiv = document.createElement("div");
            contentDiv.className = "message-content";
            streamingMessageElement.appendChild(contentDiv);
            
            messagesContainer.appendChild(streamingMessageElement);
            streamingText = "";
        }
        
        streamingText += text;
        const contentNode = streamingMessageElement.querySelector(".message-content");
        contentNode.innerHTML = renderMarkdown(streamingText);
        scrollToBottom();
    }
    
    function finalizeStreamingMessage() {
        if (streamingMessageElement) {
            const contentNode = streamingMessageElement.querySelector(".message-content");
            contentNode.innerHTML = renderMarkdown(streamingText);
            streamingMessageElement = null;
            streamingText = "";
            fetchTasks(); // Reload tasks after tool updates
        }
    }
    
    function handleError(errorText) {
        if (streamingMessageElement) {
            streamingMessageElement.remove();
            streamingMessageElement = null;
        }
        
        const errorMsgNode = document.createElement("div");
        errorMsgNode.className = "message assistant";
        errorMsgNode.innerHTML = `<div class="message-content" style="border-left: 4px solid var(--danger); background: rgba(239, 68, 68, 0.05); color: var(--text-primary);"><i class="fa-solid fa-triangle-exclamation" style="color: var(--danger); margin-right: 6px;"></i> ${errorText}</div>`;
        messagesContainer.appendChild(errorMsgNode);
        scrollToBottom();
    }

    function sendMessage(text) {
        if (!socket || socket.readyState !== WebSocket.OPEN) {
            showToast("Server offline. Cannot send message.");
            return;
        }
        
        // Append user message
        const userMsg = document.createElement("div");
        userMsg.className = "message user";
        userMsg.innerHTML = `<div class="message-content">${text}</div>`;
        messagesContainer.appendChild(userMsg);
        scrollToBottom();
        
        // Send payload
        socket.send(JSON.stringify({
            "type": "message",
            "text": text
        }));
    }

    // --- Human in the Loop Approval ---
    function showApprovalModal(description) {
        approvalDescription.textContent = description;
        approvalModal.style.display = "flex";
    }
    
    function handleApprovalResponse(approved) {
        approvalModal.style.display = "none";
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({
                "type": "approval_response",
                "approved": approved
            }));
        }
    }
    
    btnApprove.addEventListener("click", () => handleApprovalResponse(true));
    btnDeny.addEventListener("click", () => handleApprovalResponse(false));

    // --- Form & Action Chip Submit ---
    chatForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const text = chatInput.value.trim();
        if (!text) return;
        
        sendMessage(text);
        chatInput.value = "";
        chatInput.style.height = "auto";
    });
    
    chatInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event("submit"));
        }
    });

    chips.forEach(chip => {
        chip.addEventListener("click", () => {
            const query = chip.getAttribute("data-query");
            sendMessage(query);
        });
    });

    // Auto-resize textarea
    chatInput.addEventListener("input", function() {
        this.style.height = "auto";
        this.style.height = (this.scrollHeight - 4) + "px";
    });

    // --- File Ingestion / Drag-and-Drop ---
    window.addEventListener("dragenter", (e) => {
        e.preventDefault();
        fileDropzone.style.display = "flex";
    });

    fileDropzone.addEventListener("dragover", (e) => {
        e.preventDefault();
    });

    fileDropzone.addEventListener("dragleave", (e) => {
        // Only hide if cursor leaves the dropzone bounding box
        if (e.relatedTarget === null || !fileDropzone.contains(e.relatedTarget)) {
            fileDropzone.style.display = "none";
        }
    });

    fileDropzone.addEventListener("drop", (e) => {
        e.preventDefault();
        fileDropzone.style.display = "none";
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            uploadFile(files[0]);
        }
    });

    fileUpload.addEventListener("change", (e) => {
        if (e.target.files.length > 0) {
            uploadFile(e.target.files[0]);
        }
    });

    async function uploadFile(file) {
        showToast(`Uploading '${file.name}' for ingestion...`);
        
        const formData = new FormData();
        formData.append("file", file);
        
        try {
            const res = await fetch("/api/upload", {
                method: "POST",
                body: formData
            });
            const data = await res.json();
            
            if (res.ok) {
                showToast("File ingested successfully!");
                // Let the agent know in context
                sendMessage(`I uploaded and ingested document '${file.name}' successfully.`);
            } else {
                showToast(`Error: ${data.detail || "Upload failed"}`);
            }
        } catch (err) {
            console.error("Upload error:", err);
            showToast("Network error uploading file.");
        }
    }

    // --- Dashboard Data Loading ---
    async function fetchTasks() {
        try {
            const res = await fetch("/api/reminders");
            if (!res.ok) return;
            const data = await res.json();
            
            renderTasks(data.overdue, overdueList, "No overdue tasks");
            renderTasks(data.urgent, urgentList, "No urgent tasks");
            renderTasks(data.upcoming, upcomingList, "No upcoming tasks");
        } catch (err) {
            console.error("Error loading tasks:", err);
        }
    }
    
    async function fetchCalendar() {
        try {
            const res = await fetch("/api/calendar");
            if (!res.ok) return;
            const events = await res.json();
            
            calendarList.innerHTML = "";
            if (events.length === 0) {
                calendarList.innerHTML = `<li class="empty-state">No events scheduled</li>`;
                return;
            }
            
            events.forEach(evt => {
                const li = document.createElement("li");
                const start = new Date(evt.start);
                const timeString = start.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                const dateString = start.toLocaleDateString([], { month: 'short', day: 'numeric' });
                
                li.innerHTML = `
                    <div class="task-title" style="color: var(--primary-light)">${evt.title}</div>
                    <div class="task-due"><i class="fa-solid fa-clock"></i> ${dateString} @ ${timeString}</div>
                `;
                calendarList.appendChild(li);
            });
        } catch (err) {
            console.error("Error loading calendar:", err);
        }
    }
    
    function renderTasks(list, targetElement, emptyText) {
        targetElement.innerHTML = "";
        if (!list || list.length === 0) {
            targetElement.innerHTML = `<li class="empty-state">${emptyText}</li>`;
            return;
        }
        
        list.forEach(task => {
            const li = document.createElement("li");
            const due = new Date(task.deadline);
            const dueString = due.toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
            
            li.innerHTML = `
                <div class="task-title">${task.title}</div>
                <div class="task-due"><i class="fa-solid fa-hourglass-half"></i> Due: ${dueString}</div>
            `;
            targetElement.appendChild(li);
        });
    }

    // --- Pomodoro Timer ---
    function setProgress(percent) {
        const radius = progressRingCircle.r.baseVal.value;
        const circumference = radius * 2 * Math.PI;
        const offset = circumference - (percent / 100) * circumference;
        progressRingCircle.style.strokeDashoffset = offset;
    }
    
    // Initialize Circle Length
    const radius = progressRingCircle.r.baseVal.value;
    progressRingCircle.style.strokeDasharray = `${radius * 2 * Math.PI}`;
    setProgress(100);
    
    function updateTimerDisplay() {
        const mins = Math.floor(secondsLeft / 60);
        const secs = secondsLeft % 60;
        pomodoroTime.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        
        const percent = (secondsLeft / totalSeconds) * 100;
        setProgress(percent);
    }
    
    function toggleTimer() {
        if (isTimerRunning) {
            // Pause
            clearInterval(timerInterval);
            timerToggleBtn.innerHTML = `<i class="fa-solid fa-play"></i> Start`;
            isTimerRunning = false;
        } else {
            // Start
            timerInterval = setInterval(() => {
                secondsLeft--;
                updateTimerDisplay();
                
                if (secondsLeft <= 0) {
                    clearInterval(timerInterval);
                    timerToggleBtn.innerHTML = `<i class="fa-solid fa-play"></i> Start`;
                    isTimerRunning = false;
                    showToast("Focus session complete!");
                    sendMessage("I completed a Pomodoro study focus session.");
                    secondsLeft = 1500;
                    updateTimerDisplay();
                }
            }, 1000);
            
            timerToggleBtn.innerHTML = `<i class="fa-solid fa-pause"></i> Pause`;
            isTimerRunning = true;
        }
    }
    
    function resetTimer() {
        clearInterval(timerInterval);
        isTimerRunning = false;
        secondsLeft = 1500;
        updateTimerDisplay();
        timerToggleBtn.innerHTML = `<i class="fa-solid fa-play"></i> Start`;
    }
    
    timerToggleBtn.addEventListener("click", toggleTimer);
    timerResetBtn.addEventListener("click", resetTimer);

    // --- Helpers ---
    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    function showToast(message) {
        if (toastMessage) {
            toastMessage.textContent = message;
        }
        toast.classList.add("show");
        setTimeout(() => {
            toast.classList.remove("show");
        }, 3000);
    }
    
    // Markdown Parser
    function renderMarkdown(text) {
        if (!text) return "";
        let html = text;
        
        // Escape HTML tags to prevent injections
        html = html.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        
        // Code blocks
        html = html.replace(/```([\s\S]*?)```/g, "<pre><code>$1</code></pre>");
        
        // Inline code
        html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
        
        // Bold tags
        html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
        
        // List elements
        html = html.replace(/^- (.*)$/gm, "<li>$1</li>");
        html = html.replace(/(<li>.*<\/li>)/g, "<ul>$1</ul>");
        
        // Newlines/Paragraph breaks
        html = html.replace(/\n/g, "<br>");
        
        return html;
    }

    // --- Initialization ---
    connectWebSocket();
    fetchTasks();
    fetchCalendar();
    
    // Poll dashboard values every 30 seconds
    setInterval(() => {
        fetchTasks();
        fetchCalendar();
    }, 30000);
});
