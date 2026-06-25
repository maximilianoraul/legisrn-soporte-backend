import { Controller } from '@hotwired/stimulus';

export default class extends Controller {
    static targets = ['host', 'statusResult', 'statusLoading', 'homeDirsRegion', 'loggedUsersRegion'];

    connect() {
        this.element.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.check();
            }
        });
    }

    async check() {
        const host = this.hostTarget.value.trim();
        if (!host) {
            this.statusResultTarget.innerHTML = '<p style="color:red">Ingrese una IP o nombre DNS</p>';
            return;
        }

        this.resetRegions();
        this.showLoading(this.statusLoadingTarget);

        try {
            const res = await fetch(`/api/host-status?host=${encodeURIComponent(host)}`);
            const data = await res.json();
            this.hideLoading(this.statusLoadingTarget);

            if (!res.ok) {
                this.statusResultTarget.innerHTML = `<p style="color:red">Error: ${data.error}</p>`;
                return;
            }

            this.statusResultTarget.innerHTML = this.renderStatusBar(data);

            if (data.ping && data.ssh) {
                this.showHomeDirs(host);
                this.showLoggedUsers(host);
            }

            this.statusResultTarget.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        } catch (err) {
            this.hideLoading(this.statusLoadingTarget);
            this.statusResultTarget.innerHTML = `<p style="color:red">Error de conexión: ${err.message}</p>`;
        }
    }

    async showHomeDirs(host) {
        this.showRegion(this.homeDirsRegionTarget);
        const resultTarget = this.homeDirsRegionTarget.querySelector('[data-target="result"]');
        const loadingTarget = this.homeDirsRegionTarget.querySelector('[data-target="loading"]');
        this.clearRegion(resultTarget);
        this.showLoading(loadingTarget);

        try {
            const res = await fetch(`/api/home-dirs?host=${encodeURIComponent(host)}`);
            const data = await res.json();
            this.hideLoading(loadingTarget);

            if (!res.ok) {
                resultTarget.innerHTML = `<p style="color:red">Error: ${data.error}</p>`;
                return;
            }

            if (data.directories && data.directories.length) {
                resultTarget.innerHTML = '<ul>' + data.directories.map(d => `<li>${d}</li>`).join('') + '</ul>';
            } else {
                resultTarget.innerHTML = '<p>No se encontraron directorios lrn*</p>';
            }
        } catch (err) {
            this.hideLoading(loadingTarget);
            resultTarget.innerHTML = `<p style="color:red">Error: ${err.message}</p>`;
        }
    }

    async showLoggedUsers(host) {
        this.showRegion(this.loggedUsersRegionTarget);
        const resultTarget = this.loggedUsersRegionTarget.querySelector('[data-target="result"]');
        const loadingTarget = this.loggedUsersRegionTarget.querySelector('[data-target="loading"]');
        this.clearRegion(resultTarget);
        this.showLoading(loadingTarget);

        try {
            const res = await fetch(`/api/logged-users?host=${encodeURIComponent(host)}`);
            const data = await res.json();
            this.hideLoading(loadingTarget);

            if (!res.ok) {
                resultTarget.innerHTML = `<p style="color:red">Error: ${data.error}</p>`;
                return;
            }

            if (data.sessions && data.sessions.length) {
                let html = '<table><tr><th>Usuario</th><th>TTY</th><th>Desde</th><th>Online</th></tr>';
                data.sessions.forEach(s => {
                    html += `<tr><td>${s.user}</td><td>${s.tty}</td><td>${s.since}</td><td>${s.online}</td></tr>`;
                });
                html += '</table>';
                resultTarget.innerHTML = html;
            } else {
                resultTarget.innerHTML = '<p>No hay usuarios conectados</p>';
            }
        } catch (err) {
            this.hideLoading(loadingTarget);
            resultTarget.innerHTML = `<p style="color:red">Error: ${err.message}</p>`;
        }
    }

    renderStatusBar(data) {
        const icon = (ok) => ok ? '✅' : '❌';
        return `<p>Ping: ${icon(data.ping)} &nbsp; SSH: ${icon(data.ssh)}</p>`;
    }

    resetRegions() {
        this.clearRegion(this.statusResultTarget);
        this.hideRegion(this.homeDirsRegionTarget);
        this.hideRegion(this.loggedUsersRegionTarget);
    }

    showRegion(el) { el.style.display = 'block'; }
    hideRegion(el) { el.style.display = 'none'; }
    clearRegion(el) { el.innerHTML = ''; }
    showLoading(el) { el.style.display = 'block'; }
    hideLoading(el) { el.style.display = 'none'; }
}
