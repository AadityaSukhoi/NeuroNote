lucide.createIcons();

let fullMarkdown = "";
let socket = null;

async function processEHR() {
    const input = document.getElementById('ehr-input').innerText.trim();
    if (!input) return;

    fullMarkdown = "";

    document.getElementById('input-layer').classList.remove('active');
    document.getElementById('status-text').textContent = "Synthesizing";

    const output = document.getElementById('markdown-output');
    const cloud = document.getElementById('entity-cloud');

    output.innerHTML = "";
    cloud.innerHTML = "";

    if (socket) socket.close();

    socket = new WebSocket('ws://127.0.0.1:8000/ws/summarize');

    socket.onopen = () => {
        console.log("WS CONNECTED");
        socket.send(JSON.stringify({ text: input }));
    };

    socket.onmessage = (event) => {
        const msg = JSON.parse(event.data);

        // ---------------- ENTITIES ----------------
        if (msg.type === "entities") {
            const entities = msg.data;

            const addTag = (text, cls) => {
                const el = document.createElement('span');
                el.className = `ent-tag ${cls}`;
                el.textContent = text;
                cloud.appendChild(el);
            };

            entities.persons?.forEach(p => addTag(p, "ent-person"));
            entities.dates?.forEach(d => addTag(d, "ent-date"));
            entities.medications?.forEach(m => addTag(m, "ent-med"));
            entities.conditions?.forEach(c => addTag(c, "ent-med"));
            entities.labs?.forEach(l => addTag(l, "ent-med"));
            entities.vitals?.forEach(v => addTag(v, "ent-med"));

            // ✅ FIX: hide input layer fully first
            const inputLayer = document.getElementById('input-layer');
            inputLayer.style.display = 'none';
            inputLayer.classList.remove('active');

            // ✅ FIX: make result layer block FIRST, then add active on next frame
            // so CSS transition from opacity:0 → 1 actually fires
            const resultLayer = document.getElementById('result-layer');
            resultLayer.style.display = 'block';

            // Force a reflow so the browser registers display:block 
            // before the opacity transition starts
            resultLayer.getBoundingClientRect(); // ← triggers reflow

            resultLayer.classList.add('active'); // now opacity:0 → 1 transitions properly
        }

        // ---------------- STREAM ----------------
        if (msg.type === "token") {
            fullMarkdown += msg.data;
            output.innerHTML = marked.parse(fullMarkdown);
            output.scrollTop = output.scrollHeight;
        }

        // ---------------- DONE ----------------
        if (msg.type === "done") {
            console.log("Streaming finished");
            document.getElementById('status-text').textContent = "Complete";
            lucide.createIcons();
        }

        // ---------------- ERROR ----------------
        if (msg.type === "error") {
            console.error("Backend error:", msg.data);
            document.getElementById('status-text').textContent = "Error";
        }
    };

    socket.onclose = () => {
        lucide.createIcons();
    };

    socket.onerror = (err) => {
        console.error("WS ERROR", err);
        document.getElementById('status-text').textContent = "Error";
    };
}

function copyText() {
    const text = document.getElementById('markdown-output').innerText;
    navigator.clipboard.writeText(text);
}