const openNav = () => {
    document.getElementById("mobile-sidenav").classList.replace("w-0", "w-72");
};

const closeNav = () => {
    document.getElementById("mobile-sidenav").classList.replace("w-72", "w-0");
};

const togglePostForm = () => {
	const i = document.getElementById("submit-post-form");

	if (i.classList.contains("hidden")) {
		i.classList.replace("hidden", "block");
		document.getElementById("post-toggle-parent").remove();
	}
};

const quote = (pid) => {
	togglePostForm();
	const reply = document.getElementById("re-body");

	reply.value += `>>${pid} `;
};

const toggleFavorite = (board) => {

	let formData = new FormData();
	formData.append("board", `/${board}/`);

	let xhr = new XMLHttpRequest();
	xhr.responseType = "json";
	xhr.withCredentials = true;

	xhr.open("POST", "/toggle-favorite");
	xhr.send(formData);

	xhr.onload = () => {
		const h = document.getElementById("header-boardlist");
		const m = document.getElementById("mobile-boardlist");

		if (xhr.response.length > 0) {
			h.innerHTML = `[  ${xhr.response.map((b) => `<a href="${b}">${b}</a>`).join('  ')}  ]`;
		} else {
			h.innerHTML = '';
		}

		m.innerHTML = `
			${xhr.response.map((b) => `
				<li>
					<a href="${b}">${b}</a>
				</li>
			`).join(' ')}`;

		const btn = document.getElementById("toggle-fav");
		btn.classList.toggle('text-yellow-500');
		btn.classList.toggle('text-muted');
	};

	xhr.onerror = () => alert("Failed to save settings.");

};

document.addEventListener('click', e => {
    if (e.target.closest("#inner")) {
        closeNav();
    }
});
