const $ = (sel) => document.querySelector(sel);
const api = {
	async getParts() {
		const r = await fetch('/api/parts');
		return r.json();
	},
	async createPart(data) {
		const r = await fetch('/api/parts', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
		if (!r.ok) throw new Error((await r.json()).detail || 'Error');
		return r.json();
	},
	async getComplexes() {
		const r = await fetch('/api/complexes');
		return r.json();
	},
	async createComplex(data) {
		const r = await fetch('/api/complexes', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
		if (!r.ok) throw new Error((await r.json()).detail || 'Error');
		return r.json();
	},
	async assignPartToComplex(complexId, body) {
		const r = await fetch(`/api/complexes/${complexId}/parts`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
		if (!r.ok) throw new Error((await r.json()).detail || 'Error');
		return r.json();
	},
	async count(selections) {
		const r = await fetch('/api/count', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ selections }) });
		if (!r.ok) throw new Error('Ошибка подсчёта');
		return r.json();
	}
};

function toast(msg, ok=true) {
	const t = $('#toast');
	t.textContent = msg;
	t.style.background = ok ? '#16a34a' : '#ef4444';
	t.hidden = false;
	setTimeout(() => t.hidden = true, 2000);
}

const state = {
	parts: [],
	complexes: [],
	selections: []
};

function renderSelects() {
	const complexSelect = $('#complexSelect');
	const assignComplex = $('#assignComplex');
	const assignPart = $('#assignPart');
	complexSelect.innerHTML = '';
	assignComplex.innerHTML = '';
	assignPart.innerHTML = '';

	state.complexes.forEach(c => {
		const o1 = document.createElement('option'); o1.value = c.id; o1.textContent = c.name; complexSelect.appendChild(o1);
		const o2 = document.createElement('option'); o2.value = c.id; o2.textContent = c.name; assignComplex.appendChild(o2);
	});
	state.parts.forEach(p => {
		const o = document.createElement('option'); o.value = p.id; o.textContent = p.name; assignPart.appendChild(o);
	});
}

function renderSelections() {
	const tbody = $('#selectionTable tbody');
	tbody.innerHTML = '';
	state.selections.forEach((sel, idx) => {
		const tr = document.createElement('tr');
		const complex = state.complexes.find(c => c.id === sel.complex_id);
		tr.innerHTML = `
			<td>${complex ? complex.name : sel.complex_id}</td>
			<td><input type="number" min="1" value="${sel.count}" data-idx="${idx}" class="selCount"/></td>
			<td><button class="danger delSel" data-idx="${idx}">×</button></td>
		`;
		tbody.appendChild(tr);
	});
}

function renderResult(items) {
	const tbody = $('#resultTable tbody');
	tbody.innerHTML = '';
	items.forEach(it => {
		const tr = document.createElement('tr');
		tr.innerHTML = `<td>${it.name}</td><td>${it.unit || ''}</td><td>${it.total_quantity}</td>`;
		tbody.appendChild(tr);
	});
}

async function loadData() {
	[state.parts, state.complexes] = await Promise.all([api.getParts(), api.getComplexes()]);
	renderSelects();
}

function bindEvents() {
	$('#addComplexBtn').addEventListener('click', () => {
		const id = parseInt($('#complexSelect').value, 10);
		const cnt = parseInt($('#complexCount').value, 10) || 1;
		state.selections.push({ complex_id: id, count: cnt });
		renderSelections();
	});
	$('#selectionTable').addEventListener('input', (e) => {
		if (e.target.classList.contains('selCount')) {
			const idx = parseInt(e.target.dataset.idx, 10);
			const val = Math.max(1, parseInt(e.target.value, 10) || 1);
			state.selections[idx].count = val;
		}
	});
	$('#selectionTable').addEventListener('click', (e) => {
		if (e.target.classList.contains('delSel')) {
			const idx = parseInt(e.target.dataset.idx, 10);
			state.selections.splice(idx, 1);
			renderSelections();
		}
	});
	$('#countBtn').addEventListener('click', async () => {
		try {
			const res = await api.count(state.selections);
			renderResult(res.items);
			toast('Готово');
		} catch (e) { toast(String(e.message || e), false); }
	});
	$('#addPartBtn').addEventListener('click', async () => {
		const name = ($('#partName').value || '').trim();
		const unit = ($('#partUnit').value || '').trim() || null;
		if (!name) return toast('Введите название детали', false);
		try {
			await api.createPart({ name, unit });
			$('#partName').value = '';
			$('#partUnit').value = '';
			state.parts = await api.getParts();
			renderSelects();
			toast('Деталь добавлена');
		} catch (e) { toast(String(e.message || e), false); }
	});
	$('#addComplexAdminBtn').addEventListener('click', async () => {
		const name = ($('#complexName').value || '').trim();
		const description = ($('#complexDesc').value || '').trim() || null;
		if (!name) return toast('Введите название комплекса', false);
		try {
			await api.createComplex({ name, description });
			$('#complexName').value = '';
			$('#complexDesc').value = '';
			state.complexes = await api.getComplexes();
			renderSelects();
			toast('Комплекс добавлен');
		} catch (e) { toast(String(e.message || e), false); }
	});
	$('#assignBtn').addEventListener('click', async () => {
		const complexId = parseInt($('#assignComplex').value, 10);
		const partId = parseInt($('#assignPart').value, 10);
		const qty = Math.max(0, parseInt($('#assignQty').value, 10) || 0);
		try {
			await api.assignPartToComplex(complexId, { part_id: partId, quantity: qty });
			state.complexes = await api.getComplexes();
			toast('Состав обновлён');
		} catch (e) { toast(String(e.message || e), false); }
	});
}

window.addEventListener('DOMContentLoaded', async () => {
	await loadData();
	renderSelections();
	bindEvents();
});