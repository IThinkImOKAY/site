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

document.addEventListener('click', e => {
    if (e.target.closest("#inner")) {
        closeNav();
    }
});
