const menuToggleBtn = document.querySelector('.navbar-toogleBtn');
const menuBars = document.querySelector('.hidden-nav');
const logoutNav = document.querySelector('.logout-nav');

menuToggleBtn.addEventListener('click', ()=>{
  menuBars.classList.toggle('active');
  logoutNav.classList.toggle('active');
})