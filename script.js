document.addEventListener('DOMContentLoaded', () => {
    // Set default date to today
    const dateInput = document.getElementById('attDate');
    dateInput.value = new Date().toISOString().split('T')[0];

    // Auth modal controls
    const modal = document.getElementById('authModal');
    const authBtnModal = document.getElementById('authBtnModal');
    const closeModal = document.getElementById('closeModal');
    const tabLogin = document.getElementById('tabLogin');
    const tabRegister = document.getElementById('tabRegister');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const logoutBtn = document.getElementById('logoutBtn');
    const welcomeUser = document.getElementById('welcomeUser');

    authBtnModal.onclick = () => modal.style.display = 'flex';
    closeModal.onclick = () => modal.style.display = 'none';

    tabLogin.onclick = () => {
        tabLogin.classList.add('active');
        tabRegister.classList.remove('active');
        loginForm.style.display = 'block';
        registerForm.style.display = 'none';
    };

    tabRegister.onclick = () => {
        tabRegister.classList.add('active');
        tabLogin.classList.remove('active');
        registerForm.style.display = 'block';
        loginForm.style.display = 'none';
    };

    // Check user session
    async function checkUser() {
        const res = await fetch('/api/current_user');
        const data = await res.json();
        if (data.logged_in) {
            welcomeUser.textContent = `Hello, ${data.user.name} (${data.user.roll_no})`;
            authBtnModal.style.display = 'none';
            logoutBtn.style.display = 'inline-block';
        } else {
            welcomeUser.textContent = `Welcome, Guest (Please login to mark attendance)`;
            authBtnModal.style.display = 'inline-block';
            logoutBtn.style.display = 'none';
        }
    }
    checkUser();

    // Register Handler
    registerForm.onsubmit = async (e) => {
        e.preventDefault();
        const payload = {
            name: document.getElementById('regName').value,
            roll_no: document.getElementById('regRoll').value,
            password: document.getElementById('regPassword').value
        };
        const res = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        alert(data.message);
        if (res.ok) tabLogin.click();
    };

    // Login Handler
    loginForm.onsubmit = async (e) => {
        e.preventDefault();
        const payload = {
            roll_no: document.getElementById('loginRoll').value,
            password: document.getElementById('loginPassword').value
        };
        const res = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (res.ok) {
            modal.style.display = 'none';
            checkUser();
        } else {
            alert(data.message);
        }
    };

    // Logout Handler
    logoutBtn.onclick = async () => {
        await fetch('/api/logout', { method: 'POST' });
        checkUser();
    };

    // Mark Attendance Handler
    document.getElementById('attendanceForm').onsubmit = async (e) => {
        e.preventDefault();
        const payload = {
            meal_date: document.getElementById('attDate').value,
            meal_type: document.getElementById('attMeal').value,
            status: document.getElementById('attStatus').value,
            special_opted: document.getElementById('attSpecial').value
        };

        const res = await fetch('/api/mark_attendance', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        alert(data.message);
    };

    // Kitchen Cook Prediction Handler
    let chartInstance = null;
    document.getElementById('predictionForm').onsubmit = async (e) => {
        e.preventDefault();
        const payload = {
            day_of_week: document.getElementById('dayOfWeek').value,
            meal_type: document.getElementById('mealType').value,
            special_item: document.getElementById('specialItem').value
        };

        const res = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();

        // Update counts
        document.getElementById('aiCount').textContent = data.ai_prediction;
        document.getElementById('eatingCount').textContent = data.confirmed_eating;
        document.getElementById('absentCount').textContent = data.confirmed_absent;
        document.getElementById('finalCount').textContent = data.final_requirement_headcount;

        // Update Raw Material
        document.getElementById('riceVal').textContent = `${data.food_plan.rice_kg} kg`;
        document.getElementById('dalVal').textContent = `${data.food_plan.dal_ltr} L`;
        document.getElementById('rotiVal').textContent = `${data.food_plan.roti_pcs} pcs`;
    };

    // Load Charts
    async function loadAnalytics() {
        const res = await fetch('/api/stats');
        const data = await res.json();
        const averages = [0, 0, 0];
        data.forEach(item => averages[item.meal_type] = Math.round(item.avg_students));

        const ctx = document.getElementById('trendChart').getContext('2d');
        if (chartInstance) chartInstance.destroy();

        chartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Breakfast', 'Lunch', 'Dinner'],
                datasets: [{
                    label: 'Historical Average Headcount',
                    data: averages,
                    backgroundColor: ['#38bdf8', '#818cf8', '#22c55e'],
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
                    x: { ticks: { color: '#94a3b8' }, grid: { display: false } }
                },
                plugins: { legend: { labels: { color: '#f8fafc' } } }
            }
        });
    }
    loadAnalytics();
});