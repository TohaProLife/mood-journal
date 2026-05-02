const API_URL = "/api/entries";

const MOOD_EMOJI = { 1: "😞", 2: "😔", 3: "😐", 4: "🙂", 5: "😄" };
const MOOD_LABEL = { 1: "Ужасно", 2: "Плохо", 3: "Нормально", 4: "Хорошо", 5: "Отлично" };
const MOOD_COLORS = { 1: "#e53935", 2: "#ff9800", 3: "#fdd835", 4: "#66bb6a", 5: "#43a047" };

let selectedMood = null;
let currentDays = 7;
let moodChart = null;

document.addEventListener("DOMContentLoaded", () => {
    setupMoodButtons();
    setupPeriodButtons();
    document.getElementById("save-btn").addEventListener("click", saveEntry);
    loadData();
});

function setupMoodButtons() {
    document.querySelectorAll(".mood-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".mood-btn").forEach(b => b.classList.remove("selected"));
            btn.classList.add("selected");
            selectedMood = parseInt(btn.dataset.mood);
            document.getElementById("save-btn").disabled = false;
        });
    });
}

function setupPeriodButtons() {
    document.querySelectorAll(".period-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".period-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            currentDays = parseInt(btn.dataset.days);
            loadData();
        });
    });
}

async function saveEntry() {
    if (!selectedMood) return;

    let note = document.getElementById("note-input").value.trim();
    let msgEl = document.getElementById("form-message");

    try {
        let res = await fetch(API_URL + "/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ mood: selectedMood, note: note }),
        });

        if (!res.ok) {
            let err = await res.json();
            throw new Error(err.detail || "Ошибка сервера");
        }

        selectedMood = null;
        document.querySelectorAll(".mood-btn").forEach(b => b.classList.remove("selected"));
        document.getElementById("note-input").value = "";
        document.getElementById("save-btn").disabled = true;

        showMessage(msgEl, "Сохранено!", "success");
        loadData();
    } catch (err) {
        showMessage(msgEl, err.message, "error");
    }
}

async function loadData() {
    try {
        let entriesRes = await fetch(API_URL + "/?days=" + currentDays);
        let statsRes = await fetch(API_URL + "/stats?days=" + currentDays);

        if (!entriesRes.ok || !statsRes.ok) {
            throw new Error("Не удалось загрузить данные");
        }

        let entries = await entriesRes.json();
        let stats = await statsRes.json();

        renderEntries(entries);
        renderStats(stats);
        renderChart(stats);
    } catch (err) {
        console.error(err);
    }
}

async function deleteEntry(id) {
    try {
        let res = await fetch(API_URL + "/" + id, { method: "DELETE" });
        if (!res.ok) throw new Error("Не удалось удалить");
        loadData();
    } catch (err) {
        console.error(err);
    }
}

function renderEntries(entries) {
    let list = document.getElementById("entries-list");

    if (entries.length === 0) {
        list.innerHTML = '<p class="empty-state">Пока нет записей за этот период</p>';
        return;
    }

    let html = "";
    for (let e of entries) {
        let date = new Date(e.created_at).toLocaleDateString("ru-RU", {
            day: "numeric", month: "short", hour: "2-digit", minute: "2-digit"
        });
        let noteHtml = e.note ? '<div class="entry-note">' + escapeHtml(e.note) + '</div>' : "";
        html += '<div class="entry-item">' +
            '<span class="entry-mood">' + MOOD_EMOJI[e.mood] + '</span>' +
            '<div class="entry-content">' +
                '<div class="entry-date">' + date + ' — ' + MOOD_LABEL[e.mood] + '</div>' +
                noteHtml +
            '</div>' +
            '<button class="entry-delete" onclick="deleteEntry(' + e.id + ')">&times;</button>' +
        '</div>';
    }
    list.innerHTML = html;
}

function renderStats(stats) {
    document.getElementById("stat-total").textContent = stats.total_entries;
    document.getElementById("stat-avg").textContent =
        stats.average_mood !== null ? stats.average_mood.toFixed(1) : "—";
}

function renderChart(stats) {
    let ctx = document.getElementById("mood-chart").getContext("2d");

    let labels = [1, 2, 3, 4, 5].map(m => MOOD_LABEL[m]);
    let data = [1, 2, 3, 4, 5].map(m => stats.mood_counts[m] || 0);
    let colors = [1, 2, 3, 4, 5].map(m => MOOD_COLORS[m]);

    if (moodChart) moodChart.destroy();

    moodChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Количество дней",
                data: data,
                backgroundColor: colors,
                borderRadius: 6,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, ticks: { stepSize: 1 } }
            },
        },
    });
}

function showMessage(el, text, type) {
    el.textContent = text;
    el.className = "message " + type;
    setTimeout(() => {
        el.textContent = "";
        el.className = "message";
    }, 3000);
}

function escapeHtml(text) {
    let div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}
