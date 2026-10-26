const API = "";
let token = localStorage.getItem("token") || null;

const $ = (id) => document.getElementById(id);

async function api(path, body) {
    const res = await fetch(API + path, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error((await res.json()).detail || "Request failed");
    return res.json();
}

async function gql(query, variables = {}) {
    const res = await fetch("/graphql", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            ...(token ? {Authorization: `Bearer ${token}`} : {}),
        },
        body: JSON.stringify({query, variables}),
    });
    const json = await res.json();
    if (json.errors) throw new Error(json.errors.map((e) => e.message).join("; "));
    return json.data;
}

function showAdmin() {
    $("login-block").classList.add("hidden");
    $("admin-block").classList.remove("hidden");
}

function showLogin() {
    $("admin-block").classList.add("hidden");
    $("login-block").classList.remove("hidden");
}

async function loadClients() {
    const data = await gql(`{ clients { id clientId name isConfidential } }`);
    const body = $("clients-body");
    body.innerHTML = "";
    for (const c of data.clients) {
        const tr = document.createElement("tr");
        tr.innerHTML = `<td>${c.id}</td><td>${c.clientId}</td><td>${c.name}</td><td>${c.isConfidential}</td>`;
        body.appendChild(tr);
    }
}

$("login-btn").onclick = async () => {
    $("login-error").textContent = "";
    try {
        const data = await api("/auth/login", {
            email: $("email").value,
            password: $("password").value,
        });
        token = data.access_token;
        localStorage.setItem("token", token);
        showAdmin();
        await loadClients();
    } catch (e) {
        $("login-error").textContent = e.message;
    }
};

$("logout-btn").onclick = () => {
    token = null;
    localStorage.removeItem("token");
    showLogin();
};

$("create-client-btn").onclick = async () => {
    const name = $("client-name").value.trim();
    if (!name) return;
    try {
        await gql(`mutation($name: String!) { createClient(name: $name) { id clientId } }`, {name});
        $("client-name").value = "";
        await loadClients();
    } catch (e) {
        alert(e.message);
    }
};

if (token) {
    showAdmin();
    loadClients().catch(() => {
        token = null;
        localStorage.removeItem("token");
        showLogin();
    });
}