const btn = document.getElementById("summarizeBtn");
const output = document.getElementById("output");
const status = document.getElementById("status");
const downloadBtn = document.getElementById("downloadPdfBtn");

let socket;

// Connect WebSocket
function connectWebSocket() {
  socket = new WebSocket("ws://localhost:8000/ws/summarize");

  socket.onopen = () => {
    status.textContent = "● Connected";
    status.style.color = "lime";
  };

  socket.onclose = () => {
    status.textContent = "● Disconnected";
    status.style.color = "red";
  };

  socket.onerror = () => {
    status.textContent = "● Error";
    status.style.color = "orange";
  };

  socket.onmessage = (event) => {
    output.textContent += event.data;
    output.scrollTop = output.scrollHeight;
  };
}

// Generate summary
btn.addEventListener("click", () => {
  const text = document.getElementById("ehrInput").value;

  if (!text.trim()) {
    alert("Enter EHR data boss 😤");
    return;
  }

  if (!socket || socket.readyState !== WebSocket.OPEN) {
    connectWebSocket();

    setTimeout(() => {
      output.textContent = "";
      socket.send(text);
    }, 500);
  } else {
    output.textContent = "";
    socket.send(text);
  }
});

// PDF Download
downloadBtn.addEventListener("click", () => {
  const { jsPDF } = window.jspdf;

  let text = output.textContent;

  if (!text.trim()) {
    alert("No summary to download 😅");
    return;
  }

  const doc = new jsPDF();

  // Title
  doc.setFontSize(16);
  doc.text("NeuroNote - EHR Summary", 10, 10);

  // Body
  doc.setFontSize(11);
  const lines = doc.splitTextToSize(text, 180);

  doc.text(lines, 10, 20);

  doc.save("EHR_Summary.pdf");
});

// Auto connect
connectWebSocket();