from flask import Flask, request, jsonify, render_template_string
import requests

app = Flask(__name__)

# === НАСТРОЙКА API (ТОКЕН УСТАНОВЛЕН) ===
API_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6ImQ5MjNkYjBiLTgwYzUtNDg3YS1iZTI0LTlkMDIxNDlmNGE3YiIsImlhdCI6MTc4MTYzNDg0NSwic3ViIjoiZGV2ZWxvcGVyLzVhNTBkNDY1LTFmNjYteThlMy1jN2E4LWFhMWI1ZWEyZjVjYiIsInNjb3BlcyI6WyJicmF3bHN0YXJzIl0sImxpbWl0cyI6W3sidGllciI6ImRldmVsb3Blci9zaWx2ZXIiLCJ0eXBlIjoidGhyb3R0bGluZyJ9LHsiY2lkcnMiOlsiMC4wLjAuMCJdLCJ0eXBlIjoiY2xpZW50In1dfQ.LJVRA4Tdesh6eAq6hkXhVOHR-FKVWfnIw7c_Cgiu0c7e8sPaSMof3f-gbMG3-dkRjrCU4chK3kLazn7fwXFGNA"

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Accept": "application/json"
}

# === ИНТЕРФЕЙС (VEST STARS) ===
HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vest Stars — Live Brawl Stars Stats</title>
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #0b0c10; color: #e2e8f0; }
        .font-title { font-family: 'Poppins', sans-serif; }
        .gold-text {
            background: linear-gradient(135deg, #ffe066 0%, #f59e0b 50%, #b45309 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .neon-border-cyan { box-shadow: 0 0 15px rgba(6, 182, 212, 0.4); border-color: rgba(6, 182, 212, 0.6); }
        .gold-glow:hover { box-shadow: 0 0 25px rgba(245, 158, 11, 0.3); transform: translateY(-2px); }
    </style>
</head>
<body class="min-h-screen flex flex-col justify-between overflow-x-hidden">

    <header class="border-b border-gray-900 bg-black/40 backdrop-blur-md relative z-10">
        <div class="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 bg-gradient-to-tr from-purple-600 to-cyan-500 rounded-xl flex items-center justify-center font-title font-black text-xl text-white">V</div>
                <span class="font-title text-2xl font-black tracking-tight text-white">VEST <span class="gold-text">STARS</span></span>
            </div>
            <div class="text-xs text-gray-500 bg-gray-900/60 px-3 py-1.5 rounded-full border border-gray-800">
                <span class="w-2 h-2 inline-block bg-green-500 rounded-full mr-2 animate-pulse"></span>Live Supercell Bridge
            </div>
        </div>
    </header>

    <main class="flex-grow max-w-5xl w-full mx-auto px-4 py-8 relative z-10">
        <div class="bg-gradient-to-b from-gray-900/80 to-gray-950/80 border border-gray-800 rounded-3xl p-6 md:p-8 backdrop-blur-xl mb-8 shadow-2xl">
            <div class="max-w-2xl mx-auto text-center mb-6">
                <h1 class="text-3xl md:text-4xl font-title font-extrabold text-white mb-3">Реальная статистика <span class="gold-text">Brawl Stars</span></h1>
                <p class="text-gray-400 text-sm">Введите реальный тег игрока (например: YV2Y2G0L, 99UY29CL).</p>
            </div>

            <form id="searchForm" class="max-w-xl mx-auto flex flex-col sm:flex-row gap-3 items-center">
                <div class="relative w-full">
                    <span class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 font-mono text-lg font-bold">#</span>
                    <input type="text" id="playerTag" placeholder="YV2Y2G0L" class="w-full bg-black/60 border border-gray-800 rounded-xl pl-8 pr-4 py-3.5 text-white font-mono text-lg font-semibold tracking-wider uppercase focus:outline-none focus:border-purple-500" required>
                </div>
                <button type="submit" class="w-full sm:w-auto px-8 py-3.5 bg-gradient-to-r from-amber-500 to-amber-600 text-black font-title font-bold rounded-xl transition-all gold-glow cursor-pointer">
                    <i class="fa-solid fa-bolt"></i> Получить данные
                </button>
            </form>
        </div>

        <div id="loading" class="hidden text-center py-12">
            <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-t-amber-500 border-r-purple-500 border-b-cyan-500 border-l-transparent mb-4"></div>
            <p class="text-gray-400">Отправляем авторизованный запрос к серверам Supercell...</p>
        </div>

        <div id="errorBlock" class="hidden max-w-xl mx-auto bg-red-950/40 border border-red-900/60 text-red-200 p-4 rounded-xl text-center mb-8"></div>

        <div id="results" class="hidden space-y-8">
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div class="bg-gradient-to-br from-gray-900 to-purple-950/40 border border-gray-800 rounded-2xl p-6 flex flex-col justify-between">
                    <div>
                        <div class="flex items-center gap-3 mb-4">
                            <div class="w-14 h-14 bg-gray-800 rounded-xl border-2 border-purple-500 flex items-center justify-center font-title text-2xl text-cyan-400" id="resIcon">⭐</div>
                            <div>
                                <h2 class="text-2xl font-title font-bold text-white tracking-wide" id="resName">-</h2>
                                <p class="text-xs text-purple-400 font-mono" id="resTag">#000000</p>
                            </div>
                        </div>
                        <div class="inline-block bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-xs px-3 py-1 rounded-full font-medium">
                            Цвет ника: <span id="resNameColor">-</span>
                        </div>
                    </div>
                    <div class="space-y-3 border-t border-gray-800/60 pt-4 mt-4">
                        <div class="flex justify-between items-center">
                            <span class="text-gray-400 text-sm">Уровень опыта</span>
                            <span class="text-white font-bold bg-gray-800 px-2.5 py-0.5 rounded text-sm" id="resExp">-</span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-gray-400 text-sm">Клуб</span>
                            <span class="text-cyan-400 font-semibold text-sm" id="resClub">-</span>
                        </div>
                    </div>
                </div>

                <div class="lg:col-span-2 bg-gray-900/60 border border-gray-800 rounded-2xl p-6">
                    <h3 class="text-lg font-title font-bold text-white mb-4"><i class="fa-solid fa-network-wired text-cyan-400 text-sm"></i> Обнаруженные игры в Supercell ID</h3>
                    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                        <div class="bg-black/40 border neon-border-cyan rounded-xl p-4 flex flex-col justify-between">
                            <span class="text-xs font-title font-black text-cyan-400">BRAWL STARS</span>
                            <p class="text-2xl font-title font-black text-white mt-2" id="subBsTrophies">0</p>
                            <span class="text-[10px] text-green-400 mt-1 uppercase font-semibold">Активен (Данные Live)</span>
                        </div>
                        <div class="bg-black/10 border border-gray-900 rounded-xl p-4 opacity-40">
                            <span class="text-xs font-title font-black text-gray-500">CLASH ROYALE</span>
                            <p class="text-sm text-gray-600 mt-4">Требуется доп. авторизация</p>
                        </div>
                        <div class="bg-black/10 border border-gray-900 rounded-xl p-4 opacity-40">
                            <span class="text-xs font-title font-black text-gray-500">CLASH OF CLANS</span>
                            <p class="text-sm text-gray-600 mt-4">Требуется доп. авторизация</p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="bg-gray-900/40 border border-gray-800 rounded-2xl p-6">
                <h3 class="text-xl font-title font-bold text-white mb-6"><i class="fa-solid fa-chart-simple text-amber-500"></i> Основные показатели</h3>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div class="bg-black/40 border border-gray-800/60 p-4 rounded-xl">
                        <span class="text-xs text-gray-400 block mb-1">Текущие трофеи</span>
                        <span class="text-2xl font-title font-black text-amber-400 flex items-center gap-2" id="statTrophies">0</span>
                    </div>
                    <div class="bg-black/40 border border-gray-800/60 p-4 rounded-xl">
                        <span class="text-xs text-gray-400 block mb-1">Максимум трофеев</span>
                        <span class="text-2xl font-title font-black text-yellow-500" id="statHighestTrophies">0</span>
                    </div>
                    <div class="bg-black/40 border border-gray-800/60 p-4 rounded-xl">
                        <span class="text-xs text-gray-400 block mb-1">Победы 3vs3</span>
                        <span class="text-2xl font-title font-black text-purple-400" id="stat3v3">0</span>
                    </div>
                    <div class="bg-black/40 border border-gray-800/60 p-4 rounded-xl">
                        <span class="text-xs text-gray-400 block mb-1">Соло победы</span>
                        <span class="text-2xl font-title font-black text-cyan-400" id="statSolo">0</span>
                    </div>
                </div>
            </div>

            <div class="bg-gray-900/40 border border-gray-800 rounded-2xl p-6">
                <div class="flex justify-between items-center mb-6">
                    <h3 class="text-xl font-title font-bold text-white"><i class="fa-solid fa-users text-purple-500"></i> Персонажи на аккаунте</h3>
                    <span id="brawlersCount" class="bg-purple-500/10 border border-purple-500/30 text-purple-300 text-xs px-3 py-1 rounded-full font-mono font-bold">0</span>
                </div>
                <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4" id="brawlersContainer"></div>
            </div>
        </div>
    </main>

    <footer class="border-t border-gray-900 bg-black/60 py-6 text-center text-xs text-gray-600">
        <p>&copy; 2026 <span class="font-title font-bold text-gray-400">VEST STARS</span>. Настоящие данные из Supercell API.</p>
    </footer>

    <script>
        document.getElementById('searchForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const rawTag = document.getElementById('playerTag').value.trim().toUpperCase();
            const cleanTag = rawTag.replace('#', '');
            if(!cleanTag) return;

            document.getElementById('loading').classList.remove('hidden');
            document.getElementById('results').classList.add('hidden');
            document.getElementById('errorBlock').classList.add('hidden');

            fetch(`/api/stats?tag=${cleanTag}`)
                .then(res => {
                    if (!res.ok) return res.json().then(err => { throw err; });
                    return res.json();
                })
                .then(data => {
                    document.getElementById('loading').classList.add('hidden');
                    
                    // Заполняем профиль
                    document.getElementById('resName').innerText = data.name;
                    document.getElementById('resTag').innerText = `#${data.tag}`;
                    document.getElementById('resNameColor').innerText = data.nameColor || 'Стандартный';
                    document.getElementById('resExp').innerText = data.expLevel;
                    document.getElementById('resClub').innerText = data.club && data.club.name ? data.club.name : 'Нет клуба';
                    
                    // Статистика
                    document.getElementById('subBsTrophies').innerText = data.trophies.toLocaleString();
                    document.getElementById('statTrophies').innerHTML = `${data.trophies.toLocaleString()} <i class="fa-solid fa-trophy text-sm"></i>`;
                    document.getElementById('statHighestTrophies').innerText = data.highestTrophies.toLocaleString();
                    document.getElementById('stat3v3').innerText = data['3vs3Victories'] ? data['3vs3Victories'].toLocaleString() : 0;
                    document.getElementById('statSolo').innerText = data.soloVictories ? data.soloVictories.toLocaleString() : 0;
                    
                    // Бравлеры
                    const brawlers = data.brawlers || [];
                    document.getElementById('brawlersCount').innerText = `${brawlers.length} персонажей`;
                    
                    const container = document.getElementById('brawlersContainer');
                    container.innerHTML = '';
                    
                    brawlers.sort((a,b) => b.trophies - a.trophies).forEach(br => {
                        const card = document.createElement('div');
                        card.className = "bg-gradient-to-b from-gray-950 to-gray-900 border border-gray-800 rounded-xl p-3 flex flex-col justify-between";
                        card.innerHTML = `
                            <div class="flex justify-between items-center mb-2">
                                <span class="text-[10px] text-gray-500 font-bold">ID: ${br.id}</span>
                                <span class="bg-black/60 px-1.5 py-0.5 rounded text-[10px] text-amber-400 font-bold">⚡ Сила ${br.power}</span>
                            </div>
                            <div class="py-2"><p class="font-title font-bold text-white text-base">${br.name}</p></div>
                            <div class="flex items-center justify-between mt-1 pt-2 border-t border-gray-800/40">
                                <span class="text-xs text-gray-400">Кубки</span>
                                <span class="text-xs font-bold text-amber-500">${br.trophies} 🏆</span>
                            </div>
                        `;
                        container.appendChild(card);
                    });

                    document.getElementById('results').classList.remove('hidden');
                })
                .catch(err => {
                    document.getElementById('loading').classList.add('hidden');
                    const errBlock = document.getElementById('errorBlock');
                    errBlock.innerText = err.error || "Произошла непредвиденная ошибка запроса.";
                    errBlock.classList.remove('hidden');
                });
        });
    </script>
</body>
</html>
"""

# === API РОУТЕР ===
@app.route('/')
def index():
    return render_template_string(HTML_LAYOUT)

@app.route('/api/stats')
def get_stats():
    tag = request.args.get('tag', '').strip().upper().replace('#', '')
    if not tag:
        return jsonify({"error": "Тег игрока не указан"}), 400
        
    api_url = f"https://api.brawlstars.com/v1/players/%23{tag}"
    try:
        res = requests.get(api_url, headers=HEADERS, timeout=10)
        if res.status_code == 404:
            return jsonify({"error": "Игрок не найден. Проверьте правильность тега."}), 404
        elif res.status_code == 403:
            return jsonify({"error": "Ошибка авторизации API. Проверьте токен или IP-привязку в панели Supercell."}), 403
        elif res.status_code != 200:
            return jsonify({"error": f"Ошибка сервера Supercell (Код {res.status_code})"}), res.status_code
            
        return jsonify(res.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Не удалось связаться с API: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
